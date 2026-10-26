# Anonymized case report / 匿名问题汇总

Date: 2026-10-26 (Asia/Shanghai). Platform: macOS. Desktop: 26.1021.31345 (21828). CLI: 0.164.0-alpha.11.1. The app bundle was named ChatGPT.app, with bundle identifier com.openai.codex.

## Evidence ladder

| Evidence | Result | Limit |
|---|---|---|
| Owner's read-only comparison on the original machine | installation/file/environment/server IDs identical to clone; client/key IDs different | Original was not inspected directly by this project's authoring agent |
| Clone's existing runtime logs | HTTP 409 Remote app server already online for persisted server/environment | Confirms collision symptom; does not exclude other causes |
| Clone's controller logs | Device-key creation, successful challenge signing and enrollment completion | Historical success does not prove indefinite key availability |
| Packaged desktop JS, targeted static inspection | app-server notification → JSON cache; local identity filters remote host list; client public-key validation | Not a complete audit of the application |
| SQLite read-only inspection | matching host row in remote_control_enrollments | Local persisted state, not a live backend inventory |
| Revision-specific upstream CLI source | UUID file generation; host enrollment load/save; server-assigned IDs | Matched by revision string found in binary; no native disassembly |
| Actual exit-time reset | exactly one host row removed; client enrollments and other table content preserved | Local reset only |
| Read-only post-restart inspection | new installation and environment IDs observed | Two-machine simultaneous connectivity not independently tested |

## Sequence

1. Read-only inventory and private backups; no system UUID changes.
2. Identify the source installation_id file and SQLite host enrollment in addition to JSON caches.
3. Compare original and clone; distinguish host identity from controller identity.
4. Prepare and test a targeted reset with rollback on ordinary exceptions.
5. Run from an external terminal only after app/CLI exit; take a fresh consistent SQLite backup.
6. Let the app generate the installation ID and obtain service-assigned registration.
7. Leave original device registrations and both computers' controller keys intact.

## What would establish full recovery?

Different installation/server/environment IDs on both machines; consistent JSON/file/database state on each; both hosts visible and reachable simultaneously; no persistent already-online errors; unchanged original configuration. That end-to-end test is still outstanding.

## Privacy

No real installation UUIDs, server/environment/client/key IDs, account identifiers, email addresses, private paths, raw logs, configurations, authentication files, database snapshots or public-key blobs are included. Examples are generic. Runtime plans/backups must stay local.
