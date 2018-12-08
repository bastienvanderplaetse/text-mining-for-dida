import urllib.request as req

import argparse
import json
import sys

import explorer_helper as exh
import ngrams_helper as ngh
import pubmed_helper as pbmdh
import utils
from pprint import pprint

CONFIG = None
LEGAL_EXT = ['txt', 'json']

def check_args(argv):
    parser = argparse.ArgumentParser(description="Prepares publications \
        for classification")
    parser.add_argument("FILE", type=str, help="the name of the file \
        containing PMIDs or publications at JSON format. \
        Can eventually containing the corresponding label")
    parser.add_argument('OUTPUT', type=str, help="the name of the output file (without extension)")
    parser.add_argument('CONFIG', type=str, help="the name of the configuration file (without extension)")
    # parser.add_argument("-s", "--skiprows", type=int, help="the number of rows to skip")
    #
    args = parser.parse_args()
    # if args.skiprows == None:
    #     args.skiprows = 27
    #     print(bcolors.WARNING + bcolors.BOLD + "No skiprows parameter in arguments. Value by default is {0}.".format(args.skiprows)  + bcolors.ENDC)
    #
    # print("The {0} first rows will be ignored.".format(args.skiprows))

    return args

def read_file(filename, extension):
    if extension == "txt":
        f = open(filename)
        lines = f.readlines()
        pmids = []
        for line in lines:
            pmids.append(line.replace('\n', ''))
        f.close()
        return pubtator_data(pmids)
    elif extension == "json":
        return exh.load_json(filename)

def pubtator_data(pmids_list):
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
            all_data.extend(response)
        return all_data

def run(args):
    global CONFIG
    CONFIG = exh.load_json('config/{0}.json'.format(args.CONFIG))
    extension = args.FILE.split('.')[-1]

    if extension in LEGAL_EXT:
        exh.create_directory('documents')
        documents_l = read_file(args.FILE, extension)
        exh.write_json(documents_l, 'documents/{0}.json'.format(args.OUTPUT+'-back'))
        docs, _ = pbmdh.extract_features(documents_l)
        ngh.extract_ngrams(docs, CONFIG['NGRAMS'])
        exh.write_json(docs, 'documents/{0}.json'.format(args.OUTPUT))
    else:
        utils.display_fail('Extension of input file not supported. Required : txt or json. Received : {0}'.format(extension))
        sys.exit(0)

if __name__=="__main__":
    args = check_args(sys.argv)
    run(args)
