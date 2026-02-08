================================================================================
                    SERVER MIGRATION SCRIPTS
================================================================================

Location: /shared/migration-scripts/

All migration scripts and documentation are here.

QUICK START:
  Read: START-HERE.md

SCRIPTS:
  - full-server-backup.sh           Complete server backup
  - full-server-restore.sh          Complete server restore
  - openclaw-backup.sh              OpenClaw only backup
  - openclaw-restore.sh             OpenClaw only restore
  - openclaw-transfer-to-new-server.sh  Automated transfer
  - test-migration-readiness.sh     Check readiness
  - verify-server-migration.sh      Verify full migration
  - openclaw-verify.sh              Verify OpenClaw

DOCUMENTATION:
  - START-HERE.md                   Quick start guide
  - FULL-SERVER-MIGRATION-GUIDE.md  Complete guide
  - QUICK-START-MIGRATION.md        Quick reference
  - MIGRATION-README.md             Overview

To use from anywhere:
  cd /shared/migration-scripts
  ./full-server-backup.sh

Or create symlinks in /root:
  ln -s /shared/migration-scripts/*.sh /root/

================================================================================
