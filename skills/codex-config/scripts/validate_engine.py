#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None


Replacement = tuple[str, str]


class TomlLoadError(Exception):
    pass


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequirementsStackResult:
    validation: ValidationResult
    managed_proxy: bool


def parse_replacements(assignments: Iterable[str]) -> tuple[Replacement, ...]:
    return tuple(assignment.split("=", 1) for assignment in assignments)


def render(text: str, replacements: Sequence[Replacement]) -> str:
    for token, value in replacements:
        text = text.replace(token, value)
    return text


def load_toml(
    path: pathlib.Path,
    replacements: Sequence[Replacement] = (),
) -> dict[str, Any]:
    if tomllib is None:
        raise TomlLoadError(
            "python3 must provide tomllib (Python 3.11+) or the tomli package"
        )

    try:
        return tomllib.loads(render(path.read_text(), replacements))
    except Exception as exc:
        raise TomlLoadError(f"{path}: TOML parse error: {exc}") from exc


def walk_keys(value: Any, prefix: tuple[str, ...] = ()) -> Iterable[tuple[str, ...]]:
    if isinstance(value, dict):
        for key, child in value.items():
            current = prefix + (str(key),)
            yield current
            yield from walk_keys(child, current)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_keys(child, prefix + (f"[{index}]",))


def has_glob(text: str) -> bool:
    return any(character in text for character in "*?[{")


def is_simple_trailing_subtree(text: str) -> bool:
    if not text.endswith("/**"):
        return False
    prefix = text[:-3]
    return bool(prefix) and not has_glob(prefix)


def check_filesystem_table(
    table: dict[str, Any],
    where: tuple[str, ...],
) -> list[str]:
    issues = []
    for key, value in table.items():
        key = str(key)
        if isinstance(value, dict):
            issues.extend(check_filesystem_table(value, where + (key,)))
            continue
        if value not in {"read", "write", "deny"}:
            continue
        if value in {"read", "write"} and has_glob(key) and not is_simple_trailing_subtree(key):
            issues.append(
                f"{'.'.join(where)}: {key!r} = {value!r} uses an arbitrary glob. "
                "Use an exact path or a simple trailing '/**' subtree for read/write; "
                "reserve arbitrary globs for deny."
            )
        if ".." in pathlib.PurePosixPath(key).parts:
            issues.append(f"{'.'.join(where)}: {key!r} contains parent traversal '..'.")
    return issues


def collect_recursive_deny_globs(table: dict[str, Any]) -> list[str]:
    found = []
    for key, value in table.items():
        if isinstance(value, dict):
            found.extend(collect_recursive_deny_globs(value))
        elif value == "deny" and "**" in str(key):
            found.append(str(key))
    return found


def validate_config(
    path: pathlib.Path,
    *,
    managed_proxy: bool,
    cli_sandbox: str,
    replacements: Sequence[Replacement],
) -> ValidationResult:
    data = load_toml(path, replacements)
    issues = []
    warnings = []

    permissions = data.get("permissions")
    profiles_present = isinstance(permissions, dict) and bool(permissions)
    permission_model_present = profiles_present or "default_permissions" in data
    legacy_hits = [
        ".".join(key_path)
        for key_path in walk_keys(data)
        if key_path[-1] in {"sandbox_mode", "sandbox_workspace_write"}
    ]

    if permission_model_present and legacy_hits:
        issues.append(
            "permission profiles are mixed with legacy sandbox configuration: "
            + ", ".join(sorted(set(legacy_hits)))
        )

    if permission_model_present and cli_sandbox:
        issues.append(
            "permission profiles are mixed with CLI --sandbox "
            f"override {cli_sandbox!r}"
        )

    features = data.get("features") if isinstance(data.get("features"), dict) else {}
    proxy_enabled = features.get("network_proxy") is True

    if profiles_present:
        for profile_name, profile in permissions.items():
            if not isinstance(profile, dict):
                continue

            filesystem = profile.get("filesystem")
            if isinstance(filesystem, dict):
                issues.extend(
                    check_filesystem_table(
                        filesystem,
                        ("permissions", str(profile_name), "filesystem"),
                    )
                )
                scan_depth = filesystem.get("glob_scan_max_depth")
                recursive_denies = collect_recursive_deny_globs(filesystem)
                if recursive_denies and not isinstance(scan_depth, int):
                    warnings.append(
                        f"permissions.{profile_name}.filesystem has unbounded '**' deny globs "
                        "but no glob_scan_max_depth; this may require bounded expansion on "
                        "Linux, WSL, or native Windows"
                    )
                elif isinstance(scan_depth, int) and scan_depth < 1:
                    issues.append(
                        f"permissions.{profile_name}.filesystem.glob_scan_max_depth must be >= 1"
                    )

            network = profile.get("network")
            if not isinstance(network, dict):
                continue

            domains = network.get("domains")
            if network.get("enabled") is True and isinstance(domains, dict) and domains:
                if not proxy_enabled and not managed_proxy:
                    issues.append(
                        f"permissions.{profile_name}.network defines domain policy with "
                        "network.enabled=true but features.network_proxy is not true. "
                        "Domain rules do not constrain direct subprocess networking without "
                        "an active proxy. Use --managed-proxy only when administrator-managed "
                        "requirements activate it."
                    )

            sockets = network.get("unix_sockets")
            if isinstance(sockets, dict):
                for socket_path, decision in sockets.items():
                    text = str(socket_path)
                    if decision == "allow" and not pathlib.PurePosixPath(text).is_absolute():
                        issues.append(
                            f"permissions.{profile_name}.network.unix_sockets: allowed "
                            f"socket {text!r} is not absolute after known placeholder expansion"
                        )

    return ValidationResult(tuple(issues), tuple(warnings))


