from habanero import Crossref
import pandas as pd
from google_scholar_scraper.config import global_vars
from time import sleep


def _get_dois(file_path, cr, verbose):
    """Hadnler for obtaining the DOIs of the publications obtained from the scraping"""
    # Read the CSV of search results and store it as a Pandas data frame
    df = pd.read_csv(str(file_path), dtype=str)

    # Check that the right field headers are present
    try:
        assert global_vars.author_key in df and global_vars.pub_year_key in df and global_vars.title_key in df
    # If they are not, raise an error and exit the handling of this file
    except AssertionError:
        print(
            f'\nError: Header for file {file_path.name} does not match expected header for Google Scholar Scraper search results file. Skipping file.')
        return

    # If the column for DOIs still does not exist
    if (not (global_vars.doi_key in df)):
        # Create a new column for the DOIs and fill it with empty strings
        df[global_vars.doi_key] = ''

    # Pre-allocate our array of DOIs to the number of entries in our search results
    dois = [''] * df[global_vars.author_key].size

    # Fill any missing values with empty strings and store it in the same dataframe
    df.fillna('', inplace=True)

    # Loop through all the entries in the CSV file
    for i in range(df[global_vars.author_key].size):
        # If the DOI is empty, then perform the CrossRef query
        if (df[global_vars.doi_key][i] == ''):
            # Attempt the query as many times as we have set
            for attempt in range(global_vars.max_attempts):
                # Try to query the API
                try:
                    # Build the query string from the authors, year, and title
                    query = f'{str(df[global_vars.author_key][i]).replace(";", ",").replace("\"", "").lower()} ' +\
                        f'{str(df[global_vars.pub_year_key][i])} "{str(df[global_vars.title_key][i]).lower()}"'
                    # Obtain only the first result
                    x = cr.works(query=query, select='DOI', limit=1)
                    # Store the found DOI in our array
                    dois[i] = ('https://doi.org/' +
                               x['message']['items'][0]['DOI'])
                # If there was an issue performing the query, inform the user and try again after 15 seconds
                except Exception as e:
                    print(f'\n{e}')
                    print(
                        f'Error: There was a problem obtaining a DOI. Retrying in 15 seconds. Attempt {attempt + 1} of {global_vars.max_attempts}')
                    sleep(15)
                    continue

                # If we reach this point, the query was successful, so break from
                # the for loop, since we do not need to attempt the process again
                # and continue with the next entry
                break

            # If we finished the for loop, we ran out of retry attempts.
            # Inform the user and save the currently obtained DOIs.
            else:
                print(
                    f'Error: Too many failed attempts querying DOIs for file {file_path.name}. Saving current progress. Please run the program in DOI-only mode again to resume from this point.')
                # The DOIs before the one we encountered the error will be stored
                # in the data frame and saved to the CSV file.
                df[global_vars.doi_key][:i] = dois[:i]
                df.to_csv(str(file_path), index=False)
                return
        # If the DOI already exists in the file, use that value
        else:
            dois[i] = df[global_vars.doi_key][i]

        # Progressively save the output file in case of issues, since these requests
        # can take a long time. Done every 10 DOI searches, or when all searches are done
        if (((i + 1) % 10 == 0) or ((i + 1) == df[global_vars.author_key].size)):
            # Store all the found DOIs in our array to the dataframe
            df[global_vars.doi_key][:i + 1] = dois[:i + 1]
            # Save the dataframe to the CSV file
            df.to_csv(str(file_path), index=False)

            # If verbose logging was requested, provide feedback on progress
            if (verbose):
                print(f'{i+1} DOIs processed.')


def crossref_query(email, verbose, output_files):
    """Handler for performing the CrossRef queries to obtain the DOIs"""
    # Initialise a new habanero CrossRef class with the user-provided email
    cr = Crossref(mailto=email)
    # If verbose logging is enabled, provide feedback
    if (verbose):
        print(
            f'\nNumber of files to process for suggested DOIs: {len(output_files)}')
    # Loop through all the files with search results in our file list
    for output_file in output_files:
        # If verbose logging is enabled, provide feedback
        if (verbose):
            print(f'Obtaining suggested DOIs for {output_file.name}')
        # Perform the queries to get the DOIs
        _get_dois(output_file, cr, verbose)
