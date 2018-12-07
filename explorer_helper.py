import os
import json
import csv

def create_directory(dir_name):
    if not os.path.exists(dir_name) or not os.path.isdir(dir_name):
            os.mkdir(dir_name)

def load_json(filename):
    with open(filename, 'r') as f:
        content = json.load(f)
    return content

def write_json(data, filename):
    with open(filename, 'w') as fp:
        json.dump(data, fp)

def write_csv(filename, data, cols):
    with open(filename,'w') as out:
        csv_out=csv.writer(out)
        csv_out.writerow(cols)
        csv_out.writerows(data)
