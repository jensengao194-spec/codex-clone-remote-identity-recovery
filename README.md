# Codex remote connection recovery after Mac cloning

**Duplicate installation ID / environment ID / server ID · HTTP 409 `Remote app server already online`**

[简体中文](README.zh-CN.md) · [日本語](docs/ja.md) · [한국어](docs/ko.md) · [Deutsch](docs/de.md) · [Français](docs/fr.md) · [Español](docs/es.md) · [Português](docs/pt.md) · [Русский](docs/ru.md)

A documented case and a scoped local recovery script for the Codex desktop app after cloning a Mac to another Mac. Preserve the original computer; rebuild the clone's host registration through the application's normal registration flow.

This is an independent troubleshooting project, not an official OpenAI repair tool. The write path is restricted to **macOS desktop build 21828, app version 26.1021.31345**. Other versions require a fresh implementation audit. No Windows/Linux reset support is claimed.

## Symptoms and diagnosis

After a full computer clone, both Codex installations may share `~/.codex/installation_id`, `electron-local-remote-control-installation-id`, `electron-local-remote-control-environment-id`, and the SQLite host `server_id`. The backend can reject the second host with `409 Conflict: Remote app server already online`. Remote device lists may also hide another host whose installation identity matches the local host.

Compare both computers **read only**. In the observed case the installation/environment/server IDs matched, while client enrollment `clientId` and `keyId` were already different. Same-account `accountUserId` and `account_id` matching is normal. This is evidence of duplicate host registration, not proof that every connection failure has the same cause.

## Why editing three JSON fields is insufficient

| State | Role | Recovery treatment |
|---|---|---|
| `installation_id` file | CLI installation UUID; also used outside remote control | Move aside on the clone; let the app generate a new ID |
| Two `electron-local-remote-control-*` JSON keys | Desktop caches of host identity | Remove only these keys in JSON and its `.bak` |
| `state_5.sqlite` → `remote_control_enrollments` | Persistent server/environment enrollment | Delete exactly one matching clone host row |
| `electron-remote-control-client-enrollments` | Controller enrollment and device public-key metadata | Preserve, including `clientId` and `keyId` |

The installation ID is shared with the CLI; changing it also changes the CLI's installation association. This is not a remote-only configuration key. Sessions, projects, model settings, automation IDs, account credentials and system UUID are not reset. The script makes no network requests and never revokes the original host or controller.

## Inspect, review, exit, apply

Python 3.9+ and macOS are required; no third-party packages are needed. Use the script **only on the clone**. Keep the recovery folder local and outside Git.

```sh
python3 codex_clone_identity.py --plan-out clone-plan.local.json
```

This is read only apart from writing the requested local plan. Review that plan against the two-machine comparison. It includes private identifiers and paths: do not upload it. `CODEX_HOME` is honored; use `--home /absolute/path/to/.codex` if needed. Multiple accounts require `--account-id ACCOUNT_ID`; ambiguous or inconsistent state is refused.

Then, from an **external Terminal**, run:

```sh
python3 codex_clone_identity.py --plan clone-plan.local.json --apply --wait-for-exit
```

Quit Codex completely, including other Codex CLI/app-server processes. Closing a window is not sufficient. The script waits up to 30 minutes and requires about 10 seconds without detected processes. It does not quit or kill processes. Ctrl-C cancels. Without `--wait-for-exit`, a running app causes refusal. Do not relaunch the app while a reset is in progress.

After backups and the local reset finish, reopen Codex and enable remote connections in settings. The application generates the installation UUID; the backend assigns the new server/environment IDs. Do not invent IDs or alter the system UUID. No automatic application restart is performed.

## Scope and safeguards

- The reviewed plan must still match the installation, environment, server and account selection. App build changes are refused.
- JSON and `.bak` must be valid and agree with the source identity; symlinked target files are refused.
- A private exit-time backup includes an SQLite backup-API snapshot, original JSON, installation ID, and existing config/auth files. **These backups contain private data; never publish them.**
- SQLite changes use an exclusive transaction and require exactly one matched row. Other host rows and other table content are verified unchanged inside the transaction.
- JSON writes are atomic per file and preserve every non-target value, including controller enrollments. Ordinary exceptions roll back the database and restore changed files.
- Files and SQLite do not form one crash-atomic transaction. Power loss or forced termination can leave partial state; retain the backup and inspect before retrying. Process checks reduce concurrent-write risk but do not prevent another program from starting at the wrong moment. The tool assumes all writers have stopped.

## Validation and limits

An actual clone-side local reset completed on the inspected build. After restarting, new installation and environment IDs were observed. The original machine was reported unchanged by its owner. **Simultaneous connectivity of both machines has not been independently verified**, so this repository does not claim the issue is fully resolved.

Synthetic tests cover scoped deletion, preservation of unrelated data and client enrollments, stale-plan refusal and rollback after an injected file-write failure. They are not device-key hardware tests or an end-to-end backend enrollment test.

```sh
python3 -m unittest discover -s tests -v
python3 codex_clone_identity.py --help
```

## Recovery if something fails

Keep `recovery-local/result.json` and exit-time backups. The result status `local_reset_complete_registration_pending` describes local preparation only. Do not delete `.codex`, SQLite WAL/SHM files, existing server registrations, or Secure Enclave keys. For rollback, quit all writers and restore only the intended fields/file/row from the exit-time backup after checking for new work; whole-database rollback can lose newer history. No automatic restore command is supplied. Restoring the cloned identity reintroduces the original conflict.

If controller-specific key-missing/revocation errors remain, investigate them separately; this tool deliberately does not clear client enrollments.

## Evidence and implementation references

[Case report](docs/CASE-STUDY.md) separates observed runtime evidence, static analysis and unknowns. The inspected CLI was `0.164.0-alpha.11.1`; its binary contained commit `6905ecede7816e91373e9eabda3f6b0368fc747b`. Relevant OpenAI source at that revision:

- [Installation ID resolution](https://github.com/openai/codex/blob/6905ecede7816e91373e9eabda3f6b0368fc747b/codex-rs/core/src/installation_id.rs)
- [Host enrollment persistence](https://github.com/openai/codex/blob/6905ecede7816e91373e9eabda3f6b0368fc747b/codex-rs/app-server-transport/src/transport/remote_control/enroll.rs)
- [Server registration API](https://github.com/openai/codex/blob/6905ecede7816e91373e9eabda3f6b0368fc747b/codex-rs/app-server-transport/src/transport/remote_control/server_api.rs)

## Search phrases

Codex cloned Mac remote connection not working; Mac migration duplicate device identity; Migration Assistant Codex remote registration conflict; Codex HTTP 409 Remote app server already online; duplicate installation_id environment_id server_id; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments.

See the language pages for translated search phrases. Public text, filenames and repository topics help discovery; search engine indexing and ranking are not guaranteed.
