#!/usr/bin/env python

import pdb
from optparse import OptionParser
from callbacks import init_db, update_db, geocode_db

if __name__ == "__main__":
	parser = OptionParser("%prog [Options] [ID, ID, ID, ...]", version="%prog 0.1")
	parser.add_option("-d", "--delay", type="float", dest="delay", default=0.2, help="set delay between web service calls (geocoding), with default being 0.2 seconds. Needed to not exceed calls per second allowed by service provider")
	parser.add_option("-m", "--mirror", type="string", dest="mirror", default="us", help="set MiG mirror to use (us, de, br). It is not possible to download data from North Dakota site")
	parser.add_option("-g", "--geocoder", type="string", dest="gc_name", default="googlev3", help="set geocoder to use (currently only supports 'googlev3', which is also the default)")
	# methods
	parser.add_option("-i", "--initdb", help="initialize database (creates new empty database db/genealogy.db). Does not overwrite existing database (remove manually)", action="callback", callback=init_db)
	parser.add_option("-u", "--update", help="update scholar (with ID=...) in database. Give list of ID's to update using Python list index syntax (see documentation)", action="callback", callback=update_db)
	parser.add_option("-c", "--geocode", help="geocode all schools in the database (currently only supports Google V3 Geocoding API)", action="callback", callback=geocode_db)
	
	parser.parse_args()
