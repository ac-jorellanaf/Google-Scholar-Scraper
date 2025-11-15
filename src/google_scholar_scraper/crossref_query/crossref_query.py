from habanero import Crossref
import pandas as pd
from google_scholar_scraper.config import global_vars
from time import sleep


def get_dois(filename, cr, verbose):
    df = pd.read_csv(str(filename), dtype=str)

    assert global_vars.author_key in df and global_vars.pub_year_key in df and global_vars.title_key in df

    if (not (global_vars.doi_key in df)):
        df[global_vars.doi_key] = ''
    dois = [None] * df[global_vars.author_key].size
    df.fillna('', inplace=True)

    for i in range(df[global_vars.author_key].size):
        if (df[global_vars.doi_key][i] == ''):
            for attempt in range(global_vars.max_attempts):
                try:
                    x = cr.works(query=str(str(df[global_vars.author_key][i]).replace(';', ',').replace('"', '').lower() + ' ' +
                                           str(df[global_vars.pub_year_key][i]) + ' "' + str(df[global_vars.title_key][i]).lower() + '"'), select='DOI', limit=1)
                    dois[i] = ('https://doi.org/' +
                               x['message']['items'][0]['DOI'])
                except Exception as e:
                    print(f'\n{e}')
                    print(
                        f'There was a problem obtaining the suggested DOI. Retrying in 15 seconds. Attempt {attempt + 1} of {global_vars.max_attempts}')
                    attempt = attempt + 1
                    sleep(15)

                break

            else:
                print(
                    'Too many failed attempts querying the suggested DOI. Please run the DOI program again.')
                df[global_vars.doi_key][:i + 1] = dois[:i + 1]
                df.to_csv(str(filename), index=False)
        else:
            dois[i] = df[global_vars.doi_key][i]

        if (((i + 1) % 10 == 0) or ((i + 1) == df[global_vars.author_key].size)):
            df[global_vars.doi_key][:i + 1] = dois[:i + 1]
            df.to_csv(str(filename), index=False)
            if (verbose):
                print(f'{i+1} DOIs processed.')


def crossref_query(email, verbose, output_files):
    cr = Crossref(mailto=email)
    if (verbose):
        print(
            f'\nNumber of files to process for suggested DOIs: {len(output_files)}')
    for output_file in output_files:
        if (verbose):
            print(f'Obtaining suggested DOIs for {output_file.name}')
        get_dois(output_file, cr, verbose)
