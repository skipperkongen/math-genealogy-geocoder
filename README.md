# Math in genealogy

This Python program creates an updated SQLite3 database containing information from The Mathematics Genealogy Project website. After the database has been created (see Section 2) you can browse it using an SQLite 3 client. The schema described in Section 2.

In the *db* directory, you'll find a snapshot of the database (*db/genealogy.db*), that was complete as of december 2013.

On a Mac, the database ('db/genealogy.db') can be browsed using the *sqlite3* program:

```
$ sqlite3 db/genealogy.db
```

See [sqlite3 instructions](http://www.sqlite.org/sqlite.html) for using this commandline SQLite client program.

## 1: Script usage

Use the *genealogy_tool.py* script (located in this directory) to create the database. Start from scratch by manually deleting the file *'db/genealogy.db'*.
 
### Initialize database

Initialize a new (empty) SQLite3 database (creates db/genealogy.db if it doesn't exist) with schema described in Section 3:

```bash
# Create sqlite3 data
./genealogy_tool.py --initdb
```

### Update database

Add new scholars to the database (or update existing entries). This updates the *person*, *degree*, *degree_advisor*, *degree_school* and *school* tables: 

```bash
# Update scholar with ID=1
./genealogy_tool.py --update 1

# Update scholars with ID in range 10:42 (42 not inclusive)
./genealogy_tool.py --update 10:42

# Update all scholars with ID less than 10
./genealogy_tool.py --update :10

# Update all scholars with ID greater or equal to 128000
./genealogy_tool.py --update :128000

# Mix and match
./genealogy_tool.py --update :10 42 100:200 500:
```

### Geocode database

You can geocode all the schools recorded in database (rows in 'school' table). It is not possible to geocode just a single school. This will add rows to the 'school_location' table, one row for each alternative geocoding found for a particular school. The geocoding uses the school *name* and *country* information as available:

```
./genealogy_tool.py --geocode
```

This currently uses the Google V3 Geocoding API and erases old geocodings created during a previous run.

### Script options

The option for *genealogy_tool.py* can be seen by called with the *--help* or *-h* option:

```bash
$ ./genealogy_tool.py --help
Usage: genealogy_tool.py [Options] [ID, ID, ID, ...]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d DELAY, --delay=DELAY
                        set delay between web service calls (geocoding), with
                        default being 0.2 seconds. Needed to not exceed calls
                        per second allowed by service provider
  -m MIRROR, --mirror=MIRROR
                        set MiG mirror to use (us, de, br). It is not possible
                        to download data from North Dakota site
  -g GC_NAME, --geocoder=GC_NAME
                        set geocoder to use (currently only supports
                        'googlev3', which is also the default)
  -i, --initdb          initialize database (creates new empty database
                        db/genealogy.db). Does not overwrite existing database
                        (remove manually)
  -u, --update          update scholar (with ID=...) in database. Give list of
                        ID's to update using Python list index syntax (see
                        documentation)
  -c, --geocode         geocode all schools in the database (currently only
                        supports Google V3 Geocoding API)
```

## 2: Database schema

A row in the *person* table corresponds an individal page on Math in Genealogy (e.g. http://genealogy.math.ndsu.nodak.edu/id.php?id=176844):

```sql
CREATE TABLE person (
		id INTEGER PRIMARY KEY,  -- E.g. 176844
		name TEXT,  -- e.g. 'Gregory Palamas'
		mathscinet_id INTEGER  -- May be missing
);
```

The *degree* table contains one row for each degree recorded for a person on Math in Genealogy. Not all people have a recorded degree (e.g. http://genealogy.math.ndsu.nodak.edu/id.php?id=176844).

```sql
CREATE TABLE degree (
		id INTEGER PRIMARY KEY,
		person_id INTEGER,  
		degree TEXT,  -- Missing for this scholar
		title TEXT, 
		year INTEGER
);
```

For each degree, the *degree_advisor* table contains a row for each advisor recorded on Math in Genealogy:

```sql
CREATE TABLE degree_advisor (
		degree_id INTEGER,  -- (database) ID of degree 
		person_id INTEGER  -- Math in Genealogy ID of advisor 
);
```

For each degree, the *degree_school* table contain a row for each school recorded on Math in Genealogy. The actual school name is in the *school* table:

```sql
CREATE TABLE degree_school (
		degree_id INTEGER,  -- (database) ID of degree 
		school_id INTEGER -- (database) ID of school
);
```

The *school* table contains unique school names (with country if available) recorded on Math in Genealogy. The country information is obtained from the *alt attribute* of the flag image HTML tag used on the website (e.g. alt="UnitedStates").

```sql
CREATE TABLE school (
		id INTEGER PRIMARY KEY,
		name TEXT,
		country TEXT
);
```

When the *genealogy_tool.py* is called with *--geocode* option, it geocodes each row found in the *school* table, and stores the result in the *school_location* table:

```sql 
CREATE TABLE school_location (
		id INTEGER PRIMARY KEY,
		school_id INTEGER,
		location_name TEXT,
		geocoded_by TEXT,
		x DOUBLE PRECISION,
		y DOUBLE PRECISION,
		srid integer
);
```

### Additional information

Currently the database doesn't store version information, i.e. which version of the software was used to create the database. Might be added in the future.
