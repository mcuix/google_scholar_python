#! /usr/bin/env python
import datetime
import argparse
import scholar
import time
import sys

PAGE_RESULT = 10

parser = argparse.ArgumentParser(description='Wrapper for scholar.py')
parser.add_argument('-p', '--phrase', dest='phrase')
parser.add_argument('--after', type=int, dest='after')
parser.add_argument('--no-citations', action='store_true', default=False, dest='citations',
                 help='Do not include citations in results')
parser.add_argument('--no-patents', action='store_true', default=False, dest='patents',
                 help='Do not include patents in results')
parser.add_argument('-n', '--num-results', type=int, default=10, dest='num_results',
                 help='Number of Total Results (multiple of ten)')
parser.add_argument('--csv-header', action='store_true', default=False, dest='header',
                 help='Include a header separated by |')
parser.add_argument('-s', '--save', action='store_true', default=False, dest='save')
################### HAVE NOT TESTED ##############################################################
parser.add_argument('-C', '--cluster-id', metavar='CLUSTER_ID', default=None, dest='cluster_id',##
                 help='Do not search, just use articles in given cluster ID')                   ##
################### HAVE NOT TESTED ##############################################################

args = parser.parse_args()
start_idx = 0
num_results = args.num_results
all_articles = []


while num_results - PAGE_RESULT >= 0:
    print('working on results', start_idx, 'through', start_idx + PAGE_RESULT,  '...')
    if args.cluster_id:
        query = scholar.ClusterScholarQuery(cluster=args.cluster_id)
    else:
        query = scholar.SearchScholarQuery()

    query.set_num_page_results(PAGE_RESULT)
    query.set_phrase(args.phrase)
    query.set_timeframe(args.after, None)
    query.set_include_citations(not args.citations)
    query.set_include_patents(not args.patents)
    query.set_start(start_idx)


    querier = scholar.ScholarQuerier()
    querier.send_query(query)

    #either no query results or the robot checker is blocking the IP ADDR / USER_AGENT
    if not querier.articles:
        break

    for art in querier.articles:
        all_articles.append(art)

    start_idx   += PAGE_RESULT
    num_results -= PAGE_RESULT
    ### For Robot Checking
    time.sleep(15)



if all_articles:
    header = args.header
    if args.save:
        fname = 'response_' + datetime.datetime.now().strftime('%H%M') + '.txt'
        fin = open(fname, 'w')
        for art in all_articles:
            result = art.as_csv(header=header, sep='|')
            header = False
            fin.write(scholar.encode(result) + '\n')
        fin.close()
        print("Results saved to", fname)
    else:
        for art in all_articles:
            result = art.as_csv(header=header, sep='|')
            header = False
            print(scholar.encode(result) + '\n')
else:
    print('This run did not produce any results from Google Scholar.')
