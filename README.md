# Google Scholar Scraper

A wrapper for the scholarly library to scrape Google Scholar entries through a keyword search, and add suggested DOIs using CrossRef with habanero.  
Note: Scholarly requires the geckodriver browser to allow the user to solve Google captchas.

## Help
```
Scrape Google Scholar entries by keywords.

positional arguments:
  email                 For faster Crossref API queries, we require an e-mail address

optional arguments:
  -h, --help            show this help message and exit
  -q, --querystr
                        Set a custom in-line query, rather than use a query file.
  -qf, --queryfile
                        Set a custom filepath for a .csv file of entries to scrape, rather than use the queries.csv file.
  -n, --numentries
                        Set a custom in-line number of entries to scrape, rather than use the queries.csv file.
  -op, --outdir
                        Set a custom path for the directory where the search .CSV files should be stored.
  -nm, --nomerge
                        Do not merge the .CSV files after searching.
  -nd, --nodoi
                        Do not scrape CrossRef for DOIs after the search.
  -doi, --getdoi
                        Set a directory or file of GS searches for which to find the suggested entry DOIs. Combineable with --nomerge.
  -v, --verbose
                        Verbose mode.
```

# To-Do

*  Write a proper readme.
*  Comment the code.
*  Warm users of the peril of suggested DOIs.
*  Improve iteration method for going through GS entries.
*  Make --nodoi and the email arg mutually exclusive.
*  Warn users about captchas.
*  Add argument to allow for user to input the top n entries to merge