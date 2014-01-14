import pdb
import lxml.html
import urlparse
import sys
import re

STRIP = ['strip']
STRIP_AND_TITLE = ['strip', 'title']

class Anon(object):
	
	def __new__(cls, **attrs):
		result = object.__new__(cls)
		result.__dict__ = attrs
		return result

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ", ".join(["%s=%s" % (key,value) for key,value in self.__dict__.items()])

def to_unicode_transformed(obj, transforms=None, encoding='utf-8'):
	if isinstance(obj, basestring):
		if transforms:
			for t in transforms:
				obj = getattr(obj, t)()
		if not isinstance(obj, unicode):
			obj = unicode(obj, encoding)
	return obj

def get_scholar(id, mirror):
	
	FULL_NAME = 0
	MATHSCINET = 1
	scholar = Anon (
		id = id, 
		name = None,
		mathscinet_id = None,
		degrees = []
	)
	
	url = "{mirror}/id.php?id={id}".format(mirror=mirror, id=id)
	tree = lxml.html.parse(url)
	if not tree.xpath('//div[@id="paddingWrapper"]'):
		return None
	content = tree.xpath('//div[@id="paddingWrapper"]')[0].getiterator()
	
	for elem in content:
		
		# Full name of scholar
		if elem.tag == 'h2':
			scholar.name = to_unicode_transformed(elem.text, STRIP)  # to unicode
		
		# MathSciNet id
		if elem.tag == 'a' and elem.text == 'MathSciNet':
			
			mathscinet_url = elem.xpath('@href')[0]
			parsed = urlparse.urlparse(mathscinet_url)
			scholar.mathscinet_id = int(urlparse.parse_qs(parsed.query)['mrauthid'][0])  # to int
		
		# BEGIN NEW DEGREE!
		if elem.tag == 'div' and 'line-height: 30px; text-align: center; margin-bottom: 1ex' in elem.values():
			
			degree = Anon(
				degree=None, 
				title=None, 
				year=None, 
				schools=[], 
				countries=[], 
				subject=None, 
				advisors=[]
			)
			scholar.degrees.append(degree)

		# Degree + Year
		if elem.tag == 'span' and 'margin-right: 0.5em' in elem.values():
			degree_and_year = elem.xpath('text()') 
			degree.degree = to_unicode_transformed(degree_and_year[0], STRIP_AND_TITLE)  # to unicode
			years = map(lambda x: int(x), re.findall(r'\d+', degree_and_year[1].strip()))  # find numbers
			if years:
				degree.year = max(years)  # if multiple years, pick latest year, as int

		# School names, split on '/'
		if elem.tag == 'span' and 'color:\n  #006633; margin-left: 0.5em' in elem.values():	
			if elem.text:
				schools = map(lambda x: to_unicode_transformed(x, STRIP_AND_TITLE), elem.text.split('/'))
			else:
				schools = []
			degree.schools += schools  # use title as cannonical form
		
		# Country/flag, read @alt
		if elem.tag == 'img' and 'border: 0; vertical-align: middle' in elem.values():
			countries = map(lambda x: to_unicode_transformed(x, STRIP_AND_TITLE), elem.xpath('@alt')[0].split('-'))
			degree.countries += countries
		
		# Dissertation title
		if elem.tag == 'span' and 'thesisTitle' in elem.values():
			degree.title = to_unicode_transformed(elem.text, STRIP)

		# Mathematical subject
		if elem.tag == 'div' and 'text-align: center; margin-top: 1ex' in elem.values() and 'Mathematics Subject Classification' in elem.text:
			degree.subject = to_unicode_transformed(elem.text.split(':')[1], STRIP)
		
		# Advisors
		if elem.tag == 'p' and 'text-align: center; line-height: 2.75ex' in elem.values():	
			for advisor in elem.xpath('a/@href'):
				degree.advisors.append(int(advisor.split('=')[1]))

	return scholar

	

