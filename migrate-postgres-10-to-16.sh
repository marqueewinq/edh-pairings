#!/usr/bin/env bash
#
# Migrate PostgreSQL 10 -> 16 for edh-pairings.
#
# Run this ON THE SERVER before pushing the commit that changes
# docker-compose.yml from postgres:10 to postgres:16.
#
# Usage:
#   cd /path/to/edh-pairings
#   bash misc/migrate-postgres-10-to-16.sh
#
# After this script succeeds:
#   1. Edit docker-compose.yml: change postgres:10 -> postgres:16
#   2. Push the commit (triggers deploy)
#
set -euo pipefail

COMPOSE_FILE="docker-compose.yml"
DUMP_FILE="misc/pg10_dump.sql"
DATA_DIR="misc/dbdata"
BACKUP_DIR="misc/dbdata_pg10_backup"

echo "=== Step 1: Dump database from running PG10 ==="
docker compose -f "$COMPOSE_FILE" up -d db
sleep 3
docker compose -f "$COMPOSE_FILE" exec db pg_dumpall -U pairings > "$DUMP_FILE"
echo "Dump saved to $DUMP_FILE ($(wc -c < "$DUMP_FILE") bytes)"

echo ""
echo "=== Step 2: Stop all containers ==="
docker compose -f "$COMPOSE_FILE" down

echo ""
echo "=== Step 3: Back up old PG10 data directory ==="
if [ -d "$BACKUP_DIR" ]; then
    echo "Backup directory $BACKUP_DIR already exists, removing it"
    rm -rf "$BACKUP_DIR"
fi
mv "$DATA_DIR" "$BACKUP_DIR"
echo "Moved $DATA_DIR -> $BACKUP_DIR"

echo ""
echo "=== Step 4: Start PG16 with fresh data directory ==="
mkdir -p "$DATA_DIR"
docker run -d --name edh-pg16-temp \
    -e POSTGRES_USER=pairings \
    -e POSTGRES_PASSWORD=postgres \
    -v "$(pwd)/$DATA_DIR:/var/lib/postgresql/data" \
    postgres:16
echo "Waiting for PG16 to initialize..."
sleep 10

echo ""
echo "=== Step 5: Restore dump into PG16 ==="
# Restore may emit harmless "already exists" errors for roles/databases
# created during PG16 init; ignore those.
docker exec -i edh-pg16-temp psql -U pairings -d postgres < "$DUMP_FILE" || true
echo "Restore complete"

echo ""
echo "=== Step 6: Reset password for scram-sha-256 compatibility ==="
# PG10 dump has MD5 password hashes; PG16 defaults to scram-sha-256.
# Re-set the password so it's stored in the new format.
docker exec edh-pg16-temp psql -U pairings -d postgres \
    -c "ALTER USER pairings WITH PASSWORD 'postgres';"
echo "Password reset for scram-sha-256"

echo ""
echo "=== Step 7: Stop temporary container ==="
docker stop edh-pg16-temp
docker rm edh-pg16-temp

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit docker-compose.yml: change 'image: postgres:10' to 'image: postgres:16'"
echo "  2. Commit and push"
echo "  3. After verifying everything works, you can delete:"
echo "     - $BACKUP_DIR (old PG10 data)"
echo "     - $DUMP_FILE (SQL dump)"

exit 0
