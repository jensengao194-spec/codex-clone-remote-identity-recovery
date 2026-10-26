# Conexión remota de Codex después de clonar un Mac

[English](../README.md) · [简体中文](../README.zh-CN.md)

Una clonación completa puede duplicar installation_id, environment_id y server_id. Un síntoma posible es HTTP 409 `Remote app server already online`. Conserve la configuración del equipo original y actúe solo en el clon.

El modo predeterminado es de solo lectura. Las escrituras se limitan al build de macOS 21828 analizado. Cierre por completo la aplicación y Codex CLI antes de aplicar cambios. Se conservan clientId/keyId; los nuevos identificadores de servidor y entorno se obtienen mediante el registro normal. No se cambia el UUID del sistema.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / Español

Codex conexión remota no funciona, clonar Mac, Asistente de Migración, identidad de dispositivo duplicada, conflicto de registro; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
