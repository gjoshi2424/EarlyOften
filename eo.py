import pandas as pd
import sys
import os
import utils
import edit_data_filter
import logging

out = logging.getLogger()

#Note: This equation will drop subjects with 1 or less edits
def calculate_eo(session_table, codeState_table):
    #print(codeState_table)
    session_table = session_table.sort_values(by=['Order'])
    edits = session_table[session_table["EventType"] == "File.Edit"]
    sum = 0
    #size(e) * daysToDeadline
    top_of_eq = 0
    #size(e)
    bottom_of_eq = 0
    if len(edits) <= 1:
        return 0
    #print(codeState_table["Code"].iloc[0])
    for i in range(len(edits)-1):
    #for i in range(0,1):
        current_codeState = edits["CodeStateID"].iloc[i]
        next_codeState = edits["CodeStateID"].iloc[i+1]
        #print(type(next_codeState))
        current_code = codeState_table[codeState_table['CodeStateID'] == current_codeState].get("Code").iloc[0]
        next_code = codeState_table[codeState_table['CodeStateID'] == next_codeState].get("Code").iloc[0]
        current_lines = [line for line in current_code.split('\n') if line.strip() != '']
        next_lines = [line for line in next_code.split('\n') if line.strip() != '']
        current_length = len(current_lines)
        next_length = len(next_lines)
        size_of_edit = abs(current_length - next_length)
        days_to_deadline = (edits["X-Deadline"].iloc[i] - edits["X-Timestamp"].iloc[i]).days
        top_of_eq += size_of_edit * days_to_deadline
        bottom_of_eq += size_of_edit
        #print(type(current_code))
        #df = temp1.rename(None).to_frame().T
        #temp1 = temp1.get("Code")
        #print(next_code)
        #addition = (edits["X-Deadline"].iloc[i] - edits["X-Timestamp"].iloc[i]).days
        #sum += addition
    #return sum/len(edits)
    return top_of_eq/bottom_of_eq

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

    main_table_df, deadline_table_df, codestates_table_df = edit_data_filter.load_main_table(read_path, data_filter, min_edits)
    #test1 = codestates_table_df["Code"].iloc[0]
    #print(test1)
    #lines = [line for line in test1.split('\n') if line.strip() != '']
    #print(lines)
    #print(len(lines))
    #print(main_table_df)
    checker = utils.check_attributes(main_table_df, ["SubjectID", "Order", "EventType", "AssignmentID", "ParentEventID", "EditType"])
    checker2 = utils.check_attributes(deadline_table_df, ["AssignmentID", "X-Deadline"])
    checker3 = utils.check_attributes(codestates_table_df, ["CodeStateID", "Code"])
    #print("Start of Eo works")
    
    
    if checker:
        #eo_map = utils.calculate_metric_map(main_table_df, calculate_eo)
        eo_map = utils.calculate_metric(main_table_df, calculate_eo, codestates_table_df)
        out.info(eo_map)
        utils.write_metric_map("EarlyandOften", eo_map, write_path)
    