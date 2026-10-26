# Mac 복제 후 Codex 원격 연결 실패

[English](../README.md) · [简体中文](../README.zh-CN.md)

Mac 전체 복제 후 installation_id, environment_id, server_id가 중복되어 HTTP 409 `Remote app server already online` 오류가 발생할 수 있습니다. 원본 컴퓨터 설정은 유지하고 복제한 컴퓨터만 점검합니다.

기본 동작은 읽기 전용이며 쓰기는 분석한 macOS build 21828에 한정됩니다. 적용 전에 앱과 Codex CLI를 완전히 종료하세요. clientId/keyId는 보존하며 새 환경 및 서버 ID는 정상 등록을 통해 받습니다. 시스템 UUID를 변경하지 않습니다.

[Instructions, backup/rollback limits and validation status](../README.md#inspect-review-exit-apply) · [Case report](CASE-STUDY.md)

## Search / 한국어

Codex 원격 연결 안됨, Mac 복제, 마이그레이션 지원, 장치 식별자 중복, 원격 등록 충돌; electron-local-remote-control-installation-id; electron-local-remote-control-environment-id; electron-remote-control-client-enrollments; installation_id; environment_id; server_id.
