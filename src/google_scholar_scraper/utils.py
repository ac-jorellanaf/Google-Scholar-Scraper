import time
from pathlib import Path as p
import pandas as pd
import csv
from google_scholar_scraper.config import global_vars


def parse_queries(query_string, max_results, query_file):
    """Parse the queries for the searches"""

    # If the query_string is set, use that rather than a file
    if (query_string and query_string.strip()):
        return [(query_string, max_results)]
    # Otherwise, create an empty array of queries
    else:
        parsed_queries = []
        # Open the query file to use as a csvfile
        with open(query_file.strip(), 'r', newline='') as csvfile:

            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(csvfile.read(1024))
            csvfile.seek(0)
            # Create a CSV reader object
            reader = csv.reader(
                csvfile, delimiter=',', skipinitialspace=True)
            if has_header:
                next(reader)

            # Iterate through each row
            for row in reader:
                # Check if the row is not either empty or starts with a pound sign (#)
                if (row[0].strip() and row[0].strip()[0] != '#'):
                    # Set the query's max results to the default for now
                    query_max_results = max_results
                    # If soe, store the query into a variable
                    query = row[0].strip()
                    # If the number of maximum search results for the query was specified
                    if (len(row) > 1):
                        # Try to convert it to an int
                        try:
                            query_max_results = int(row[1].strip())
                            try:
                                assert query_max_results > 0
                            except AssertionError:
                                print(
                                    f'\nWarning: Maximum results must be greater than 0. Current value = "{query_max_results}"')
                        # Or throw a warning if it cannot be converted to an integer and continue to the next row
                        except Exception:
                            print(
                                f'\nWarning: There was a problem reading the maximum number of results ("{query_max_results}") for query "{query}". ' +
                                'This query will be ignored and the program will continue, or press Ctrl+C to cancel the search and try again.')
                            continue
                    # If there was no error, add the query and the max results
                    # to get from it to our array of parsed queries
                    parsed_queries.append((query, query_max_results))
        # Return the array of parsed queries
        return parsed_queries


def merge_search(output_files, output_dir, verbose):
    """Merge the various files from each individual query into a single file"""
    # Initialise an empty array of Pandas dataframes
    dfs = [None] * len(output_files)
    # If we want verbose logging, print out the files we're merging
    if (verbose):
        print(f'\nMerging {len(output_files)} .csv files.')
    # Iterate through our files in the output directory
    for (idx, filename) in enumerate(output_files):
        # Read the CSV as a dataframe and append it to our array
        df = pd.read_csv(str(filename), dtype=str)
        dfs[idx] = (df)

    # Merge our dataframes and store them in full_df
    full_df = pd.concat(dfs, ignore_index=True, keys=None, sort=False)
    # Remove any duplicates if they have the same authors, publication year, and title
    merged_df = pd.DataFrame.drop_duplicates(
        full_df, subset=[global_vars.author_key, global_vars.pub_year_key, global_vars.title_key], ignore_index=True)

    # Get the current timestamp
    timestamp = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))

    # Define the output file path
    output_file_path = p(output_dir / f'merged_{timestamp}.csv')

    # convert the merged dataframe to a CSV and store it in the output file path location
    merged_df.to_csv(str(output_file_path), index=False)

    # If verbose, signal completion
    if (verbose):
        print(f'\nMerging complete: file {str(output_file_path)} saved.')
