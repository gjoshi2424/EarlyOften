from pydriller import Repository
from git import Repo
import glob

#gjoshi2424/test_data

def check(repo_path):
    linkTable_files = []
    main_file = []
    Repo.clone_from("https://github.com/" + repo_path + '.git', './temp')
    for filename in glob.iglob('./temp/Data/LinkTables/**/*.csv', recursive = True):
        linkTable_files.append(filename)
    for filename in glob.iglob('./temp/Data/MainTable.csv', recursive = True):
        main_file.append(filename)
    #Check for errors
    if len(linkTable_files) < 2 or len(main_file) != 1:
        raise Exception("Format not valid")
    
    read_path = './temp/Data/'
    return read_path
