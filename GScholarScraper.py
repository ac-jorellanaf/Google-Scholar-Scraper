from habanero import Crossref
from scholarly import scholarly
import argparse
import csv
from pathlib import Path
import pandas as pd
import re
import time


def main(args):
    AUTHOR_KEY = 'AUTHOR'
    PUB_YEAR_KEY = 'PUB_YEAR'
    TITLE_KEY = 'TITLE'
    SCHOLAR_LINK_KEY = 'SCHOLAR_LINK'
    PUB_URL_KEY = 'PUB_URL'
    GSRANK_KEY = 'GSRANK'
    NUM_CITATIONS_KEY = 'NUM_CITATIONS'
    DOI_KEY = 'SUGGESTED_DOI'
    NUM_ATTEMPTS = 10

    def scrapeGS(query, numentries, outdir, verbose):
        DEFENTRIES = 20

        if (not numentries or not numentries.strip()):
            numentries = DEFENTRIES
        numentries = int(numentries)

        assert numentries > 0

        for attempt in range(NUM_ATTEMPTS):
            try:
                search_query = scholarly.search_pubs(query, patents=False)
            except Exception as e:
                print('\n{}'.format(e))
                print(
                    'There was a problem scraping Google Scholar publications. Retrying in 15 seconds. Attempt {}/{}'.format(attempt + 1, NUM_ATTEMPTS))
                attempt = attempt + 1
                time.sleep(15)
            else:
                break
        else:
            print(
                'Too many failed attempts at scraping Google Scholar. Please run the program again.')

        entries = [dict() for x in range(numentries)]
        attempt = 0
        for i in range(numentries):
            for attempt in range(NUM_ATTEMPTS):
                try:
                    entrydict = next(search_query)
                    # entry = next(search_query)
                    # entrydict = scholarly.fill(entry)
                    authors = re.sub(r'[\[\]\']', '', str(
                        entrydict['bib'][AUTHOR_KEY.lower()]).replace(',', ';'))
                    pubyear = str(entrydict['bib'][PUB_YEAR_KEY.lower()])
                    title = str(entrydict['bib'][TITLE_KEY.lower()])
                    if (not ('pub_url' in entrydict)):
                        entrydict['pub_url'] = ''

                    entries[i] = {
                        AUTHOR_KEY: authors,
                        PUB_YEAR_KEY: pubyear,
                        TITLE_KEY: title,
                        SCHOLAR_LINK_KEY: 'https://scholar.google.com' + entrydict['url_scholarbib'].replace('q=info:', 'cluster=').replace(':scholar.google.com/&output=cite&scirp=' + str(i), ''),
                        PUB_URL_KEY: str(entrydict[PUB_URL_KEY.lower()]),
                        GSRANK_KEY: str(entrydict[GSRANK_KEY.lower()]),
                        NUM_CITATIONS_KEY: str(
                            entrydict[NUM_CITATIONS_KEY.lower()])
                    }

                    if (verbose and (i + 1) % 100 == 0 or (i + 1) == numentries):
                        print('{} entries scraped'.format(i + 1))
                except Exception as e:
                    print('\n{}'.format(e))
                    print(
                        'There was a problem scraping a Google Scholar entry. Retrying. Attempt {}/{}'.format(attempt + 1, NUM_ATTEMPTS))
                    attempt = attempt + 1
                    time.sleep(1)
                else:
                    break
            else:
                print(
                    'Too many failed attempts at scraping Google Scholar. Please run the program again.')
                quit()

        date = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))
        regex = re.compile('[^a-zA-Z]')
        outfile = Path(outdir / (date + '_' +
                                  regex.sub('', query.lower())[:15] + '.csv'))

        with open(str(outfile), 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [AUTHOR_KEY, PUB_YEAR_KEY,
                          TITLE_KEY, SCHOLAR_LINK_KEY, PUB_URL_KEY, GSRANK_KEY, NUM_CITATIONS_KEY]
            writer = csv.DictWriter(
                csvfile, fieldnames=fieldnames, delimiter=',')
            writer.writeheader()
            for i in range(numentries):
                writer.writerow(entries[i])
            # bibtxt.append(entrydict['bib']tex)

        return outfile

    def getDOIs(filename, cr, verbose):
        df = pd.read_csv(str(filename), dtype=str)

        assert AUTHOR_KEY in df and PUB_YEAR_KEY in df and TITLE_KEY in df

        if (not (DOI_KEY in df)):
            df[DOI_KEY] = ''
        dois = []
        df.fillna('', inplace=True, downcast=str)

        for i in range(df[AUTHOR_KEY].size):
            if (not df[DOI_KEY][i]):
                attempt = 0
                for attempt in range(NUM_ATTEMPTS):
                    try:
                        x = cr.works(query=str(str(df[AUTHOR_KEY][i]).replace(';', ',').replace('"', '').lower() + ' ' +
                                               str(df[PUB_YEAR_KEY][i]) + ' "' + str(df[TITLE_KEY][i]).lower() + '"'), select='DOI', limit=1)
                        dois.append('https://doi.org/' +
                                    x['message']['items'][0]['DOI'])
                    except Exception as e:
                        print('\n{}'.format(e))
                        print(
                            'There was a problem obtaining the suggested DOI. Retrying in 15 seconds. Attempt {}/{}'.format(attempt + 1, NUM_ATTEMPTS))
                        attempt = attempt + 1
                        time.sleep(15)
                    else:
                        break
                else:
                    print(
                        'Too many failed attempts querying the suggested DOI. Please run the DOI program again.')
                    df[DOI_KEY][:i + 1] = dois[:i + 1]
                    df.to_csv(str(filename), index=False)
            else:
                dois.append(df[DOI_KEY][i])

            if (((i + 1) % 10 == 0) or ((i + 1) == df[AUTHOR_KEY].size)):
                df[DOI_KEY][:i + 1] = dois[:i + 1]
                df.to_csv(str(filename), index=False)
                if (verbose):
                    print('{} DOIs processed.'.format(i + 1))

    def mergeSearch(filenames, outdir, verbose):
        dfs = []
        if (verbose):
            print('\nMerging {} csv files.'.format(len(filenames)))
        for filename in filenames:
            df = pd.read_csv(str(filename), dtype=str)
            dfs.append(df)

        fulldf = pd.concat(dfs, ignore_index=True, keys=None, sort=False)
        mergeddf = pd.DataFrame.drop_duplicates(
            fulldf, subset=[AUTHOR_KEY, PUB_YEAR_KEY, TITLE_KEY], ignore_index=True)

        date = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))

        outfile = Path(outdir / ('merged_' + date + '.csv'))

        mergeddf.to_csv(str(outfile), index=False)
        
        if (verbose):
            print('\nMerging complete: {}.'.format(outfile))

    def processQueries(querystr, numentries, queryfile):
        if (querystr and querystr.strip()):
            return [[querystr, numentries]]
        else:
            queries = []
            with open(queryfile.strip()) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                for row in reader:
                    if (row['QUERY'].strip()[0] != '#'):
                        queries.append([row['QUERY'], row['NUMENTRIES']])
            return queries

    def scrapeWrapper(email, querystr=None, queryfile='queries.csv', numentries=None,
                      outdir=None, nomerge=False, nodoi=False, getdoi=None, verbose=False):
        if (not getdoi):
            queries = processQueries(querystr, numentries, queryfile)
            outfiles = []

            if (verbose):
                print('Google Scholar Scraper.')
                print('\nNumber of queries: {}'.format(len(queries)))
                print('\nQueries processed:')
                for [query, nentries] in queries:
                    print('query: {} - {} entries.'.format(query, nentries))

            if (not outdir):
                date = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))
                outdir = Path('entries/' + date)
                outdir.mkdir(exist_ok=True)
                if (verbose):
                    print('\nOutput path: {}'.format(outdir))

            for query, numentries in queries:
                if (verbose):
                    print('\nStarting GS scrape: {}'.format(query))
                outfiles.append(
                    scrapeGS(query, numentries, outdir, verbose))
        else:
            if (Path(getdoi).is_file()):
                outfiles = [Path(getdoi)]
            elif (Path(getdoi).is_dir):
                outfiles = [x for x in Path(getdoi).iterdir() if x.is_file()]

        cr = Crossref(mailto=email)
        if (not nodoi):
            if (verbose):
                print('\nNumber of files to process for suggested DOIs: {}'.format(
                    len(outfiles)))
            for outfile in outfiles:
                if (verbose):
                    print('Obtaining suggested DOIs for {}'.format(outfile.name))
                getDOIs(outfile, cr, verbose)

        if (not nomerge and len(outfiles) > 1):
            mergeSearch(outfiles, outdir, verbose)

    scrapeWrapper(args.email, args.querystr, args.queryfile, args.numentries,
                  args.outdir, args.nomerge, args.nodoi, args.getdoi, args.verbose)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scrape Google Scholar entries by keywords.')
    parser.add_argument(
        'email', help='For faster Crossref API queries, we require an e-mail address')
    querygroup = parser.add_mutually_exclusive_group()
    querygroup.add_argument('-q', '--querystr',
                            help='Set a custom in-line query, rather than use a query file.')
    querygroup.add_argument('-f', '--queryfile',
                            help='Set a custom filepath for a .csv file of entries to scrape, rather than use the queries.csv file.', default='queries.csv')
    parser.add_argument('-e', '--numentries',
                        help='Set a custom in-line number of entries to scrape, rather than use the queries.csv file.')
    parser.add_argument('-o', '--outdir',
                        help='Set a custom path for the directory where the search .CSV files should be stored.')
    parser.add_argument('-m', '--nomerge',
                        help='Do not merge the .CSV files after searching.', default=False)
    doigroup = parser.add_mutually_exclusive_group()
    doigroup.add_argument('-n', '--nodoi',
                          help='Do not scrape CrossRef for DOIs after the search.', default=False)
    doigroup.add_argument('-d', '--getdoi',
                          help='Set a directory or file of GS searches for which to find the suggested entry DOIs. Combineable with --nomerge.')
    parser.add_argument('-v', '--verbose',
                        help='Verbose mode.')
    args = parser.parse_args()

    main(args)
