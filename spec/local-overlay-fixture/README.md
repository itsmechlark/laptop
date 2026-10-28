# local-overlay-fixture

This directory is a placeholder. The local overlay detection is self-tested
inline in `scripts/check-payload` with a temporary symlink (not a directory
fixture), because `is_local_skill` is path-based and cannot be exercised
against a root other than `skills/` without a temp link.

The self-test block is labelled "local overlay detection self-test" in
`check-payload`.
