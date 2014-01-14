# Creating a time lapse animation

Create a table in PostgreSQL for storing denormalized data:

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
