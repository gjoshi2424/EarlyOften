import pandas as pd
import sys
import os
import utils
import edit_data_filter
import logging

out = logging.getLogger()

def calculate_eo(session_table):
    session_table = session_table.sort_values(by=['Order'])
    edits = session_table[session_table["EventType"] == "File.Edit"]
    sum = 0
    for i in range(len(edits)):
        addition = (edits["X-Deadline"].iloc[i] - edits["X-Timestamp"].iloc[i]).days
        sum += addition
    return sum/len(edits)
if __name__ == "__main__":
    read_path = "./data"
    write_path = "./out/EO.csv"

    if len(sys.argv) > 1:
        read_path = sys.argv[1]
    if len(sys.argv) > 2:
        write_path = sys.argv[2]
    while True:
        filter_data = str(input("Would you like to filter data (Y/N): "))
        if(filter_data == "Y" or filter_data == "N"):
            break
        else:
            print("Enter valid input (Y/N)")
            continue
    data_filter = False
    min_edits = 0
    if(filter_data == "Y"):
        data_filter = True
        while True:
            try:
                min_edits = int(input("Enter minimum number of edits required for each subject (positive integer): "))
                if min_edits >= 1:
                    break
                else:
                    print("Please enter a positive integer")
            except ValueError:
                print("Give a positive integer")
                continue

    main_table_df, deadline_table_df = edit_data_filter.load_main_table(read_path, data_filter, min_edits)
    #print(main_table_df)
    checker = utils.check_attributes(main_table_df, ["SubjectID", "Order", "EventType", "EventID", "ParentEventID", "EditType"])
    checker2 = utils.check_attributes(deadline_table_df, ["AssignmentID", "X-Deadline"])
    #print("Start of Eo works")
    if checker:
        #eo_map = utils.calculate_metric_map(main_table_df, calculate_eo)
        eo_map = utils.calculate_metric(main_table_df, calculate_eo)
        out.info(eo_map)
        utils.write_metric_map("EarlyandOften", eo_map, write_path)