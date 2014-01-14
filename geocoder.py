from geopy import geocoders
from random import choice
import pdb

def geocode(search_string, gc_name):
	#print "DEBUG", gc_name
	
	all_coders = {
		#'bing': geocoders.Bing, 
		#'dot_us': geocoders.GeocoderDotUS, 
		#'geonames': geocoders.GeoNames,
		#'google': geocoders.Google, 
		'googlev3': geocoders.GoogleV3, 
		#'mapquest': geocoders.MapQuest, 
		#'openmapquest': geocoders.OpenMapQuest, 
		#'wiki_gis': geocoders.MediaWiki, 
		#'wiki_semantic': geocoders.SemanticMediaWiki, 
		#'yahoo': geocoders.Yahoo
	}
	
	if gc_name.lower() in all_coders:
		geocoder = all_coders[gc_name.lower()]()
	else:
		raise ValueError("Unknown geocoder: " + name.lower())
	
	res = geocoder.geocode(search_string, exactly_one=False) or []
	for geocode in res:
		yield Geocode(geocode[0], geocode[1][0], geocode[1][1], 4326, gc_name.lower())
		

class Geocode:
	def __init__(self, placename, x, y, srid, geocoder=None):
		self.placename = placename
		self.x = x
		self.y = y
		self.srid = srid
		self.geocoder = geocoder
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ", ".join(["%s=%s" % (key,value) for key,value in self.__dict__.items()])