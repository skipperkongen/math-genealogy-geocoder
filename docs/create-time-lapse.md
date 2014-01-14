# Creating a time lapse animation

Create a table in PostgreSQL for storing denormalized data appropriate for creating an ESRI Shapefile. Latter the Shapefile will be imported into CartoDB (if your account is big enough):

```sql
CREATE TABLE time_lapse (
  id SERIAL PRIMARY KEY,
  scholar_name TEXT,
  degree TEXT,
  thesis_title TEXT,
  university_1 TEXT,    
  country_1 TEXT,
  url TEXT,
  year DATE,
  wkb_geometry GEOMETRY);
```

Fix degree entry for Gerd Brunk. The entry has year as 78, should be 1978:

```sql
UPDATE degree SET year = 1978 WHERE id=89142;
``` 

Populate the table:

```sql 
INSERT INTO time_lapse (scholar_name, degree, thesis_title, university_1, country_1, url, year, wkb_geometry)
SELECT
    p.name, 
    d.degree, 
    d.title, 
    s.name, 
    s.country,
    'http://genealogy.math.ndsu.nodak.edu/id.php?id=' || p.id::text,
    (d.year || '-01-01')::date, 
    l.wkb_geometry
FROM
    degree d, person p, degree_school ds, school s, school_location l
WHERE
    p.id = d.person_id AND
    d.id = ds.degree_id AND
    ds.school_id = s.id AND
    s.id = l.school_id;
```

Delete this one entry which is really old:

```
DELETE FROM time_lapse WHERE year < '1000-01-01';
```


Create an ESRI Shapefile (zipped) from the new table:
```
$ ogr2ogr mathgenealogy-timelapse.shp PG:"host=localhost user=xxxxx password=xxxxx dbname=mathgenealogy" -sql 'select * from time_lapse' -a_srs 'epsg:4326'
$ zip mathgenealogy-timelapse.zip mathgenealogy-timelapse.*
```

Upload this file to CartoDB using the create new table dialogue... create time lapse with the Torque visualization option.

