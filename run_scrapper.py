from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag


def parse_html(base_url, html_doc):
    soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer('a'))
    links = [link.get('href') for link in soup.find_all('a')]  # find all a-tags and get href of it
    links = [urljoin(base_url, link) for link in links]  # convert relative links to absolute
    links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(base_url)]
    links = sorted(set(urldefrag(link)[0].strip('/') for link in links))
    return links