def validate_requirements(path: pathlib.Path) -> ValidationResult:
    data = load_toml(path)
    issues = []
    rules = data.get("rules")
    prefix_rules = rules.get("prefix_rules") if isinstance(rules, dict) else None
    if isinstance(prefix_rules, list):
        for index, rule in enumerate(prefix_rules):
            decision = rule.get("decision") if isinstance(rule, dict) else None
            if decision not in {"prompt", "forbidden"}:
                issues.append(
                    f"rules.prefix_rules[{index}].decision must be prompt or forbidden"
                )
                break
    return ValidationResult(tuple(issues))


def validate_requirements_stack(
    config_paths: Sequence[pathlib.Path],
    requirements_paths: Sequence[pathlib.Path],
    *,
    cli_sandbox: str,
    replacements: Sequence[Replacement],
) -> RequirementsStackResult:
    allowed_profiles: dict[str, Any] = {}
    default_permissions: Any = None
    network: dict[str, Any] = {}
    config_profiles = set()
    requirements_profiles = set()
    managed_permission_model_present = False

    for kind, paths in (("config", config_paths), ("requirements", requirements_paths)):
        for path in paths:
            data = load_toml(path, replacements if kind == "config" else ())
            profiles = data.get("permissions")
            if isinstance(profiles, dict):
                names = {
                    str(name)
                    for name, profile in profiles.items()
                    if isinstance(profile, dict) and name != "filesystem"
                }
                if kind == "config":
                    config_profiles.update(names)
                else:
                    requirements_profiles.update(names)

            if kind != "requirements":
                continue

            incoming_profiles = data.get("allowed_permission_profiles")
            if isinstance(incoming_profiles, dict):
                managed_permission_model_present = True
                allowed_profiles.update(incoming_profiles)

            if "default_permissions" in data:
                managed_permission_model_present = True
                default_permissions = data.get("default_permissions")

            incoming_network = data.get("experimental_network")
            if isinstance(incoming_network, dict):
                for key, value in incoming_network.items():
                    if key == "domains" and isinstance(value, dict):
                        domains = network.get("domains")
                        if not isinstance(domains, dict):
                            domains = {}
                        domains.update(value)
                        network["domains"] = domains
                    else:
                        network[key] = value

    issues = []
    profile_conflicts = sorted(config_profiles & requirements_profiles)
    if profile_conflicts:
        issues.append(
            f"requirements permission profile {profile_conflicts[0]!r} conflicts "
            "with a config-defined profile"
        )

    built_in_profiles = {":read-only", ":workspace", ":danger-full-access"}
    defined_profiles = built_in_profiles | config_profiles | requirements_profiles
    undefined_profiles = sorted(set(allowed_profiles) - defined_profiles)
    if undefined_profiles:
        issues.append(
            "allowed_permission_profiles refers to undefined profile "
            f"{undefined_profiles[0]!r}"
        )

    has_domain_policy = any(
        network.get(key) for key in ("domains", "allowed_domains", "denied_domains")
    )
    managed_proxy = network.get("enabled") is True
    if has_domain_policy and not managed_proxy:
        issues.append("experimental_network defines domain policy but enabled is not true")

    if (
        isinstance(default_permissions, str)
        and allowed_profiles.get(default_permissions) is not True
    ):
        issues.append(
            f"default_permissions {default_permissions!r} is not enabled by "
            "allowed_permission_profiles"
        )

    if cli_sandbox and managed_permission_model_present:
        issues.append(
            "permission profiles are mixed with CLI --sandbox "
            f"override {cli_sandbox!r}"
        )

    return RequirementsStackResult(ValidationResult(tuple(issues)), managed_proxy)


