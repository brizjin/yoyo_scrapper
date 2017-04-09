import asyncio
import concurrent
import logging

import click
import re
import requests
import time
from bs4 import BeautifulSoup, SoupStrainer
from tld import get_tld
from urllib.parse import urljoin, urldefrag


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


@click.command()
@click.option('--url', help='Url for start scrapping.')
@click.option('--requests_threads', default=64, help='Number of threads for run http requests in parallel.')
@click.option('--parser_processes', default=16, help='Number of processes for parse html files of pages.')
@click.option('--max_pages', default=1000, help='Max number of pages to download.')
@click.option('--max_level', default=5, help='Max number of jumps by links.')
def scrap_site(url, requests_threads=64, parser_processes=16, max_pages=1000, max_level=5):
    loop = asyncio.get_event_loop()
    site_map = {}

    class Counter:
        page = 1

    c = Counter()

    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=requests_threads)
    processes_pool = concurrent.futures.ProcessPoolExecutor(max_workers=parser_processes)

    async def fetch_request(executor, fetch_url):
        try:
            r = await loop.run_in_executor(executor, requests.get, fetch_url)
            return r.content
        except requests.exceptions.ConnectionError:
            print("fetch_request error on url=", fetch_url)

    async def parse_page(page_url, html_doc):
        return await loop.run_in_executor(processes_pool, parse_html, page_url, html_doc)

    async def spy(spy_url, level=1):
        if spy_url in site_map:
            return
        if c.page > max_pages or level > max_level:
            return
        c.page += 1
        site_map[spy_url] = None
        html_doc = await fetch_request(thread_pool, spy_url)
        if html_doc is not None:
            links, assets = await parse_page(spy_url, html_doc)
            site_map[spy_url] = assets
            await asyncio.gather(*[spy(link, level + 1) for link in links])

    async def main():
        await spy(url)
        return c.page - 1, site_map

    beg_time = time.time()
    pages_loaded, site_map_loaded = loop.run_until_complete(main())
    print("\n\n\nSite-map with assets:")
    for key in sorted(site_map_loaded.keys()):
        print(key, site_map_loaded[key])
    print("Downloaded %s pages from %s for %ss" % (pages_loaded, url, time.time() - beg_time))


if __name__ == "__main__":
    scrap_site()
