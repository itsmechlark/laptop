#!/usr/bin/env python3
"""Run a trigger evaluation for a skill description using a REAL skill.

This is the replacement for the skill-creator harness (scripts/run_eval.py),
which measured triggering by dropping a *command* file into
`.claude/commands/<name>.md`. Command files are `/slash` commands: they are
never listed among the model-invocable skills and the `Skill` tool cannot call
them, so on Claude Code v2.1.236+ that harness produced a universal null result
(0 triggers across everything).

This helper measures an actual, model-invocable skill instead. It runs
`claude -p` from an empty temp project and watches the stream for the `Skill`
tool firing on the skill under test — on the streamed `tool_use` block, before
execution, which is the model's decision point.

By default it measures the skill *where it is already installed*: `skills/` is
`~/.claude/skills` via mac's symlink, so the shipped description is live, and
its adjacent siblings load and compete exactly as they would in real use. Only
`--description` installs a temporary probe skill, because a candidate rewrite
has nowhere else to live.

Do not reintroduce CLAUDE_CONFIG_DIR isolation here; see run_single_query.

Self-contained on purpose: it does NOT import from the external skill-creator
package, so the check no longer depends on a harness that has drifted out from
under it.

Output is the same JSON shape the old harness emitted, with two additions:
`mechanism` (so an artifact records how it was measured) and `stderr_log`.
"""