def validate_config_stack(
    config_paths: Sequence[pathlib.Path],
    requirements_paths: Sequence[pathlib.Path],
    *,
    replacements: Sequence[Replacement],
) -> ValidationResult:
    profile_files = []
    legacy_files = []

    for kind, paths in (("config", config_paths), ("requirements", requirements_paths)):
        for path in paths:
            data = load_toml(path, replacements if kind == "config" else ())
            profiles_present = "default_permissions" in data or data.get("permissions")
            if kind == "requirements":
                profiles_present = profiles_present or bool(
                    data.get("allowed_permission_profiles")
                )
            if profiles_present:
                profile_files.append(str(path))
            if "sandbox_mode" in data or "sandbox_workspace_write" in data:
                legacy_files.append(str(path))

    issues = []
    if profile_files and legacy_files:
        issues.append(
            "effective configuration mixes permission profiles with legacy sandbox "
            f"settings across files: profiles={profile_files}, legacy={legacy_files}"
        )
    return ValidationResult(tuple(issues))


def render_file(
    source: pathlib.Path,
    destination: pathlib.Path,
    replacements: Sequence[Replacement],
) -> None:
    destination.write_text(render(source.read_text(), replacements))


def add_common_stack_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", action="append", default=[])
    parser.add_argument("--requirements", action="append", default=[])
    parser.add_argument("--replace", action="append", default=[])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex configuration validation engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config = subparsers.add_parser("config")
    config.add_argument("--file", required=True)
    config.add_argument("--managed-proxy", action="store_true")
    config.add_argument("--sandbox", default="")
    config.add_argument("--replace", action="append", default=[])

    requirements = subparsers.add_parser("requirements")
    requirements.add_argument("--file", required=True)

    effective_requirements = subparsers.add_parser("effective-requirements")
    add_common_stack_arguments(effective_requirements)
    effective_requirements.add_argument("--sandbox", default="")

    effective_config = subparsers.add_parser("effective-config")
    add_common_stack_arguments(effective_config)

    render_parser = subparsers.add_parser("render")
    render_parser.add_argument("--source", required=True)
    render_parser.add_argument("--destination", required=True)
    render_parser.add_argument("--replace", action="append", default=[])

    return parser


def print_result(result: ValidationResult, *, prefix_errors: bool = False) -> int:
    for warning in result.warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    for issue in result.issues:
        prefix = "ERROR: " if prefix_errors else ""
        print(f"{prefix}{issue}", file=sys.stderr)
    return 1 if result.issues else 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "config":
            result = validate_config(
                pathlib.Path(args.file),
                managed_proxy=args.managed_proxy,
                cli_sandbox=args.sandbox,
                replacements=parse_replacements(args.replace),
            )
            status = print_result(result, prefix_errors=True)
            if not status:
                print(f"static invariants: {args.file}")
            return status

        if args.command == "requirements":
            result = validate_requirements(pathlib.Path(args.file))
            status = print_result(result)
            if not status:
                print(f"requirements invariants: {args.file}")
            return status

        if args.command == "effective-requirements":
            stack = validate_requirements_stack(
                tuple(map(pathlib.Path, args.config)),
                tuple(map(pathlib.Path, args.requirements)),
                cli_sandbox=args.sandbox,
                replacements=parse_replacements(args.replace),
            )
            status = print_result(stack.validation)
            if not status:
                print(f"managed_proxy={'true' if stack.managed_proxy else 'false'}")
                print("effective requirements invariants")
            return status

        if args.command == "effective-config":
            result = validate_config_stack(
                tuple(map(pathlib.Path, args.config)),
                tuple(map(pathlib.Path, args.requirements)),
                replacements=parse_replacements(args.replace),
            )
            status = print_result(result)
            if not status:
                print("effective configuration invariants")
            return status

        if args.command == "render":
            render_file(
                pathlib.Path(args.source),
                pathlib.Path(args.destination),
                parse_replacements(args.replace),
            )
            return 0
    except TomlLoadError as exc:
        print(exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"filesystem error: {exc}", file=sys.stderr)
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
