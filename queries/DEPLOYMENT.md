# Database Deployment

## How to apply changes

Run `create_all.sql` against the database:

```bash
psql -U postgres -d self_control_db -h localhost -p 5432 -f queries/create_all.sql
```

This is safe to run on an existing database:
- **Tables**: Uses `CREATE TABLE IF NOT EXISTS` — skips if already exist
- **Functions**: Uses `CREATE OR REPLACE FUNCTION` — always updates to latest version
- **Indexes**: Uses `CREATE INDEX IF NOT EXISTS` — skips if already exist
- **Seed data**: Uses `ON CONFLICT DO NOTHING` — skips if already exist
- **New columns**: Uses `ALTER TABLE ADD COLUMN IF NOT EXISTS` at the end of the file

## Adding new columns to existing tables

1. Add the column to the `CREATE TABLE` statement (for fresh databases)
2. Add an `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` at the end of the file (for existing databases)
3. Run `create_all.sql` as above

## Notes

- The two trigger statements (`event_trigger`, `peck_trigger`) will show ERROR if they already exist. This is harmless — triggers don't support `CREATE OR REPLACE` in PostgreSQL < 14.
- Always keep `checks.sql` and `results.sql` in sync with the functions in `create_all.sql`.
