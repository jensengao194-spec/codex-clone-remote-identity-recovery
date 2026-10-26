# Удалённое подключение Codex после клонирования Mac

[English](../README.md) · [简体中文](../README.zh-CN.md)

Полное клонирование Mac может дублировать installation_id, environment_id и server_id. Возможный симптом: HTTP 409 `Remote app server already online`. Сохраните настройки исходного компьютера и работайте только с клоном.

По умолчанию выполняется только чтение. Запись ограничена исследованной сборкой macOS 21828. Перед применением полностью закройте приложение и Codex CLI. clientId/keyId сохраняются; новые ID среды и сервера выдаются при обычной регистрации. Системный UUID не изменяется.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / Русский

Codex удалённое подключение не работает, клонирование Mac, Ассистент миграции, дубликат идентификатора устройства, конфликт регистрации; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
