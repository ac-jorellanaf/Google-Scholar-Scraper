import csv
import time
import re
from pathlib import Path as p
from google_scholar_scraper.config import global_vars
from urllib import request, parse
import json
import math
from sys import exit


def scrape_google_scholar(serp_api_key, search_query, max_entries, base_output_dir, verbose):
    entries = [None] * max_entries

    for i in range(math.ceil(max_entries / 20)):
        start = i * 20
        num_results = min(max_entries - start, 20)
        for attempt in range(global_vars.max_attempts):
            try:
                clean_query = parse.quote_plus(search_query)
                url = f'https://serpapi.com/search?engine=google_scholar&api_key={serp_api_key}' +\
                    f'&start={start}&num={num_results}&q={clean_query}'
                with request.urlopen(url) as response:
                    search_results = json.loads(response.read())
                    search_results = search_results['organic_results']
                    for (idx, entry) in enumerate(search_results):
                        title = entry['title']
                        authors = '; '.join(
                            [x['name'] for x in entry['publication_info']['authors'][:]])
                        regex = re.compile(r'.*, (\d{4}) - .*')
                        pub_year = re.match(regex,
                                            entry['publication_info']['summary'])
                        pub_year = '' if pub_year is None else pub_year.groups(
                        )[-1]
                        if (not ('link' in entry)):
                            entry['link'] = ''
                        g_scholar_link = f'https://scholar.google.com/scholar?cluster={entry['inline_links']['versions']['cluster_id']}' \
                            if 'inline_links' in entry and 'versions' in entry['inline_links'] and 'cluster_id' in entry['inline_links']['versions'] \
                            else ''
                        num_citations = entry['inline_links']['cited_by']['total'] \
                            if 'inline_links' in entry and 'cited_by' in entry['inline_links'] and 'total' in entry['inline_links']['cited_by'] \
                            else 0

                        entries[start + idx] = {
                            global_vars.author_key: authors,
                            global_vars.pub_year_key: pub_year,
                            global_vars.title_key: title,
                            global_vars.scholar_link_key: g_scholar_link,
                            global_vars.pub_url_key: entry['link'],
                            global_vars.gs_rank_key: start + entry['position'],
                            global_vars.num_citations_key: num_citations
                        }

                        if (verbose and (start + idx + 1) % 100 == 0 or idx + 1 == num_results and num_results < 20):
                            print(f'{start + idx + 1} entries scraped')

                    break
            except Exception as e:
                print(f'\n{e}')
                print(
                    f'\nThere was a problem scraping Google Scholar publications. Retrying in 15 seconds. Attempt {attempt + 1} of {global_vars.max_attempts}')
                attempt = attempt + 1
                time.sleep(15)
        else:
            print(
                'Too many failed attempts at scraping Google Scholar. Please check your API key and try again.')
            exit(500)

    entries = [x for x in entries if x is not None]

    timestamp = time.strftime('%Y-%m-%dT%H%M%S', time.localtime(time.time()))
    regex = re.compile('[^a-zA-Z]')
    output_file_path = p(base_output_dir /
                         f'{timestamp}_{regex.sub('', search_query.lower())[:15]}.csv')

    with open(str(output_file_path), 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [global_vars.author_key, global_vars.pub_year_key,
                      global_vars.title_key, global_vars.scholar_link_key, global_vars.pub_url_key, global_vars.gs_rank_key, global_vars.num_citations_key]
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for i in range(len(entries)):
            writer.writerow(entries[i])

    return output_file_path
