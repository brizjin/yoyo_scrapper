import asyncio
import concurrent
import logging

import re
import requests
import time
from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag

base_url = 'http://yoyowallet.com'
requests_thread_pool_workers = 64
parser_process_pool_workers = 16


def parse_html(url, html_doc):
    start_time = time.time()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s PID %(process)5s %(threadName)10s %(name)18s: %(message)s')
    log_parse_html = logging.getLogger('parse_html ' + url)
    log_parse_html.info("beg")
    soup = BeautifulSoup(html_doc, 'lxml', parse_only=SoupStrainer(['a', 'link', 'img', 'script']))

    links = [urljoin(url, link.get('href')) for link in soup.find_all('a') if link.get('href') is not None]
    links = [link for link in links if get_tld(link, fail_silently=True) == get_tld(url)]
    links = sorted(set(urldefrag(link)[0].strip('/') for link in links if not re.match(".*?(zip|png)$", link)))

    assets = [tag.get('href') for tag in soup.find_all(['a', 'link'])]
    assets += [tag.get('src') for tag in soup.find_all(['img', 'script'])]
    assets = sorted(set(urljoin(url, asset.strip('/')) for asset in assets if asset is not None))
    # remove broken urls such "javascript:;" in python.org.html
    assets = [asset for asset in assets if get_tld(asset, fail_silently=True) is not None]
    # print(base_url, links)
    log_parse_html.info("parsed for %s" % (time.time() - start_time))
    return links, assets


def scrap_site(url):
    loop = asyncio.get_event_loop()
    site_map = {}

    class Level:
        i = 0

    l = Level()

    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=requests_thread_pool_workers)
    processes_pool = concurrent.futures.ProcessPoolExecutor(max_workers=parser_process_pool_workers)

    async def fetch_request(executor, url):
        try:
            r = await loop.run_in_executor(executor, requests.get, url)
            return r.content
        except Exception as e:
            print("fetch_request error on url=", url)

    async def parse_page(url, html_doc):
        return await loop.run_in_executor(processes_pool, parse_html, url, html_doc)

    async def spy(url):
        if url in site_map:
            return
        if l.i > 1000:
            return
        l.i += 1
        site_map[url] = None
        html_doc = await fetch_request(thread_pool, url)
        if html_doc is not None:
            links, assets = await parse_page(url, html_doc)
            site_map[url] = assets
            await asyncio.gather(*[spy(link) for link in links])

    async def main():
        await spy(url)
        return site_map

    return loop.run_until_complete(main())
    # print(html.keys())
    # print(html[list(html.keys())[10]])


if __name__ == "__main__":
    beg_time = time.time()
    site_map = scrap_site(base_url)
    # print("\n".join(sorted(site_map.keys())))
    print("\n\n\nSite-map with assets:")
    for key in sorted(site_map.keys()):
        print(key, site_map[key])
    print("Site %s have been scraped for %s" % (base_url, time.time() - beg_time))
