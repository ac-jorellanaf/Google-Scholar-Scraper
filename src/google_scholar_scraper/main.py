from google_scholar_scraper.config import parse_args
from google_scholar_scraper.serp_query import scrape_google_scholar
from google_scholar_scraper.utils import merge_search, parse_queries, select_dir
from google_scholar_scraper.crossref_query.crossref_query import crossref_query
import time
from pathlib import Path as p
from sys import exit


def main():
    """Main function to initialise the Google Scholar Scraper"""

    # Get the arguments from the parser
    args = parse_args()

    # Assign them to prettier variables
    serp_api_key, email, query_file, query_string, interactive_query_file_picker, \
        max_results, base_output_dir, interactive_base_output_dir_picker, \
        custom_output_dir_name, no_merge, no_doi, doi_only, recursive_doi_only, \
        verbose = \
        args.serp_api_key, args.email, args.query_file, \
        args.query_string, args.interactive_query_file_picker, \
        args.max_results, args.base_output_dir, \
        args.interactive_base_output_dir_picker, \
        args.custom_output_dir_name, args.no_merge, args.no_doi, args.doi_only, \
        args.recursive_doi_only, args.verbose

    if verbose:
        print('\nGoogle Scholar Scraper')

    # Check that max_results can be converted to an integer and is greater than 0
    try:
        assert int(max_results) if max_results else True
        assert max_results > 0 if max_results else True
    except Exception:
        print(
            f'\nError: max_results ("{max_results}") is not a valid positive integer')
        exit(406)

    # Take the base output dir value and convert it to a Path object
    base_output_dir = p(base_output_dir)

    # If the user requested the use of the interactive directory picker,
    # run the method to get the chosen base output directory
    if (interactive_base_output_dir_picker):
        base_output_dir = select_dir()

    # If the user did not specify a custom output directory name, specify
    # the default one using the current timestamp
    if (not custom_output_dir_name):
        custom_output_dir_name = time.strftime(
            '%Y-%m-%dT%H%M%S', time.localtime(time.time()))
    # Create the output directory recursively
    output_dir = p(base_output_dir / custom_output_dir_name)
    output_dir.mkdir(exist_ok=True, parents=True)
    if (verbose):
        print(f'\nOutput path: {str(output_dir)}')

    # If we do not want to just get the DOI for existing search results
    if (not doi_only):
        # Get the list of queries to run
        parsed_queries = parse_queries(
            query_string, max_results, query_file, interactive_query_file_picker)
        # Declare an array of output file paths
        output_files = []

        # If we want verbose logging, show the results of the query parsing
        if (verbose):
            print(f'\nNumber of queries: {len(parsed_queries)}')
            print('\nQueries parsed:')
            for (query, max_results) in parsed_queries:
                print(f'query: {query}: {max_results} desired results.')

        # For each query, run the google scholar scraper, and store its return
        # value (the path of the output file) in the array of output files
        for query, max_results in parsed_queries:
            if (verbose):
                print(f'\nStarting Google Scholar scrape: {query}')
            output_files.append(
                scrape_google_scholar(serp_api_key, query, max_results, output_dir, verbose))
    # If we do want to perform the DOI search
    else:
        # If the specified value is a file, add it to the output files array
        if (p(doi_only).absolute().is_file()):
            output_files = [p(doi_only)]
        # If it is a directory, add all the .csv files in the directory,
        # recursively, if specified as such
        elif (p(doi_only).absolute().is_dir()):
            output_files = [x for x in p(doi_only).glob(
                '**/*.csv' if recursive_doi_only else '*.csv')]
        # If the doi-only argument is not an existing file nor directory, print
        # an error and exit
        else:
            print(
                f'\nError: no file or directory found for the DOI search ({doi_only})')
            exit(404)

    # If we do want to get DOIs for search results (i.e. if nodoi was not set)
    # run the crossref queries with
    if (not no_doi):
        crossref_query(email, verbose, output_files)

    # If we are not just performing DOI queries or do want to merge
    # (i.e. if nomerge was not set), and we have more than one output file,
    # we should merge these into one file
    if (not doi_only and len(output_files) > 1 or not no_merge and len(output_files) > 1):
        merge_search(output_files, output_dir, verbose)
