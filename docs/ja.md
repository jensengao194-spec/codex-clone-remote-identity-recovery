# Mac のクローン後に Codex のリモート接続ができない

[English](../README.md) · [简体中文](../README.zh-CN.md)

Mac を複製した後、installation_id・environment_id・server_id が重複し、HTTP 409 `Remote app server already online` が発生する場合があります。元のコンピューターの設定を保持し、複製先だけを調査してください。

既定は読み取り専用です。書き込みは調査済みの macOS build 21828 に限定されます。適用前にアプリと Codex CLI を完全に終了します。clientId/keyId は保持し、環境・サーバー ID はサービスに再登録させます。システム UUID を変更しません。

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / 日本語

Codex リモート接続できない、Mac クローン、移行アシスタント、端末 ID 重複、リモート登録競合; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