import argparse
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Return (name, description, full_content) for a SKILL.md.

    Inlined rather than imported from the skill-creator package: the whole point
    of this rewrite is to stop depending on that harness. Handles single-line
    descriptions and YAML block scalars (>, |, >-, |-), which is all the repo's
    SKILL.md files use.
    """
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{skill_path}/SKILL.md missing opening frontmatter ---")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError(f"{skill_path}/SKILL.md missing closing frontmatter ---")

    name = ""
    description = ""
    fm = lines[1:end_idx]
    i = 0
    while i < len(fm):
        line = fm[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                cont: list[str] = []
                i += 1
                while i < len(fm) and (fm[i].startswith("  ") or fm[i].startswith("\t")):
                    cont.append(fm[i].strip())
                    i += 1
                description = " ".join(cont)
                continue
            description = value.strip('"').strip("'")
        i += 1

    return name, description, content


def _write_temp_skill(root: Path, clean_name: str, description: str) -> Path:
    """Install a real project skill under <root>/.claude/skills/<clean_name>/.

    A YAML block scalar carries the description verbatim so quotes, colons, and
    newlines in it can never break the frontmatter.
    """
    skill_dir = root / ".claude" / "skills" / clean_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # An empty settings.json marks the folder as a project and is where a live
    # run would add `permissions`/trust settings if the folder-trust prompt
    # turns out to block headless invocation (see DESIGN.md, open questions).
    (root / ".claude" / "settings.json").write_text("{}\n")

    indented = "\n  ".join(description.split("\n"))
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {clean_name}\n"
        "description: |\n"
        f"  {indented}\n"
        "---\n\n"
        f"# {clean_name}\n\n"
        "Probe skill installed by run_eval_local.py to measure whether the "
        "description above causes autonomous invocation. Body intentionally "
        "inert.\n"
    )
    return skill_dir


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    extra_flags: list[str],
    stderr_log: str | None = None,
    model: str | None = None,
    use_probe: bool = False,
) -> bool:
    """Run one query and report whether the skill under test fired.

    Runs against the DEFAULT config dir. An earlier version pointed
    CLAUDE_CONFIG_DIR at a throwaway directory to keep the maintainer's
    installed skills from competing; that silently broke every run, because
    credential discovery is scoped to the config dir — `claude -p` under a fresh
    one exits "Not logged in · Please run /login" even with a valid keychain
    grant. Seeding the throwaway dir with the account state from ~/.claude.json
    is not enough, so the only way to keep it would be copying the live OAuth
    token into every temp dir, once per query. Not worth it.

    Letting the installed skills load is the better measurement anyway. `skills/`
    IS `~/.claude/skills` (mac symlinks it), so the skill under test is already
    live and model-invocable, and the eval sets deliberately share queries
    between adjacent skills — `git-commit`/`pull-request` and friends — to prove
    exactly one of the pair fires. Under isolation the sibling was not loaded to
    win the query, so every negative label passed for free.

    Default mode installs nothing and detects the real skill by name. Passing
    `use_probe` (which --description does) installs a probe carrying the
    candidate text, and detects only the probe, so a rewrite is measured against
    the incumbent description rather than in place of it.
    """
    project_root = Path(tempfile.mkdtemp(prefix="trigger-eval-"))

    try:
        if use_probe:
            target_name = f"{skill_name}-eval-{uuid.uuid4().hex[:8]}"
            _write_temp_skill(project_root, target_name, skill_description)
        else:
            # Neutral cwd: an empty project so the *repo's* CLAUDE.md and
            # settings cannot color the run. The skill itself comes from
            # ~/.claude/skills, already installed.
            target_name = skill_name
            (project_root / ".claude").mkdir(parents=True, exist_ok=True)
            (project_root / ".claude" / "settings.json").write_text("{}\n")

        # The `Read` fallback catches a skill discovered by reading its SKILL.md
        # when no partial stream arrives. It is only safe for a probe, whose
        # `<name>-eval-<uuid>` cannot appear unless the skill was found. A real
        # name can appear because the *query* said it — "review the codex-config
        # SKILL.md" makes the model read that path, which is the user's request
        # being answered, not the skill triggering. So watch Skill alone there.
        watched_tools = ("Skill", "Read") if use_probe else ("Skill",)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
            *extra_flags,
        ]
        if model:
            cmd.extend(["--model", model])

        # Drop CLAUDECODE so a nested `claude -p` is allowed; the guard only
        # protects interactive terminals, not programmatic subprocesses.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        # Surface stderr instead of discarding it. The old harness sent it to
        # /dev/null, which is exactly how a run where every `claude -p` errored
        # could masquerade as "0% triggers" — a description problem it was not.
        err_dst = open(stderr_log, "a") if stderr_log else subprocess.DEVNULL
        try:
            if stderr_log:
                err_dst.write(f"\n===== {target_name} :: {query[:80]!r} =====\n")
                err_dst.flush()

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=err_dst,
                cwd=str(project_root),
                env=env,
            )

            triggered = False
            start_time = time.time()
            buffer = ""
            pending_tool_name = None
            accumulated_json = ""

            try:
                while time.time() - start_time < timeout:
                    if process.poll() is not None:
                        remaining = process.stdout.read()
                        if remaining:
                            buffer += remaining.decode("utf-8", errors="replace")
                        break

                    ready, _, _ = select.select([process.stdout], [], [], 1.0)
                    if not ready:
                        continue

                    chunk = os.read(process.stdout.fileno(), 8192)
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="replace")

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        # Early detection from partial stream events: the model
                        # emits the tool_use block before the tool executes.
                        if event.get("type") == "stream_event":
                            se = event.get("event", {})
                            se_type = se.get("type", "")

                            if se_type == "content_block_start":
                                cb = se.get("content_block", {})
                                if cb.get("type") == "tool_use":
                                    tool_name = cb.get("name", "")
                                    if tool_name in watched_tools:
                                        pending_tool_name = tool_name
                                        accumulated_json = ""
                                    else:
                                        # An allowed non-Skill tool (Glob/Grep)
                                        # can precede the Skill call; ignore it
                                        # and keep watching rather than scoring a
                                        # false miss on the first tool. The run
                                        # ends as "not triggered" only at
                                        # message_stop/result below.
                                        pending_tool_name = None

                            elif se_type == "content_block_delta" and pending_tool_name:
                                delta = se.get("delta", {})
                                if delta.get("type") == "input_json_delta":
                                    accumulated_json += delta.get("partial_json", "")
                                    # Substring match on the whole input JSON
                                    # covers both Skill (`skill`: name) and Read
                                    # (`file_path`: .../<target_name>/SKILL.md).
                                    # Safe as a substring test: no skill name in
                                    # skills/ is a substring of another.
                                    if target_name in accumulated_json:
                                        return True

                            elif se_type in ("content_block_stop", "message_stop"):
                                if pending_tool_name:
                                    return target_name in accumulated_json
                                if se_type == "message_stop":
                                    return False

                        # Fallback: full assistant message (no partial stream).
                        elif event.get("type") == "assistant":
                            message = event.get("message", {})
                            for content_item in message.get("content", []):
                                if content_item.get("type") != "tool_use":
                                    continue
                                tool_name = content_item.get("name", "")
                                tool_input = content_item.get("input", {})
                                if tool_name == "Skill" and target_name in tool_input.get("skill", ""):
                                    triggered = True
                                elif "Read" in watched_tools and tool_name == "Read" \
                                        and target_name in tool_input.get("file_path", ""):
                                    triggered = True
                                return triggered

                        elif event.get("type") == "result":
                            return triggered
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()

            return triggered
        finally:
            if stderr_log and err_dst is not subprocess.DEVNULL:
                err_dst.close()
    finally:
        shutil.rmtree(project_root, ignore_errors=True)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    extra_flags: list[str],
    stderr_log: str | None,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    use_probe: bool = False,
) -> dict:
    """Run the full eval set and return results in the harness's JSON shape."""
    results = []

    # Threads, not processes: every worker does nothing but spawn `claude -p` and
    # parse its stream, so the GIL is released on the I/O anyway and a process
    # pool buys no parallelism. It also costs: ProcessPoolExecutor's
    # _check_system_limits() calls sysconf("SC_SEM_NSEMS_MAX"), which a seatbelt
    # sandbox denies, so constructing one raises PermissionError and the eval
    # cannot run from inside an agent session at all. run_single_query keeps no
    # shared state — its env dict, temp dirs, and probe name are all per-call.
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    extra_flags,
                    stderr_log,
                    model,
                    use_probe,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            query_triggers.setdefault(query, [])
            try:
                query_triggers[query].append(future.result())
            except Exception as e:  # noqa: BLE001 - surface, never swallow
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "mechanism": "probe-skill" if use_probe else "installed-skill",
        "stderr_log": stderr_log,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run a trigger eval against a real skill")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to the skill directory under test")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Per-query timeout (s)")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger-rate threshold")
    parser.add_argument("--model", default=None, help="Model for claude -p (default: user's configured model)")
    parser.add_argument("--stderr-log", default=None, help="File to append every claude -p stderr to")
    parser.add_argument(
        "--claude-flags",
        default="--disallowedTools|Bash Edit Write MultiEdit NotebookEdit Task",
        help="Pipe-separated extra flags passed to claude -p. Default forbids "
             "the doing-tools so the model must reach for a skill instead of "
             "executing the task directly (headless Claude otherwise just runs "
             "Bash and never invokes the Skill tool).",
    )
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description
    extra_flags = [f for f in args.claude_flags.split("|") if f != ""]

    if args.verbose:
        print(f"Evaluating (real skill): {description[:100]}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        extra_flags=extra_flags,
        stderr_log=args.stderr_log,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        # Only a description override needs a probe: the shipped text is already
        # live in ~/.claude/skills and can be measured where it sits.
        use_probe=args.description is not None,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
