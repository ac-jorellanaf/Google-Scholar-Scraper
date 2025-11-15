import argparse
from pathlib import Path as p


def parse_args():
    """Parse the command line arguments to run the module"""
    BASE_DIR = p.cwd().absolute() if p.cwd(
    ).parts[-1] != 'src' else p.cwd().absolute().parent

    parser = argparse.ArgumentParser(prog='Google Scholar Scraper',
                                     description='Scrape Google Scholar entries by keywords.')
    parser.add_argument(
        'serp_api_key', help='The API key for your SERP account to use to scrape Google Scholar data.'
    )
    parser.add_argument(
        'email', help='For faster Crossref API queries, we require an email address.')

    querygroup = parser.add_mutually_exclusive_group()
    querygroup.add_argument('-f', '--query-file',
                            help="""Set the filepath for a .csv file of entries
                            to scrape. By default, this file should be located
                            inside the "queries" folder within the base module
                            folder, and named 'queries.csv'""",
                            default=str(
                                p(BASE_DIR / 'queries' / 'queries.csv')),
                            type=str)
    querygroup.add_argument('-q', '--query-string',
                            help='Set a custom in-line query string, rather than use a query file. Requires setting the -e/--max-results argument.',
                            type=str)

    parser.add_argument('-e', '--max-results',
                        help="""Sets the maximum number of search results to
                        scrape when using a query string or the default number
                        of maximum search results when using a file to use when
                        not specifying the max number of search results for one
                        or more queries.""",
                        default=20,
                        type=int),
    parser.add_argument('-b', '--base-output-dir',
                        help="""Set the path for the base output directory
                        where the search result .csv files should be stored.
                        By default, this is an 'output' folder located inside
                        the base module directory.""",
                        default=str(p(BASE_DIR / 'output')),
                        type=str)
    parser.add_argument('-o', '--custom-output-dir',
                        help="""By default, the scraper creates a directory with
                        the current timestamp inside the base output folder
                        every time it is run and stores the search results
                        there. Provide the a valid directory name if you wish to
                        use a custom name instead.""",
                        type=str)
    parser.add_argument('-m', '--no-merge',
                        help='Set this to true to prevent merging the individual query .csv files into a single .csv file.',
                        default=False,
                        type=bool)

    doi_group = parser.add_mutually_exclusive_group()
    doi_group.add_argument('-n', '--no-doi',
                           metavar='NO_DOI_SEARCH',
                           help='Set this to true to prevent scraping CrossRef for DOIs after the search.',
                           default=False,
                           type=bool)
    doi_group.add_argument('-d', '--doi-only',
                           help="""Set the path for either a .csv file of scraped
                          results or a directory containing such files to obtain
                          DOIs for the results without actually performing a
                          search query.""",
                           type=str)
    parser.add_argument('-r', '--recursive-doi-only',
                              help='Search recursively for all .csv files in the folder specified for running DOI-only searches. Only works for doi-only searches',
                              action='store_true')

    parser.add_argument('-v', '--verbose',
                        help='Verbose logging mode.',
                        action='store_true')
    args = parser.parse_args()

    return args


class global_vars:
    author_key = 'AUTHOR'
    pub_year_key = 'PUB_YEAR'
    title_key = 'TITLE'
    scholar_link_key = 'SCHOLAR_LINK'
    pub_url_key = 'PUB_URL'
    gs_rank_key = 'GSRANK'
    num_citations_key = 'NUM_CITATIONS'
    doi_key = 'SUGGESTED_DOI'
    max_attempts = 5
    default_max_entries = 20
