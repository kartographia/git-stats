from pydriller import Repository
from datetime import datetime
from config import CONTRIBUTORS
from config import LOCAL_PROJECT_DIRECTORY
from config import IGNORE_DIRECTORY
from config import REPO_LINK
from pprint import pprint
from datetime import timedelta
from itertools import islice
import os
import csv
import random
import argparse



'''
https://pydriller.readthedocs.io/en/latest/reference.html#module-pydriller.repository
only_in_branch (str) – only commits in this branch will be analyzed
only_authors (List[str]) – only commits of these authors will be analyzed (the check is done on the username, NOT the email)
only_commits (List[str]) – only these commits will be analyzed

author
----------------------------------------------------------------------
author_date
----------------------------------------------------------------------
author_timezone
----------------------------------------------------------------------
branches
----------------------------------------------------------------------
committer
----------------------------------------------------------------------
committer_date
----------------------------------------------------------------------
committer_timezone
----------------------------------------------------------------------
deletions
----------------------------------------------------------------------
dmm_unit_cbranchesomplexity
----------------------------------------------------------------------
dmm_unit_interfacing
----------------------------------------------------------------------
dmm_unit_size
----------------------------------------------------------------------
files
----------------------------------------------------------------------
hash
----------------------------------------------------------------------
in_main_branch
----------------------------------------------------------------------
insertions
----------------------------------------------------------------------
lines
----------------------------------------------------------------------
merge
----------------------------------------------------------------------
modified_files
----------------------------------------------------------------------
msg
----------------------------------------------------------------------
parents
----------------------------------------------------------------------
project_name
----------------------------------------------------------------------
project_path
'''
    
class engine:
        
    def _AllCommitStats(self):
        '''show multiple useful information field results from the commit object '''
        for commit in Repository(REPO_LINK).traverse_commits():
            # print(commit.msg)
            # print(commit.project_name)
            # print(commit.parents)
            # print(dir(commit.modified_files))
            print("deletion count  "+str(commit.deletions))
            print("insertion count  "+str(commit.insertions))
            print("file count modified  "+str(commit.files))
            # print("date authored " + str(commit.author_date))
            print("date committed " + str(commit.committer_date))
            # print("project path print " + str(commit.project_path))

            print("-"*70)
            print("-"*70)

    def _AllOptions(self):
        ''' show all options of the commit object '''
        for commit in Repository(REPO_LINK).traverse_commits():
            # for i in commit:
                # print(i)
            # print(dir(commit))
            for i in dir(commit):
                if i[0] != "_":
                    print(i)
                    print("-"*70)

            print("-"*70)
            print("-"*70)
            print("-"*70)
            print("-"*70)
            print("-"*70)
            print("-"*70)

    def getReport(self, maxLines, exportDir, startDate=None, endDate=None):
            '''get a detailed report in the following format:
                    date,username,num_lines_changed,file,path,branch,commit
            option:
            maxLines - at what count of lines modified do we no longer track a commit. If a commit exceeds this amount then we will skip it.
            '''
            records = []
            commitsObject = Repository(REPO_LINK).traverse_commits()
            for commit in commitsObject:
               #get commits from all branches - skip commits that have already been checked
                # print("in main branch printout "+ str(commit.in_main_branch))
                if startDate != None and endDate != None:
                    dateEnd = datetime.strptime(endDate,'%m/%d/%Y').date()
                    dateStart = datetime.strptime(startDate,'%m/%d/%Y').date()
                    dateDifferenceDays = (dateEnd - dateStart).days

                elif days != None:
                    dateDifferenceDays = days
                    dateEnd = datetime.now().date()
                    dateStart = dateEnd - timedelta(days)

                if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:
                    for userProfiles in CONTRIBUTORS:
                        for userProfile in CONTRIBUTORS[userProfiles]:
                            if commit.author.name == userProfile:
                                if (commit.insertions+commit.deletions) > maxLines:
                                    if args.v:
                                        print("-"*70)
                                        print(f"skipping {commit.insertions+commit.deletions} modified lines for user {userProfile} ---------- github ref link -- {REPO_LINK}/commit/{commit.hash}")
                                    break
                                for file in commit.modified_files:
                                    if file.filename in self.getAcceptableFiles():
                                        d = {"date":commit.committer_date, "username":userProfiles, "num_lines_changed":0, "file":file.filename, "path":None, "branch":next(iter(commit.branches)), "commitNum":commit.hash}

                                        for line in file.diff_parsed["added"]:
                                            if "console.log" in line[1]:
                                                pass
                                            elif "#" in line[1]:
                                                pass
                                            elif (line[1].isspace() == True):
                                                pass

                                            else:
                                                d["num_lines_changed"] =  d["num_lines_changed"] + 1
                                        
                                        for line in file.diff_parsed["deleted"]:
                                            if "console.log" in line[1]:
                                                pass

                                            elif "#" in line[1]:
                                                pass

                                            elif (line[1].isspace() == True or line[1] == ""):
                                                pass

                                            else:
                                                d["num_lines_changed"] =  d["num_lines_changed"] + 1
                                        records.append(d)
                
                                break


            keys = records[0].keys()

            with open(exportDir, 'w') as f:
                if args.v:
                    print(f"exporting {len(records)} records to csv file {exportDir} ...")
                dict_writer = csv.DictWriter(f,keys)
                dict_writer.writeheader()
                dict_writer.writerows(records)
                if args.v:
                    print("done!")
        

    def getAcceptableFiles(self):
        ''' returns a list of filenames to log modified line counts from - ignoring directories and filenames declared in config.py'''
        acceptableFiles = []
        for root, dirs, files in os.walk(LOCAL_PROJECT_DIRECTORY):
            [dirs.remove(d) for d in list(dirs) if d in IGNORE_DIRECTORY]
            for file in files:
                acceptableFiles.append(file)
        return acceptableFiles
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-exportCSV', help='pass directory of where to export CSV')
    parser.add_argument('-start', help='start date for querying github repository in m/d/y format')
    parser.add_argument('-end', help='end date for querying github repository in m/d/y format')
    parser.add_argument('-maxLines', help='specify acceptable maximum lines modified from commits queried - use for accuracy (default is 1000)')
    parser.add_argument('-v', help='verbose output - show additional information', action='store_true')

    args = parser.parse_args()
    if args.exportCSV:
        if  ".csv" not in args.exportCSV:
            raise ValueError('option -exportCSV must be used with a filename ending with extension .csv')
        a = engine()
        if args.start and args.end:
            if args.maxLines != None:
                if args.v:
                    print(f"specified maximum lines from any single commit is {args.maxLines}")
                a.getReport(exportDir=args.exportCSV, maxLines=args.maxLines, startDate=args.start, endDate=args.end)
            else:
                a.getReport(exportDir=args.exportCSV, maxLines=1000, startDate=args.start, endDate=args.end)
        else:
            if args.maxLines != None:
                if args.v:
                    print(f"specified maximum lines from any single commit is {args.maxLines}")
                a.getReport(exportDir=args.exportCSV, maxLines=args.maxLines)
            else:
                a.getReport(exportDir=args.exportCSV, maxLines=1000)

