# Connexion distante Codex après clonage d’un Mac

[English](../README.md) · [简体中文](../README.zh-CN.md)

Un clonage complet peut dupliquer installation_id, environment_id et server_id. Le symptôme peut être HTTP 409 `Remote app server already online`. Préservez la configuration du Mac d’origine et intervenez uniquement sur le clone.

La lecture seule est le mode par défaut. Les écritures sont limitées au build macOS 21828 étudié. Quittez complètement l’application et Codex CLI avant toute modification. clientId/keyId sont conservés ; les nouveaux identifiants serveur/environnement proviennent de l’inscription normale. Aucun changement de l’UUID système.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / Français

Codex connexion à distance impossible, clonage Mac, Assistant migration, identité appareil dupliquée, conflit inscription; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
