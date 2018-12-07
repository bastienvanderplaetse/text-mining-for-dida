import sys
import argparse
import datetime
import urllib.request as req
import xml.etree.ElementTree as ET
import numpy as np
from copy import deepcopy
import json
from pprint import pprint

START_YEAR = 1950
URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={0}&retmax={1}"

def check_args(argv):
    parser = argparse.ArgumentParser(description="Downloads Pubmed publications about digenic diseases.")
    parser.add_argument("DIDA", type=str, help="the file name containing the list of pmids present in DIDA")
    parser.add_argument('OUTPUT', type=str, help="the name of the output file (without extension)")
    parser.add_argument("-s", "--splityear", type=int, help="the frontier year between old and new publications")

    args = parser.parse_args()

    if args.splityear == None:
        args.splityear = 2016

    return args

def get_pmids(query="digenic", retmax=1000):
    resp = req.urlopen(URL.format(query,retmax)).read().decode('utf-8')
    root = ET.fromstring(resp)
    pmids = root.find('IdList').getchildren()
    for i in range(len(pmids)):
        pmids[i] = pmids[i].text
    # for pmid in pmids:
    #     pmid =pmid.text
    return pmids


def get_pmids_by_dates(start_year, end_year):
    ids = []
    query="digenic+AND+{0}[pdat]"
    for year in range(start_year, end_year):
        ids.extend(get_pmids(query.format(year)))

    x = np.array(ids)
    return list(np.unique(x))

def get_dida_pmids(dida_pmids):
    f = open(dida_pmids)
    lines = f.readlines()
    pmids = []
    for line in lines:
        pmids.append(line.replace('\n', ''))
    f.close()
    return pmids

def filter(pmids, known_pmids):
    notdida = []
    for pmid in pmids:
        if not pmid in known_pmids:
            notdida.append(pmid)
    return notdida

def save_to_json(data, filename):
    with open(filename, 'w') as fp:
        json.dump(data, fp)

def download_doc(pmids_list, filename):
    all_data = []

    stepsize = 50
    for i in range(0, len(pmids_list), stepsize):
        subset = pmids_list[i:i + stepsize]
        pmids = ""
        for id in subset[:-1]:
            pmids += id + ','
        pmids += subset[-1]
        # print(pmids)
        url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/{0}/JSON/".format(pmids)
        response = req.urlopen(url).read().decode('utf-8')
        response = json.loads(response)
        all_data.extend(deepcopy(response))

    save_to_json(all_data, filename)

def run(dida_pmids, split_year):
    known_pmids = get_dida_pmids(dida_pmids)
    pmids = get_pmids_by_dates(START_YEAR, datetime.datetime.now().year-1)

    notdida_pmids = filter(pmids, known_pmids)
    print("Total digenic : " + str(len(pmids)) + " / DIDA : " + str(len(known_pmids)) + " / Not DIDA : " + str(len(notdida_pmids)))
    download_doc(notdida_pmids, args.OUTPUT+'.json')

if __name__=="__main__":
    args = check_args(sys.argv)
    run(args.DIDA, args.splityear)
