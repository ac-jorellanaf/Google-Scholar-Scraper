# Google Scholar Scraper

A wrapper for SerpApi to scrape Google Scholar entries through a keyword search, as well as adding **suggested** DOIs using CrossRef with habanero.

In order to use this, **you must have an account with [SerpApi](https://serpapi.com/users/sign_up?plan=free)** and use your SerpApi key. Free accounts are limited to 250 searches a month, but unless you are trying to obtain 5000 search results in a single month, you should be fine.

## Installation

Download the contents of the repository to your computer (be it using the web interface, or from a release, or with `git clone {URL}`). Open a console and navigate it to the downloaded repository's base folder (i.e. the one containing the `README.md` file), then to the `src` directory, and from there you can run the scraper with `python -m google-scholar-scraper {YOUR_SERP_API_KEY} {YOUR_EMAIL}`.

## Usage

To view the list of arguments, run `python -m google-scholar-scraper -h`.

If you want to use the default query file location, you should create a folder named `queries` in the repository's base folder (i.e. the one containing the `README.md` file). In the `queries` folder, create a `.csv` file named `queries.csv` with the first column defining the search query to use and the second column the number of search results to obtain. See [the example query .csv file](./example_query_file.csv) for further details.

A minimum working example for using an inline query is `python -m google-scholar-scraper {YOUR_SERP_API_KEY} {YOUR_EMAIL} -q="google scholar" -e=200`.

To specify your own query file in another location, run `python -m google-scholar-scraper {YOUR_SERP_API_KEY} {YOUR_EMAIL} f={PATH_TO_FILE}`

## License

This work is an open source work licensed according to the terms of the Unlicense (see license file)
