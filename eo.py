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
        sum += edits["X-daysToDeadline"].iloc[i]
    return sum/len(edits)

if __name__ == "__main__":
    read_path = "./data"
    write_path = "./out/EO.csv"

    if len(sys.argv) > 1:
        read_path = sys.argv[1]
    if len(sys.argv) > 2:
        write_path = sys.argv[2]

    main_table_df = edit_data_filter.load_main_table(read_path)
    print(main_table_df)
    checker = utils.check_attributes(main_table_df, ["SubjectID", "Order", "EventType", "EventID", "ParentEventID", "EditType", "X-Deadline"])
    print("Start of Eo works")
    if checker:
        eo_map = utils.calculate_metric_map(main_table_df, calculate_eo)
        out.info(eo_map)
        utils.write_metric_map("EarlyandOften", eo_map, write_path)