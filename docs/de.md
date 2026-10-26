# Codex-Remote-Verbindung nach dem Klonen eines Macs reparieren

[English](../README.md) · [简体中文](../README.zh-CN.md)

Nach einem vollständigen Mac-Klon können installation_id, environment_id und server_id doppelt vorhanden sein. Ein mögliches Symptom ist HTTP 409 `Remote app server already online`. Die Konfiguration des ursprünglichen Computers bleibt erhalten.

Standardmäßig wird nur gelesen. Schreibzugriffe sind auf den untersuchten macOS-Build 21828 beschränkt. App und Codex CLI vor der Anwendung vollständig beenden. clientId/keyId bleiben erhalten; neue Server- und Umgebungs-IDs kommen aus der regulären Registrierung. Die System-UUID wird nicht geändert.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / Deutsch

Codex Fernverbindung funktioniert nicht, Mac klonen, Migrationsassistent, doppelte Geräteidentität, Registrierungskonflikt; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
