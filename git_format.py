import pydriller 
import datetime

def run_repo(end_date, repo_path):
    user_date = end_date
    repo_name = repo_path
    year, month, day = map(int, user_date.split('-'))
    deadline = datetime.date(year,month, day)
    total_size_deadline = 0
    total_size = 0
    for commit in pydriller.Repository(repo_name).traverse_commits():
        comm_date = commit.committer_date.date()
        days_to_deadline = (deadline-comm_date).days
        size_of_edit = 0
        for modification in commit.modified_files:
            size_of_edit += modification.added_lines
            size_of_edit += modification.deleted_lines
        total_size_deadline += (size_of_edit * days_to_deadline)
        total_size += size_of_edit

    print("EO value: " + str(total_size_deadline/total_size))