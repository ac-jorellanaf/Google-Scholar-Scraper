import argparse
from pathlib import Path as p


def parse_args():
    """Parse the command line arguments to run the module"""
    # Obtain the default base directory. If the user is running this module
    # locally, then the CWD would be in ROOT/src, so we check if this is the
    # case and adjust the path accordingly.
    DEFAULT_BASE_DIR = p.cwd().absolute() if p.cwd(
    ).parts[-1] != 'src' else p.cwd().absolute().parent

    # Set up the command line argument parser
    parser = argparse.ArgumentParser(prog='Google Scholar Scraper',
                                     description='Scrape Google Scholar entries by keywords.')
    parser.add_argument(
        'serp_api_key', help='The API key for your SerpApi account to use to scrape Google Scholar data.'
    )
    parser.add_argument(
        'email', help='For faster Crossref API queries, we require an email address.')

    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument('-f', '--query-file',
                             help="""Set the filepath for a .csv file of entries
                            to scrape. By default, this file should be located
                            inside the "queries" folder within the base module
                            folder, and named 'queries.csv'""",
                             default=str(
                                 p(DEFAULT_BASE_DIR / 'queries' / 'queries.csv')),
                             type=str)
    query_group.add_argument('-q', '--query-string',
                             help='Set a custom in-line query string, rather than use a query file. if the max-results argument is not set, the default number of search results.',
                             type=str)

    parser.add_argument('-i', '--interactive-query-file-picker',
                        help="""Use this option to show a window to select your
                        query file instead of manually inputting it in the
                        command line. This setting will override any value set
                        for either the query file or the query string.""",
                        action='store_true')
    parser.add_argument('-m', '--max-results',
                        help="""Sets the maximum number of search results to
                        scrape when using a query string or the default number
                        of maximum search results when using a query file (and
                        one or more queries do not have a specific max search
                        results). Default = 20.""",
                        default=20,
                        type=int),

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-b', '--base-output-dir',
                              help="""Set the path for the base output directory
                        where the search result .csv files should be stored.
                        By default, this is an 'output' folder located inside
                        the base module directory.""",
                              default=str(p(DEFAULT_BASE_DIR / 'output')),
                              type=str)
    output_group.add_argument('-I', '--interactive-base-output-dir-picker',
                              help="""Use this option to show a window to select
                              your base output directory instead of manually
                              inputting it in the command line.""",
                              action='store_true')
    parser.add_argument('-o', '--custom-output-dir-name',
                        help="""By default, the scraper creates a directory with
                        the current timestamp inside the base output folder
                        every time it is run and stores the search results
                        there. Provide a valid folder name if you wish not to
                        use the auto-generated directory names (note that
                        therefore all queries will be stored in the same folder).""",
                        type=str)
    parser.add_argument('-n', '--no-merge',
                        help='Use this option to prevent merging the individual query .csv files into a single .csv file that has any duplicates removed.',
                        action='store_true')

    doi_group = parser.add_mutually_exclusive_group()
    doi_group.add_argument('-N', '--no-doi',
                           help='Use this option to prevent scraping CrossRef for DOIs after the search.',
                           action='store_true')
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

    # Returned the parsed args
    return args


class global_vars:
    """Class to store globally-accessible read-only variables with more
    easily-readable and refactor-able dot syntax."""
    author_key = 'AUTHOR'
    pub_year_key = 'PUB_YEAR'
    title_key = 'TITLE'
    scholar_link_key = 'SCHOLAR_LINK'
    pub_url_key = 'PUB_URL'
    gs_rank_key = 'GSRANK'
    num_citations_key = 'NUM_CITATIONS'
    doi_key = 'SUGGESTED_DOI'
    max_attempts = 5
    default_max_results = 20
    default_serp_max_results = 20
