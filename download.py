"""Download PubMed publications

This script allows the user to download PubMed publications between two
particular dates (see configuration files). The downloaded publications will be
the ones that are not already present in DIDA.

The script can be run through the following command :
`python download.py DIDA CONFIG`
where `DIDA` is a .txt file containing the list of the PMIDs of DIDA
publications
and `CONFIG` is the name of the configuration file situated in the `config`
folder (without the extension).
"""

import argparse
import numpy as np
import sys

import display
import explorer_helper as exh
import pubmed_helper as pbmdh

CONFIG = None



""" CONFIGURATION """

def check_args(argv):
    """Checks and parses the arguments of the command typed by the user

    Parameters
    ----------
    argv :
        The arguments of the command typed by the user

    Returns
    -------
    ArgumentParser
        the values of the arguments of the commande typed by the user
    """
    parser = argparse.ArgumentParser(description="Downloads Pubmed publications about digenic diseases.")
    parser.add_argument('DIDA', type=str, help="the file name containing the list of pmids present in DIDA")
    parser.add_argument('CONFIG', type=str, help="the name of the configuration file (without extension)")

    args = parser.parse_args()

    return args



""" FUNCTIONS """

def download_doc(pmids_list):
    """Downloads publications based on a PMIDs list and saves them into a
    JSON file

    Parameters
    ----------
    pmids_list : list
        The list containing the PMIDs of the publications to download
    """
    print("Downloading PMIDs for Not-DIDA")
    all_data = pbmdh.download_publications(pmids_list)
    filename = CONFIG['NOTDIDA_DOCS'] + ".json"
    exh.write_json(all_data, filename)
    display.display_info("Not-DIDA publications saved in {0}".format(filename))

def filter(pmids, known_pmids):
    """Filters from new PMIDs the ones that are already in DIDA

    Parameters
    ----------
    pmids : list
        The list of new PMIDs
    known_pmids : list
        The list of PMIDs already in DIDA

    Returns
    -------
    list
        the list of PMIDs that are not in DIDA
    """
    print("Filtering PMIDs.")
    notdida = []
    for pmid in pmids:
        if not pmid in known_pmids:
            notdida.append(pmid)
    display.display_ok("Filtering PMIDs done.")
    return notdida

def get_dida_pmids(dida_pmids):
    """Gets the PMIDs of publications in DIDA from a text file

    Parameters
    ----------
    dida_pmids : str
        The file name of the file containing the PMIDs in DIDA

    Returns
    -------
    list
        the list of PMIDs of publications in DIDA
    """
    print("Retrieving PMIDs from {0}".format(dida_pmids))
    f = open(dida_pmids)
    lines = f.readlines()
    pmids = []
    for index, line in enumerate(lines):
        pmids.append(line.replace('\n', ''))
    f.close()
    display.display_ok("Retrieving PMIDs done. {0} PMIDs found".format(len(pmids)))
    return pmids

def get_pmids_by_dates():
    """Gets the PMIDs of publications between the dates specified in the configuration file

    Returns
    -------
    list
        the list of the PMIDs of the found publications
    """
    start_year = CONFIG['START_YEAR']
    end_year = CONFIG['SPLIT_YEAR']
    print("Retrieving new PMIDs between {0} and {1}".format(start_year, end_year))

    ids = []
    query = "digenic+AND+{0}[pdat]"
    for year in range(start_year, end_year):
        ids.extend(pbmdh.get_pmids(query.format(year)))

    x = np.array(ids)
    x = list(np.unique(x))
    display.display_ok("{0} new PMIDs found".format(len(x)))
    return x



""" EXECUTION """

def run(dida_pmids):
    """Executes the main process of the script

    Parameters
    ----------
    dida_pmids : str
        The file name of the file containing the PMIDs in DIDA
    """
    global CONFIG
    # Load configuration
    CONFIG = exh.load_json("config/{0}.json".format(args.CONFIG))

    # Get DIDA PMIDs
    known_pmids = get_dida_pmids(dida_pmids)
    # Get Not-DIDA PMIDs
    pmids = get_pmids_by_dates()
    notdida_pmids = filter(pmids, known_pmids)

    display.display_info("Total PMIDs between {0} and {1} : {2}".format(CONFIG['START_YEAR'], CONFIG['SPLIT_YEAR'], len(pmids)))
    display.display_info("Total PMIDs in DIDA : {0}".format(len(known_pmids)))
    display.display_info("Total PMIDs in Not-DIDA : {0}".format(len(notdida_pmids)))

    # Download Not-DIDA publications
    download_doc(notdida_pmids)

if __name__=="__main__":
    args = check_args(sys.argv)
    run(args.DIDA)
