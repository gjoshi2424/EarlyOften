import pathlib
import csv
import logging
import sys
import os

out = logging.getLogger()
VERSION = 'v2019.08.30'


def setup_logging(out_dir):
    if out.hasHandlers():
        return
    print("Setting up logger...")
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    file_handler = logging.FileHandler(os.path.join(out_dir, "log.txt"))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    out.addHandler(file_handler)
    out.addHandler(stream_handler)
    out.setLevel(logging.DEBUG)
    out.info("Logger initialized for version: " + VERSION)


setup_logging("out")


def check_attributes(main_table, attributes):
    # Check whether the dataset has required attributes, if not, warnings:
    for required_attr in attributes:
        if not isinstance(required_attr, list):
            required_attr = [required_attr]
        has = False
        for attr in required_attr:
            if attr in main_table:
                has = True
        if not has:
            out.warning("One of the following attributes is required: %s!" % required_attr)
            return False
    return True


def write_metric_map(name, metric_map, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf8') as file:
        writer = csv.DictWriter(file, fieldnames=["SubjectID", name], lineterminator='\n')
        writer.writeheader()
        for subject_id, value in sorted(metric_map.items()):
            writer.writerow({"SubjectID": subject_id, name: value})

def write_git_metrics(name, metric_map, path):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    metric_map.to_csv(path, encoding='utf-8', index=False, sep=' ')

def calculate_metric(main_table, metric_used, codeState_table):
    out.info("Calculating early and often metric")
    list_of_subjects = set(main_table["SubjectID"])
    map_score = {}
    dropped_metrics = 0
    for subject in list_of_subjects:
        current_events = main_table[main_table["SubjectID"] == subject]
        current_metric = metric_used(current_events, codeState_table)
        if current_metric == 0:
            dropped_metrics += 1
            continue
        map_score[subject] = current_metric
    out.info("Dropped %d subjects with no score" % dropped_metrics)
    return map_score
