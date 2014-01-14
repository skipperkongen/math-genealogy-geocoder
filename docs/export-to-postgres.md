# Export SQLite database to PostgreSQL

Exporting the database from SQLite to PostgreSQL

```
sqlite3 genealogy.db .dump > dump.sql
psql -d <DATABASENAME> -U <USERNAME> -W < dump.sql
```

In the SQLIte database, geographical points are represented with an *x* and *y* column (should properly be called long and lat).
It is easy convert these two floating point columns into a proper GEOMETRY column in PostgreSQL:
 
```sql
-- Start by adding PostGIS extensions if not already installed
create extension postgis;

-- Add column
ALTER TABLE school_location ADD COLUMN wkb_geometry GEOMETRY;

-- Write a point value into the GEOMETRY column, using the *x*, *y* and *srid* columns
UPDATE school_location
SET wkb_geometry = ST_SetSRID(ST_MakePoint(x,y), srid); 

-- Optionally drop the *x*, *y* and *srid* columns
ALTER TABLE DROP COLUMN x;
ALTER TABLE DROP COLUMN y;
ALTER TABLE DROP COLUMN srid;
``` 
