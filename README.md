# Text-mining for DIDA publications
Project realised in the context of my Scientific Research Trip in the [Machine Learning Group](http://mlg.ulb.ac.be/) at the Université Libre de Bruxelles.

[DIDA](http://dida.ibsquare.be/) is a novel database created by Andrea Gazzo and colleagues at [IB²](http://ibsquare.be/) in 2017. Its goal is to provide detailed information about digenic diseases, as well as as the variants and genes involved.

The main purpose of this work was to help to automate the update process of this database. Two essentials questions can be asked concerning the maintenance of DIDA :
1. *Which publications contain relevant information for DIDA?*
What are the important characteristics that differentiate relevant publications from the others? How can we identify and classify them?
2. *How to find publications relevant to evaluate the current information in DIDA ?*
How to extract information from publications ? How can we check if this information is not in contradiction with the data in DIDA? Does this new data provide additional proof for information already in DIDA?

This work had as objective the evaluation of intelligent approaches that could be used to solve the first question. Two studies were performed that provide answers :
1.  Investigating the relevance of Text Mining approaches.
2.  Using Question Answering systems to  evaluate the article relevance.

This repository is focused on Text Mining approaches.
Question Answering systems approach is available at : [https://github.com/bastienvanderplaetse/qas-for-dida](https://github.com/bastienvanderplaetse/qas-for-dida)

The explanations of the algorithms can be found in the report related to this project.

## 1. Data set preparation
The `PMIDS.txt`file contains the PMIDs of publications present in DIDA.
The first step is to download the publications from the NotDIDA class by running the following command :
```sh
$ python download.py PMIDS.txt config
```
A new file `not_dida.json` will be created in `documents` directory. This file contains the publications with their abstracts queried with [PubTator](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/guest2.cgi) NCIB tool. These publications are the ones queried with the word *digenic* and published between 1950 and 2017. The script automatically removes from this list the publications having their PMID in the `PMIDS.txt` file.

To extract n-grams for each publication in our data set, run the following commands :
```sh
$ python prepare.py PMIDS.txt dida config
$ python prepare.py not_dida.json not_dida config
```
The first one will download each publication having its PMID in the `PMIDS.txt` file and will saved them into `documents/dida-back.json`. After that, it will extract the n-grams of the publication abstract and saved them into `documents/dida.json`. The second one will make a backup of the abstract publication for NotDIDA class by saving them into `documents/not_dida-back.json` and the file containing their n-grams will be saved into `documents/not_dida.json`.

NOTE : do not remove `dida-back.json` and `not_dida-back.json` files if you intend to execute the Top-20 analysis.

## 2. Top-20 grams analysis
To execute the Top-20 grams analysis, run the following command :
```sh
python topwords.py config
```
The results will be saved into the `topwords` directory.
For the Top-20 grams, a file will be created at each iteration of the process in order to check which grams was present in the current list and which ones were used as stop words or blacklisted grams.
For the *strict* Top-20, only one file per type of n-grams will be created.

## 3. Minimum Set Cover
To execute the resolution of the Minimum Set Cover problem approach, run the following command :
```sh
python coverwords.py config
```
The results will be saved into the `coverwords` directory.

## 4. Words distribution analysis
To execute the resolution of the words distribution analysis, run the following command :
```sh
python wordsdistribution.py config
```
The results will be saved into the `wordsdistribution` directory. The CSV files contain the ratio of each gram in each class and their `V` score.
If you want to evaluate our classification models based on the words distribution analysis, run the following command :
```sh
python wordsdistribution_classification.py config
```
The results will be saved into the `wordsdistribution` directory. The JSON files contain the exact values of the confusion matrix and F-score for each model. Plots to check the evolution of these values will be saved in the same directory.

## 5. Words clustering analisys
To execute the resolution of the words clustering analysis, run the following command :
```sh
python wordsclustering.py config
```
The results will be saved into the `wordsclustering` directory. All the data required by the Naive Bayes classifier will be stored in `didaclusters`. It contains the list of the words present in the data set (`W.json`), their number of occurrences in each publication (`ndw.json`) and the list of all clusters constructed by the Agglomerative IB method.
If you want to evaluate our classification model, run the following command :
```sh
python wordsclustering_classification.py config
```
The results will be saved into the `wordsclustering` directory. The JSON files contain the exact values of the confusion matrix and F-score for each converter. Plots to check the evolution of these values will be saved in the same directory.

## 6. Configuration
The different parameters used in this project can be changed through a configuration file. In our previous commands, we used the same parameter `config`. This parameter references the `config.json` file stored in `config` directory.
User can change parameters in this file or create a new one. If he creates a new configuration file, the previous commands should be run by replacing `config` parameter with the name of the new configuration file (without its extension).

The parameters that can be changed are :
- `NGRAMS` : the maximum length of n-grams that should be used.
- `DIDA_DOCS` : the name of the first class (here we used "dida"). This parameter is used in many result namefiles.
- `NOTDIDA_DOCS` : the name of the second class (here we used "not_dida"). This parameter is used in many result namefiles.
- `START_YEAR` : used by the `download.py` script, corresponds to the year of publication for the oldest publications we want to use.
- `SPLIT_YEAR` : used by the `download.py` script, corresponds to the year of publication for the newest publications we want to use.
- `NTOPWORDS` : the maximum size of the top grams list (here we limit the list to 20 for Top-20 grams analysis)
- `TETA_COVERWORDS` : defines the threshold in MSC problem to determine which n-grams should be used to solve MSC. The threshold is defined by `M * TETA_COVERWORDS` where `M` is the highest ratio of the corresponding list. Here we used 0.5 to choose the half.
- `WORDS_DISTRIBUTION_MAX_THRESHOLD` : the words distribution based classifiers are evaluated for many theta threshold. This parameters determines the maximum value of this threshold.
- `WORDS_DISTRIBUTION_STEP_THRESHOLD` : determines the step of decreasing the theta threshold used by words distribution based classifiers.
- `CLUSTERING_CLASSES` : list of class names used for the words clustering.
- `ALL_CLUSTERS_DIRECTORY` : name of the directory created in `wordsclustering` directory. This directory will contain the clusters obtained by the Agglomerative IB method, the `ndw.json`and `W.json` files.
