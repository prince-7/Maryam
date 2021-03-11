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

from core.module import BaseModule
import re
import concurrent.futures

class Module(BaseModule):
	meta = {
		'name': 'Reddit Search',
		'author': 'Kunal Khandelwal',
		'version': '0.5',
		'description': 'Search your query in the Reddit and show the results.',
		'sources': ('google', 'yahoo', 'bing', 'yippy', 'metacrawler', 'millionshort', 'carrot2', 'qwant'),
		'options': (
			('query', None, True, 'Query string', '-q', 'store'),
			('limit', 1, False, 'Search limit(number of pages, default=1)', '-l', 'store'),
			('count', 50, False, 'Number of links per page(min=10, max=100, default=50)', '-c', 'store'),
			('engine', 'google', False, 'Engine names for search(default=google)', '-e', 'store'),
			('thread', 2, False, 'The number of engine that run per round(default=2)', '-t', 'store'),
			('output', False, False, 'Save output to workspace', '--output', 'store_true'),
		),
		'examples': ('reddit -q <QUERY> -l 15 --output',)
	}

	links = []

	def set_data(self, urls):
		for url in urls:
			self.links.append(url)

	def thread(self, function, thread_count, engines, q, q_formats, limit, count):
		threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)
		futures = (threadpool.submit(
			function, name, q, q_formats, limit, count) for name in engines if name in self.meta['sources'])
		for _ in concurrent.futures.as_completed(futures):
			pass

	def search(self, name, q, q_formats, limit, count):
		engine = getattr(self, name)
		name = engine.__name__

		q = f"{name}_q" if f"{name}_q" in q_formats else q_formats['default_q']

		varnames = engine.__code__.co_varnames

		if 'limit' in varnames and 'count' in varnames:
			attr = engine(q, limit, count)
		elif 'limit' in varnames:
			attr = engine(q, limit)
		else:
			attr = engine(q)

		attr.run_crawl()
		self.set_data(attr.links)

	def module_run(self):
		query = self.options['query']
		limit = self.options['limit']
		count = self.options['count']
		engine = self.options['engine'].split(',')
		q_formats = {
			'default_q': f"site:www.reddit.com {query}",
			'yippy_q': f'"www.reddit.com" {query}',
			'millionshort_q': f'site:www.reddit.com "{query}"',
			'qwant_q': f'site:www.reddit.com {query}'
		}
		usernames = []

		self.thread(self.search, self.options['thread'], engine, query, q_formats, limit, count)

		links = list(set(self.links))
		links = list(self.reglib().filter(r"https?://(www\.)?reddit\.com/", links))
		if not links:
			self.output('Without result')
		else:
			self.alert('usernames')
			for link in self.reglib().filter(r"https?://(www\.)?reddit\.com/user/", links):
				link = re.sub(r"https?://(www\.)?reddit\.com/user/", '', link)
				if re.search(r'^[\w\d_\-\/]+$', link):
					link = link.rsplit('/')
					if link[0] not in usernames:
						usernames.append(link[0])
						self.output(f"\t@{link[0]}", 'G')

			self.alert('posts')
			for link in links:
				if re.search(r"reddit\.com/r/", link) and "/about/" not in link:
					post_url = re.sub(r"https?://(www\.)?reddit\.com/r/", '', link)
					post_url = post_url.rsplit('/')
					subreddit = post_url[0]
					try:
						post = post_url[3]
					except Exception as e:
						continue

					post = post.replace('_', ' ')
					post = self.urlib(post).unquote
					self.output(f"\t{post.title()} => r/{subreddit}")
					self.output(f"\t\t{link}", 'G')

		self.save_gather({'links': links, 'usernames': usernames},
						 'search/reddit', query, output=self.options.get('output'))
