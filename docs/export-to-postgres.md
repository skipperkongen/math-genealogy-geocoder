# Exporting the database to PostgreSQL/PostGIS

```
sqlite3 genealogy.db .dump > dump.sql
psql -d <DATABASENAME> -U <USERNAME> -W < dump.sql
```
