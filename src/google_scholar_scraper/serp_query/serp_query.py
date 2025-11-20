import csv
import time
import re
from pathlib import Path as p
from google_scholar_scraper.config import global_vars
from urllib import request, parse
import json
import math
from sys import exit


def scrape_google_scholar(serp_api_key, search_query, max_results, base_output_dir, verbose):
    """Method to scrape Google Scholar via a query using SerpApi and return the
    path of the file where the results were saved."""
    # Pre-allocate an array of size max_results for better performance
    results = [None] * max_results

    def _process_queries():
        """Process the queries"""
        # The maximum number of search results returnable by SerpApi is set in a global variable,
        # so divide the desired total number of search results for the query into
        # batches of at most the maximum results of a SerpApi query.
        for i in range(math.ceil(max_results / global_vars.default_serp_max_results)):
            # We define which search results we want based on the batch index
            # and the number of maximum results for SerpApi
            start = i * global_vars.default_serp_max_results
            # Also specify how many results we actually want to request from SerpApi,
            # which is normally the maximum, except when the last batch is smaller
            # than the maximum
            num_results = min(max_results - start,
                              global_vars.default_serp_max_results)

            # Attempt the query as many times as we have set
            for attempt in range(global_vars.max_attempts):
                # Try to query the API
                try:
                    # URL encode the search query we want to use to search Google Scholar with
                    clean_query = parse.quote_plus(search_query)
                    # Build the query URL
                    url = f'https://serpapi.com/search?engine=google_scholar&api_key={serp_api_key}' +\
                        f'&start={start}&num={num_results}&q={clean_query}'
                    # Process the response
                    with request.urlopen(url) as response:
                        # Store the JSON response into a dictionary
                        search_results = json.loads(response.read())
                        # We only care about the 'organic_results' property, so
                        # overwrite the search_results variable with it
                        search_results = search_results['organic_results']

                        # Loop through the search results, keeping track of the index
                        for (idx, result) in enumerate(search_results):
                            # Parse the response object into string variables
                            title = result['title']
                            # From the array of authors, make a single semicolon-separated string
                            authors = '; '.join(
                                [x['name'] for x in result['publication_info']['authors'][:]])
                            # There is no actual property for the year, we need to
                            # awkwardly parse it from the publication info summary
                            # by using a regex search for what would likely be the year
                            regex = re.compile(r'.*, (\d{4}) - .*')
                            pub_year = re.match(regex,
                                                result['publication_info']['summary'])
                            pub_year = '' if pub_year is None else pub_year.groups(
                            )[-1]

                            # If the search result does not have an external link, the index
                            # will not be accessible, so add it to the object with an empty string as value
                            if (not ('link' in result)):
                                result['link'] = ''
                            # Generate the Google Scholar publication page link from the cluster ID value if available
                            g_scholar_link = f'https://scholar.google.com/scholar?cluster={result['inline_links']['versions']['cluster_id']}' \
                                if 'inline_links' in result and 'versions' in result['inline_links'] and 'cluster_id' in result['inline_links']['versions'] \
                                else ''
                            # Generate the number of citations from the respective property if available
                            num_citations = result['inline_links']['cited_by']['total'] \
                                if 'inline_links' in result and 'cited_by' in result['inline_links'] and 'total' in result['inline_links']['cited_by'] \
                                else 0

                            # Store the variables in the search results array
                            # using the global variables for the column names
                            results[start + idx] = {
                                global_vars.author_key: authors,
                                global_vars.pub_year_key: pub_year,
                                global_vars.title_key: title,
                                global_vars.scholar_link_key: g_scholar_link,
                                global_vars.pub_url_key: result['link'],
                                global_vars.gs_rank_key: start + result['position'],
                                global_vars.num_citations_key: num_citations
                            }

                            # If verbose logging was requested, provide constant information
                            if (verbose and (start + idx + 1) % 100 == 0 or idx + 1 == num_results and num_results < global_vars.default_serp_max_results):
                                print(f'{start + idx + 1} entries scraped')

                        # In the rare case that we ran out of search results before
                        # reaching our desired number of results, stop performing more queries
                        # by exiting the method
                        if idx + 1 < num_results:
                            return

                        # If we reach this point, the query was successful, so break from
                        # the for loop, since we do not need to attempt the process again
                        # and continue with the next batch
                        break
                # If there was an issue performing the query, inform the user and try again after 15 seconds
                except Exception as e:
                    print(f'\n{e}')
                    print(
                        f'\nThere was a problem scraping Google Scholar publications. Retrying in 15 seconds. Attempt {attempt + 1} of {global_vars.max_attempts}')
                    time.sleep(15)
                    continue
            # If we finished the for loop, we ran out of retry attempts. Inform the user and exit
            else:
                print(
                    'Too many failed attempts at scraping Google Scholar. Please check your API key and try again.')
                exit(500)

    # Run the method to process the queries
    _process_queries()

    # Remove any empty elements in the results array
    # (present if the search results obtained were fewer than the max desired)
    results = [x for x in results if x is not None]

    # Generate a timestamp string
    timestamp = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))
    # Clean out any non-alphanumeric characters in the query string to use as
    # part of the output CSV file path
    regex = re.compile('[^a-zA-Z]')
    output_file_path = p(base_output_dir /
                         f'{timestamp}_{regex.sub('', search_query.lower())[:15]}.csv')

    # Create this CSV file and save the results into it
    with open(str(output_file_path), 'w', newline='', encoding='utf-8') as csvfile:
        # Set the field names as defined in global variables
        fieldnames = [global_vars.author_key, global_vars.pub_year_key,
                      global_vars.title_key, global_vars.scholar_link_key, global_vars.pub_url_key, global_vars.gs_rank_key, global_vars.num_citations_key]
        # A new writer object to handle the writing of the file
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, delimiter=',')
        # Write the header of the CSV first
        writer.writeheader()
        # Write the results row-by-row
        for i in range(len(results)):
            writer.writerow(results[i])

    # Return the file path where we stored the results as a Path object
    return output_file_path
