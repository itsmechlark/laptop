# Grant OpenSSL configuration read access

**Context:** The Codex developer profile denies host access by default and
reopens only named runtime paths. Node.js reads
`/System/Library/OpenSSL/openssl.cnf` when crypto initializes, but that file is
not part of Codex's `:minimal` read set, so Node.js exited before running tests.

**Decision:** Grant the Codex developer profile read access only to
`/System/Library/OpenSSL/openssl.cnf`.

**Consequences:** Node.js crypto works inside Codex without making the host or
all of `/System/Library` readable. The profile carries a macOS-specific runtime
exception that needs revalidation when Node.js or Codex's `:minimal` paths
change.

**Rejected:** Reading the whole host or `/System/Library` would widen the
sandbox beyond the one immutable file Node.js needs. Setting
`OPENSSL_CONF=/dev/null` avoids the read failure but also discards the operating
system's OpenSSL configuration.
