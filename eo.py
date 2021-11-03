import pandas as pd
import sys
import os
import utils
import git_format
import edit_data_filter
import logging
import difflib

out = logging.getLogger()

#Note: This equation will drop subjects with 1 or less edits
def calculate_eo(session_table, codeState_table):
    session_table = session_table.sort_values(by=['Order'])
    edits = session_table[session_table["EventType"] == "File.Edit"]
    sum = 0
    #Going to be used to calculate diff in lines
    size_of_edit = 0
    #size(e) * daysToDeadline
    top_of_eq = 0
    #size(e)
    bottom_of_eq = 0
    if len(edits) <= 1:
        return 0
    for i in range(len(edits)-1):
        current_codeState = edits["CodeStateID"].iloc[i]
        next_codeState = edits["CodeStateID"].iloc[i+1]
        current_code = codeState_table[codeState_table['CodeStateID'] == current_codeState].get("Code").iloc[0]
        next_code = codeState_table[codeState_table['CodeStateID'] == next_codeState].get("Code").iloc[0]
        size_of_edit += calculate_line_difference(current_code, next_code)
        days_to_deadline = (edits["X-Deadline"].iloc[i] - edits["X-Timestamp"].iloc[i]).days
        top_of_eq += size_of_edit * days_to_deadline
        bottom_of_eq += size_of_edit
    return top_of_eq/bottom_of_eq

def calculate_line_difference(current_code, next_code):
    diff_size = 0
    more_lines = []
    less_lines = []
    current_lines = [line for line in current_code.split('\n') if line.strip() != '']
    next_lines = [line for line in next_code.split('\n') if line.strip() != '']
    current_length = len(current_lines)
    next_length = len(next_lines)
    if(current_length >= next_length):
        more_lines = current_lines
        less_lines = next_lines
    else:
        more_lines = next_lines
        less_lines = current_lines
    diffInstance = difflib.Differ()
    diffList = list(diffInstance.compare(more_lines, less_lines))
    if len(diffList) > 0:
        for line in diffList:
            if line[0] == '-':
                diff_size += 1
    return diff_size

if __name__ == "__main__":
    if(len(sys.argv) == 3 and sys.argv[1] == "-g"):
        write_path = "./out/EO_git.csv"
        file_path = sys.argv[2]
        git_metric = git_format.run_repos(file_path)
        print(git_metric)
        utils.write_git_metrics("EarlyandOften", git_metric, write_path)
        
    
    else:
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

        main_table_df, deadline_table_df, codestates_table_df = edit_data_filter.load_main_table(read_path, data_filter, min_edits)
        checker = utils.check_attributes(main_table_df, ["SubjectID", "Order", "EventType", "AssignmentID", "ParentEventID", "EditType"])
        checker2 = utils.check_attributes(deadline_table_df, ["AssignmentID", "X-Deadline"])
        checker3 = utils.check_attributes(codestates_table_df, ["CodeStateID", "Code"])
        
        
        if checker and (checker2 and checker3):
            eo_map = utils.calculate_metric(main_table_df, calculate_eo, codestates_table_df)
            out.info(eo_map)
            utils.write_metric_map("EarlyandOften", eo_map, write_path)
    