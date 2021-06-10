
import pandas as pd
import datetime
import os
import logging
import re

#This is used for deriving independent session ids
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

CACHE_VERSION = '2019.08.28.A'
CACHE_TABLE_NAME = "MainTable_filtered_" + CACHE_VERSION + ".csv"

out = logging.getLogger()


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def get_cache_table_path(data_dir):
    #cache/.data/MainTable_filtered_2019.08.28.A.csv
    return "cache/" + get_valid_filename(data_dir) + "/" + CACHE_TABLE_NAME


def format_times(main_table_df, deadline_table_df):
    out.info("Formatting server and deadline timestamps")
    #Check for either servertimestamp, or client timestamp
    for tsf in ["ServerTimestamp", "ClientTimestamp"]:
        if tsf in main_table_df:
            timestamp_field = tsf
    if timestamp_field is None:
        raise Exception("No Timestamp!")
    timestamps = []
    deadlines = []
    for i in range(len(deadline_table_df)):
        deadlines.append(datetime.datetime.strptime(deadline_table_df["X-Deadline"].iloc[i], DATE_FORMAT))
    for i in range(len(main_table_df)):
        timestamps.append(datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT))
    deadline_table_df["X-Deadline"] = deadlines
    main_table_df["X-Timestamp"] = timestamps
    main_table_df = pd.merge(main_table_df, deadline_table_df, left_on= 'AssignmentID', right_on= "AssignmentID", how= "left")
    main_table_df.sort_values(['Order'], inplace=True)
    #print(main_table_df)
    return main_table_df

def filter_dataset(main_table_df, min_edits):
    out.info("Filtering data set")
    subjects_removed = 0
    list_of_subjects = set(main_table_df["SubjectID"])
    for subject in list_of_subjects:
        check = main_table_df[main_table_df["SubjectID"] == subject]
        if len(check) < min_edits:
            subjects_removed += 1
            main_table_df = main_table_df[main_table_df["SubjectID"] != subject]
            out.info("Removed %s" % subject)
    out.info("Removed %d subjects" % subjects_removed)
    return main_table_df


def load_main_table(read_dir, filter, min_edits, from_cache=True):
    #Gets file path to main events table
    table_path = get_cache_table_path(read_dir)

    #os path will be false for default
    #print(os.path.exists(table_path) == True)
    if filter and from_cache and os.path.exists(table_path):
        out.info("Loading from cached file: %s" % table_path)
        return pd.read_csv(table_path)
    #Crates a pandas data frame from MainTable csv
    main_table_df = pd.read_csv(os.path.join(read_dir, "MainTable.csv"))
    deadline_table_df = pd.read_csv(os.path.join(read_dir, "LinkTables/Deadline.csv"))
    codestates_table_df = pd.read_csv(os.path.join(read_dir, "LinkTables/CodeStates.csv"))
    #filter is true by default
    main_table_df = format_times(main_table_df, deadline_table_df)
    if filter:
        main_table_df = filter_dataset(main_table_df, min_edits)
    return main_table_df, deadline_table_df, codestates_table_df
