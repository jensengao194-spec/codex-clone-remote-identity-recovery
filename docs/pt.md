# Conexão remota do Codex após clonar um Mac

[English](../README.md) · [简体中文](../README.zh-CN.md)

Uma clonagem completa pode duplicar installation_id, environment_id e server_id. Um sintoma possível é HTTP 409 `Remote app server already online`. Preserve a configuração do computador original e altere apenas o clone.

O modo padrão é somente leitura. As gravações ficam restritas ao build macOS 21828 analisado. Encerre completamente o aplicativo e o Codex CLI antes de aplicar alterações. clientId/keyId são preservados; novos IDs de servidor e ambiente vêm do registro normal. O UUID do sistema não é alterado.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / Português

Codex conexão remota não funciona, clonagem Mac, Assistente de Migração, identidade de dispositivo duplicada, conflito de registro; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
