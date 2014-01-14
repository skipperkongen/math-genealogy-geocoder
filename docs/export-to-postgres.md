# Export SQLite database to PostgreSQL

1) Create SQLite dump file, and import into PostgreSQL:

```
sqlite3 genealogy.db .dump > dump.sql
psql -d <DATABASENAME> -U <USERNAME> -W < dump.sql
```

2) Change representation of geographical locations. In the plain SQLIte database, geographical points are represented with an *x* and *y* column (should properly be called long and lat).
You can replace these columns with a proper GEOMETRY column in PostgreSQL:
 
```sql
-- Add PostGIS extension if not already installed
create extension postgis;

-- Add GEOMETRY column
ALTER TABLE school_location ADD COLUMN wkb_geometry GEOMETRY;

-- Update GEOMETRY column with point values
UPDATE school_location
SET wkb_geometry = ST_SetSRID(ST_MakePoint(x,y), srid); 

-- Optionally drop the *x*, *y* and *srid* columns
ALTER TABLE DROP COLUMN x;
ALTER TABLE DROP COLUMN y;
ALTER TABLE DROP COLUMN srid;
``` 
