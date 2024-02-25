#!/usr/bin/env python3
# reference.bib to markdown

# wget https://raw.githubusercontent.com/dendibakh/perf-book/main/biblio.bib -O references.bib
# Usage: python bib2markdown.py references.bib > outfile.md

import bibtexparser
import sys

with open(sys.argv[1]) as bibtex_file:
    bibtex_str = bibtex_file.read()

bib_database = bibtexparser.loads(bibtex_str)

print("References")
print("==========")

def print_article(entry):
	# bibtex separates authors with ' and '
	authors = entry['author'].replace(' and ', ', ')
	
	# these keys are (supposed to be) in every entry
	print('**{}** {}. {}.'.format(
		authors, 
		entry['year'], 
		entry['title'], 
		)),
	
	# not every entry has these
	if 'volume' in entry:
		print('**{}**'.format(entry['volume'])),
		if 'number' in entry:
			print('({}):'.format(entry['number'])),
		else:
			print(':',)
	else:
		if 'number' in entry:
			print('{}:'.format(entry['number'])),
	if 'pages' in entry:
		print('{}.'.format(entry['pages'])),
	
	# should appear in every entry:
	if hasattr(entry, 'doi'):
		print('[[{}](http://doi.org/{})]'.format(entry['doi'],entry['doi'])),
	print('`[id:{}]`\n'.format(entry['ID']))


def print_ref_table(entry):
	# this is an HTML anchor so we can refer to the reference entry in markdown as:
	# [Foo2017](../REFERENCES#Foo2017)
	print('\n<div id="{}"></div>'.format(entry['ID']))
	print('`[@{}]`\n'.format(entry['ID']))
	sk = "|"
	for key in entry.keys():
		sk += " {} |".format(key)
	print(sk)

	s = "|"
	for key in entry.keys():
		s += "---|"
	print(s)

	sv = "|"
	for key in entry.keys():
		sv += " {} |".format(entry[key].replace('\n', ', '))
	print(sv)
	return
	

for entry in bib_database.entries:
	#print(entry)

	print_ref_table(entry)
