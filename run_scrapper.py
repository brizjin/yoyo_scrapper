import asyncio
import concurrent
import logging

import requests
from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag


def parse_html(base_url, html_doc):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s PID %(process)5s %(threadName)10s %(name)18s: %(message)s')
    log_parse_html = logging.getLogger('parse_html ' + base_url)
    log_parse_html.info("beg")
    soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer(['a', 'link', 'img', 'script']))

    links = [urljoin(base_url, link.get('href')) for link in soup.find_all('a') if link.get('href') is not None]
    links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(base_url)]
    links = sorted(set(urldefrag(link)[0].strip('/') for link in links))

    assets = [tag.get('href') for tag in soup.find_all(['a', 'link'])]
    assets += [tag.get('src') for tag in soup.find_all(['img', 'script'])]
    assets = sorted(set(urljoin(base_url, asset.strip('/')) for asset in assets if asset is not None))
    # remove broken urls such "javascript:;" in python.org.html
    assets = [asset for asset in assets if get_tld(asset, fail_silently=True) is not None]
    # log_parse_html.info("end")
    return links, assets


def scrap_site(base_url):
    loop = asyncio.get_event_loop()
    site_map = {}

    class Level:
        i = 0

    l = Level()

    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=256)
    processes_pool = concurrent.futures.ProcessPoolExecutor(max_workers=32)

    async def fetch_request(executor, url):
        r = await loop.run_in_executor(executor, requests.get, url)
        return r.content

    async def parse_page(url, html_doc):
        return await loop.run_in_executor(processes_pool, parse_html, url, html_doc)

    async def spy(url):
        if url in site_map:
            return
        if l.i > 100:
            return
        l.i += 1
        site_map[url] = None
        html_doc = await fetch_request(thread_pool, url)
        links, assets = await parse_page(url, html_doc)
        site_map[url] = assets
        await asyncio.gather(*[spy(link) for link in links])

    async def main():
        await spy(base_url)
        return site_map

    html = loop.run_until_complete(main())
    print(html.keys())
    print(html[list(html.keys())[10]])


if __name__ == "__main__":
    # scrap_site('http://python.org')
    scrap_site('http://yoyowallet.com/')
