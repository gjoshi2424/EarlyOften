import pydriller 
import datetime
import pandas as pd

def run_repos(file_path):
    try:
        cur_df = pd.DataFrame(columns=['Repo_name', 'EarlyandOften'])
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                temp_arr = line.split()
                if len(temp_arr) != 2:
                    print("Txt file has incorrect format")
                    exit(1)
                val = calc_repo_eo(temp_arr[1], temp_arr[0])
                print(val)
                temp = {'Repo_name': temp_arr[0], 'EarlyandOften':val}
                cur_df = cur_df.append(temp, ignore_index=True)
        #print(cur_df)
        return cur_df
    except FileNotFoundError:
        print("Invalid path to git repo file")
        exit(1)
            

def calc_repo_eo(user_date, repo_name):
    try:
        year, month, day = map(int, user_date.split('-'))
        deadline = datetime.date(year,month, day)
    except ValueError:
        print("Could not convert input to valid date value")
        exit(1)

    total_size_deadline = 0
    total_size = 0
    try:
        for commit in pydriller.Repository(repo_name).traverse_commits():
            comm_date = commit.committer_date.date()
            days_to_deadline = (deadline-comm_date).days
            size_of_edit = 0
            for modification in commit.modified_files:
                size_of_edit += modification.added_lines
                size_of_edit += modification.deleted_lines
            total_size_deadline += (size_of_edit * days_to_deadline)
            total_size += size_of_edit
    except Exception as e:
        print("Not valid git repo path")
        exit(1)

    print("EO value: " + str(total_size_deadline/total_size))
    return str(total_size_deadline/total_size)
 