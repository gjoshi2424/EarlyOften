
import pandas as pd
import numpy as np
import datetime
import sys
import os
import csv
import pathlib
import utils
import logging
import re

#This is used for deriving independent session ids
GAP_TIME = 1200
MIN_SESSIONS_Z = -2
#Temporary
MIN_EDITS = 2
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

CACHE_VERSION = '2019.08.28.A'
CACHE_TABLE_NAME = "MainTable_filtered_" + CACHE_VERSION + ".csv"

out = logging.getLogger()


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def get_cache_table_path(data_dir):
    return "cache/" + get_valid_filename(data_dir) + "/" + CACHE_TABLE_NAME


def assign_session_ids(main_table_df, gap_time=GAP_TIME):
    #If there already is a sessionID then return
    if "SessionID" in main_table_df:
        return main_table_df

    out.info("Assigning session IDs:")
    #Check for either servertimestamp, or client timestamp
    for tsf in ["ServerTimestamp", "ClientTimestamp"]:
        if tsf in main_table_df:
            timestamp_field = tsf
    if timestamp_field is None:
        raise Exception("No Timestamp!")

    #Sort table by subjects and then order 
    main_table_df.sort_values(['SubjectID', 'Order'], inplace=True)
    timestamps = []
    #This will be the days to deadline column
    difference = []
    for i in range(len(main_table_df)):
        timestamps.append(datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT))
        difference.append((datetime.datetime.strptime(main_table_df["X-Deadline"].iloc[i], DATE_FORMAT) - 
            datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT)).days)
        #print(difference[len(difference)-1])
        #print(datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT))
        #print("Server")
        #print(datetime.datetime.strptime(main_table_df["X-Deadline"].iloc[i], DATE_FORMAT))
        #print("Deadline")
        #print(datetime.datetime.strptime(main_table_df["X-Deadline"].iloc[i], DATE_FORMAT) - datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT))
        #print("Diff")
    subject_id = None
    session_id = 0
    session_ids = []
    #timestamps = [datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT)
     #             for i in range(len(main_table_df))]

    subject_changes = 0
    #Now we have a seperate array of timestamps and subjects/ order sorted
    for i in range(len(main_table_df)):
        timestamp = timestamps[i]
        #print(timestamp.year)
        #If the subject changes in the table
        if subject_id != main_table_df["SubjectID"].iloc[i]:
            last_timestamp = datetime.datetime.strptime(main_table_df[timestamp_field].iloc[i], DATE_FORMAT)
            session_id = session_id + 1
            subject_id = main_table_df["SubjectID"].iloc[i]
            subject_changes += 1

        # Store separately for efficiency
        session_ids.append(session_id)

        #If the gap time is greater then create a new session id
        if (timestamp - last_timestamp).total_seconds() / 60.0 > gap_time:
            session_id += 1
        last_timestamp = timestamp
        utils.print_progress_bar(i + 1, len(main_table_df))

    #Add the sessionID column to the events table
    main_table_df["SessionID"] = session_ids
    main_table_df["X-daysToDeadline"] = difference

    out.info("Subjects: " + str(subject_changes))
    out.info("Assigned %d unique sessionIDs" % session_id)
    #Sort the table by order only again
    main_table_df.sort_values(['Order'], inplace=True)
    #print(main_table_df)
    return main_table_df


def filter_dataset(main_table_df, gap_time=GAP_TIME, min_edits=MIN_EDITS, min_sessions_z=MIN_SESSIONS_Z):
    #main_table_df is just the main events table w/ sessions in it
    main_table_df = assign_session_ids(main_table_df, gap_time)
    n_students = len(set(main_table_df["SubjectID"]))
    n_sessions = len(set(main_table_df["SessionID"]))
    #print(n_students)
    #print(n_sessions)

    #Need to change this part 
    out.info("Filtering sessions...")
    edit_sessions = main_table_df[main_table_df["EventType"] == "File.Edit"]["SessionID"]
    edit_count_map = {session_id: np.sum(edit_sessions == session_id)
                          for session_id in set(main_table_df["SessionID"])}
    out.debug("Edits count map: %s" % edit_count_map)

    mean_edits = np.mean(list(edit_count_map.values()))
    sd_edits = np.std(list(edit_count_map.values()))
    session_to_keep = [session_id for session_id in edit_count_map.keys()
                       if edit_count_map[session_id] >= min_edits]

    main_table_df = main_table_df[main_table_df["SessionID"].isin(session_to_keep)]
    out.info("Dropping %d sessions with < %.02f edits (M=%.02f and SD=%.02f), removing %s students" %
            (n_sessions - len(session_to_keep), min_edits, mean_edits, sd_edits,
             n_students - len(set(main_table_df["SubjectID"]))))

    out.info("Filtering students...")
    session_count_map = {subject_id: len(set(main_table_df[main_table_df["SubjectID"] == subject_id]["SessionID"]))
                         for subject_id in set(main_table_df["SubjectID"])}
    out.debug("Session count map: %s" % session_count_map)
    mean_sessions = np.mean(list(session_count_map.values()))
    sd_sessions = np.std(list(session_count_map.values()))
    if sd_sessions == 0:
        sd_sessions = 1

    students_to_keep = [subject_id for subject_id in session_count_map.keys()
                        if (session_count_map[subject_id] - mean_sessions) / sd_sessions >= min_sessions_z]

    out.info("Dropping %d students with with z-score < %.02f for sessions (M=%.02f and SD=%.02f)" %
            (len(session_count_map) - len(students_to_keep), min_sessions_z, mean_sessions, sd_sessions))

    main_table_df = main_table_df[main_table_df["SubjectID"].isin(students_to_keep)]

    return main_table_df


def load_main_table(read_dir, filter=True, from_cache=True):
    #Gets file path to main events table
    table_path = get_cache_table_path(read_dir)
    #os path will be false for default
    #print(os.path.exists(table_path) == True)
    if filter and from_cache and os.path.exists(table_path):
        out.info("Loading from cached file: %s" % table_path)
        return pd.read_csv(table_path)
    #Crates a pandas data frame from MainTable csv
    main_table_df = pd.read_csv(os.path.join(read_dir, "MainTable.csv"))
    #filter is true by default
    if filter:
        #print("Gets here")
        main_table_df = filter_dataset(main_table_df)
    return main_table_df
