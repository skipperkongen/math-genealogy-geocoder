import sqlite3
import os
import sys
import pdb
import lxml.html
import time
import scraper
import traceback
from geopy import geocoders

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'db', 'genealogy.db')

def init_db(option, opt, value, parser):
	
	print "Initializing database..."	
	try:
		dbbuilder = DatabaseBuilder()
		dbbuilder.init_db()
	except:
		#traceback.print_exc()
		#print ''
		print sys.exc_info()[1].message
		sys.exit(1)
	sys.exit(0)
	

def update_db(option, opt, value, parser):
	
	print "Updating database..."
	try:
		dbbuilder = DatabaseBuilder()
		dbbuilder.update_db(
			parser.values.mirror,
			parser.values.delay,
			*parser.rargs
		)
	except:
		traceback.print_exc()
		print ''
		print sys.exc_info()[1].message
		sys.exit(1)
	sys.exit(0)


def geocode_db(option, opt, value, parser):
	
	print "Geocoding schools..."
	try:
		dbbuilder = DatabaseBuilder()
		dbbuilder.geocode_db(parser.values.gc_name)
	except:
		traceback.print_exc()
		print ''
		print sys.exc_info()[1].message
		sys.exit(1)
	sys.exit(0)
	

class DatabaseBuilder:
	
	def init_db(self):
		
		if os.path.isfile(DB_PATH):
			raise ValueError('Database file (db/genealogy.db) already exists. Remove it first.')


		conn_sqlite3 = sqlite3.connect(DB_PATH)
		c = conn_sqlite3.cursor()

		# Create table
		c.execute('''
CREATE TABLE person (
		id INTEGER PRIMARY KEY,  -- MiG ID
		name TEXT,
		mathscinet_id INTEGER
);
		''')

		c.execute('''
CREATE TABLE degree (
		id INTEGER PRIMARY KEY,
		person_id INTEGER,
		degree TEXT,
		title TEXT,
		year INTEGER
);
		''')

		c.execute('''
CREATE TABLE degree_advisor (
		degree_id INTEGER,
		person_id INTEGER
);
		''')

		c.execute('''
CREATE TABLE degree_school (
		degree_id INTEGER,
		school_id INTEGER
);
		''')

		c.execute('''
CREATE TABLE school (
		id INTEGER PRIMARY KEY,
		name TEXT,
		country TEXT
);
		''')

		c.execute('''
CREATE TABLE school_location (
		id INTEGER PRIMARY KEY,
		school_id INTEGER,
		location_name TEXT,
		geocoded_by TEXT,
		x DOUBLE PRECISION,
		y DOUBLE PRECISION,
		srid integer
);
		''')
		
		conn_sqlite3.commit()
		conn_sqlite3.close()

				
	def update_db(self, mirror_key, delay_ms, *args):
		self._check_db_exist()
		mirror = self._get_mirror(mirror_key)
		count = self._get_count(mirror)
		ids = self._ids_from_args(args, count)
		
		conn = sqlite3.connect(DB_PATH)
		# Fetch scholars from mirror
		completed = 0.0
		for id in ids:
			# Get scholar from website
			scholar = scraper.get_scholar(id, mirror)
			if not scholar: continue
			# Update database
			self._update_scholar_in_db(scholar, conn)
			completed += 1.0
			# Progress bar update...
			sys.stdout.write("Completed: %.2f%% (id=%d)  \r" % (100.0*completed/len(ids), id) ) 
			sys.stdout.flush()
		conn.close()
		print ''
				
	def geocode_db(self, gc_name, delay_s=.1):
		
		# SQL time
		conn = sqlite3.connect(DB_PATH)
		cur = conn.cursor()
				
		# delete geocodings made with same geocoder
		cur.execute('''DELETE FROM school_location WHERE geocoded_by=?''', (gc_name,))
		cur.execute('''SELECT id, name, country FROM school''')
		
		# geocoder
		geocoder = geocoders.GoogleV3()
		gc_name = 'googlev3'
		
		for row in cur.fetchall():
			# Geocode row
			id, name, country = row
			if country:
				searchstring = "%s, %s" % (name.encode('utf-8'), country.encode('utf-8'))
			else:
				searchstring = name
			# stay under call limit
			time.sleep(delay_s)
			sys.stdout.write("Geocoding school: %s, %s                        \r" % (name, country) ) 
			sys.stdout.flush()
			try:
				locations = geocoder.geocode(searchstring, exactly_one=False) or []
			except:
				locations = []
			for gc in locations:
				cur.execute('''INSERT INTO school_location
				(school_id, location_name, geocoded_by, x, y, srid) VALUES (?, ?, ?, ?, ?, ?)''',
				(id, gc[0], gc_name, gc[1][1], gc[1][0], 4326))
				break  # only use first geocoding
		conn.commit()
		conn.close()
		print ''

	def _update_scholar_in_db(self, scholar, conn):
		# SQL time
		cur = conn.cursor()

		# Update person
		cur.execute('''INSERT OR REPLACE INTO person (id, name, mathscinet_id)
		  VALUES (?, ?, ?);''', (scholar.id, scholar.name, scholar.mathscinet_id))
		
		# Delete "old" degrees
		cur.execute('''DELETE FROM degree_advisor WHERE degree_id IN (SELECT id FROM degree WHERE person_id=?)''', (scholar.id,))
		cur.execute('''DELETE FROM degree_school WHERE degree_id IN (SELECT id FROM degree WHERE person_id=?)''', (scholar.id,))				
		cur.execute('''DELETE FROM degree WHERE person_id=?''', (scholar.id,))

		# Insert "new" degrees, one at a time (does not work with concurrent access to db)
		for degree in scholar.degrees:
			
			# Insert "new" degree
			cur.execute('''INSERT INTO degree 
			(person_id, degree, title, year) VALUES (?, ?, ?, ?)''',
			(scholar.id, degree.degree, degree.title, degree.year))
			conn.commit()  # to get lastrowid
			# New degree id
			degree_id = cur.lastrowid

			# Add advisors
			for advisor in degree.advisors:
				cur.execute('''INSERT INTO degree_advisor
				(degree_id, person_id) VALUES (?, ?)''',
				(degree_id, advisor))
			
			# Insert new schools. First check if exists already
			for i, name in enumerate(degree.schools):
				country = (degree.countries[i] if i < len(degree.countries) else None)
				# check if school exists
				cur.execute('''SELECT id FROM school WHERE name=? AND country=?''', (name, country))
				row = cur.fetchone()
				school_id = row[0] if row else None
				if not school_id:
					# Create new school
					cur.execute('''INSERT INTO school
					(name, country) VALUES (?, ?)''',
					(name, country))
					conn.commit()
					school_id = cur.lastrowid
				# Use school
				cur.execute('''INSERT INTO degree_school
				(degree_id, school_id) VALUES (?, ?)''',
				(degree_id, school_id))
			
		conn.commit()

	def _ids_from_args(self, args, count):

		if not args:
			return set().union(range(1, count+1))
		s = set()
		for v in args:
			v_ints = [int(x) for x in v.split(":") if x.isdigit()]
			if v.startswith(':') and len(v_ints) == 1:
				s = s.union(range(1, v_ints[0]))
			elif v.endswith(':') and len(v_ints) == 1:
				s = s.union(range(v_ints[0], count+1))
			elif ':' in v and len(v_ints) == 2 and v_ints[0] < v_ints[1]:
				s = s.union(range(v_ints[0],v_ints[1]))
			elif len(v_ints) == 1:
				s.add(v_ints[0])
			else:
				raise ValueError("Arguments must be on form 'i', ':i', 'i:' or 'i:j' where i<j")
		return s
	
	def _check_db_exist(self):
		if not os.path.isfile(DB_PATH):
			raise ValueError("db/genealogy.db does not exist. Run again with --initdb option")
	
	def _get_mirror(self, mirror):
		all_mirrors = {
			'us': 'http://www.genealogy.ams.org/',
			'de':'http://genealogy.math.uni-bielefeld.de/',
			'br':'http://genealogy.impa.br/'
		}
		if mirror.lower() in all_mirrors:
			return all_mirrors[mirror.lower()]
		else:
			raise ValueError("Unknown mirror:",mirror.lower())
	
	def _get_count(self, mirror):
		print "Fetching count for scholars on", mirror
		tree = lxml.html.parse(mirror)
		count_text = tree.xpath("//span[@style='font-size: x-large; color: red; font-style:  italic']")[0].text
		return int(count_text.split()[0])
