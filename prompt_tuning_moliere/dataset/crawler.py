import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

@dataclass
class URL:
    url: str 
    depth: str = 0

class Crawler:
    def __init__(self, urls=[], max_depth=2):
        urls = [URL(url) for url in urls]
        self.visited_urls = []
        self.urls_to_visit = urls
        self.crawled_docs: List[str] = []
        self.max_depth = max_depth

    def download_url(self, url: URL):
        return requests.get(url.url).text

    def get_linked_urls(self, url: URL, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url.url, path)
            yield URL(path, url.depth + 1)

    def add_url_to_visit(self, url: URL):
        if url.url not in self.visited_urls and url.url not in {u.url for u in self.urls_to_visit}:
            self.urls_to_visit.append(url)

    def crawl(self, url: URL):
        html = self.download_url(url)
        self.crawled_docs.append(html)
        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            if url.depth <= self.max_depth:
                logging.info(f'Crawling: {url}')
                try:
                    self.crawl(url)
                except Exception:
                    logging.exception(f'Failed to crawl: {url}')
                finally:
                    self.visited_urls.append(url.url)

if __name__ == '__main__':
    c = Crawler(urls=["https://www.texteslibres.fr/auteur/moliere-jean-baptiste-poquelin.html"])
    c.run()
    print(len(c.crawled_docs))