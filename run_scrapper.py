from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag


def parse_html(base_url, html_doc):
    soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer(['a', 'link', 'img', 'script']))

    links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a') if link.get('href') is not None]
    links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(base_url)]
    links = sorted(set(urldefrag(link)[0].strip('/') for link in links))

    assets = [tag.get('href') for tag in soup.find_all(['a', 'link'])]
    assets += [tag.get('src') for tag in soup.find_all(['img', 'script'])]
    assets = sorted(set(urljoin(base_url, asset.strip('/')) for asset in assets if asset is not None))
    # remove broken urls such "javascript:;" in python.org.html
    assets = [asset for asset in assets if get_tld(asset, fail_silently=True) is not None]
    return links, assets
