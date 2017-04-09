# Scrapper
Get help of using run_scrapper script run follow command:
```commandline
>python run_scrapper.py --help
Usage: run_scrapper.py [OPTIONS]

Options:
  --url TEXT                  Url for start scrapping.
  --requests_threads INTEGER  Number of threads for run http requests in
                              parallel.
  --parser_processes INTEGER  Number of processes for parse html files of
                              pages.
  --max_pages INTEGER         Max number of pages to download.
  --max_level INTEGER         Max number of jumps by links.
  --help                      Show this message and exit.
```