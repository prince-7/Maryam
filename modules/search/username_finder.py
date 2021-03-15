"""
OWASP Maryam!
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import concurrent.futures
import os

meta = {
	'name': 'UserName Finder',
	'author': 'Aman Singh',
	'version': '0.1',
	'description': 'Search a username across 100+ Social networks',
	'sources': ('google', 'carrot2', 'bing', 'yippy', 'yahoo', 'millionshort', 'qwant', 'duckduckgo'),
	'options': (
		('query', None, True, 'Query string', '-q', 'store'),
		('limit', 1, False, 'Search limit(number of pages, default=1)', '-l', 'store'),
		('count', 50, False, 'Number of results per page(min=10, max=100, default=50)', '-c', 'store'),
		('thread', 2, False, 'The number of engine that run per round(default=2)', '-t', 'store'),
		('engine', 'google,yippy', False, 'Engine names for search(default=google)', '-e', 'store'),
	),
	'examples': ('username -q <QUERY> -l 15 --output',)
}

LINKS = []
PAGES = ''

def thread(function, self, thread_count, engines, q, q_formats, limit, count):
	threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)
	futures = (threadpool.submit(function, self, name, q, q_formats, limit, count))
	for _ in concurrent.futures.as_completed(futures):
		pass

def search(self, name, q, q_formats, limit, count):
	global PAGES,LINKS
	engine = getattr(self, name)
	name = engine.__init__.__name__
	q = q_formats['default_q']
	varnames = engine.__init__.__code__.co_varnames
	if 'limit' in varnames and 'count' in varnames:
		attr = engine(q, limit, count)
	elif 'limit' in varnames:
		attr = engine(q, limit)
	else:
		attr = engine(q)

	attr.run_crawl()
	LINKS += attr.links
	PAGES += attr.pages
	if name == 'google':
		attr.q = q_formats['default_q']
		attr.run_crawl()
		PAGES += attr.pages

def module_api(self):
	query = self.options['query']
	limit = self.options['limit']
	count = self.options['count']
	output = {'profiles': []}
	engines = self.options['engine'].split(',')
	filename = os.path.abspath(os.curdir) + '/data/username_checker.json'
	file = open(filename)
	data = json.loads(file.read())
	for site in data:
		q_formats = {
			'default_q': data[site][url].format(query)
		}
		thread(search, self, self.options['thread'], engines, query, q_formats, limit, count)
	links = filter(list(set(LINKS)))
	networks = self.page_parse(PAGES).get_networks
	output['profiles'] = list(set(networks))
	self.save_gather(output, 'search/username_finder', query, output=self.options.get('output'))
	return output

def module_run(self):
	self.alert_results(module_api(self))