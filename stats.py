from pydriller import Repository
from datetime import datetime
from config import configGroup
# from config import LOCAL_PROJECT_DIRECTORY
from datetime import timedelta
import os
import csv
import argparse
import re
import string
import time
import sys

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
   
py_re = re.compile(r' = |\(\)|print\(|^import |^from \w+ import|^def |^if.*\:|^return |^class.*\:|import \w+ as |for \w+ in \w+\:|\)\)')

def line_is_significant(line, file_extension):
    line = line.strip()
    if not line:
        return False
    if line[0] == '#':
        return False
    if line[:2] == '//':
        return False
    if 'console.log' in line:
        return False
    if file_extension == '.ipynb':
        if not py_re.search(line):
            return False
    return True


class engine:

    def _AllCommitStats(self):
        '''show multiple useful information field results from the commit object '''
        for commit in Repository(self.LOCAL_PROJECT_DIRECTORY).traverse_commits():
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
        ''' show all options of the commit object
        Note: need to declare a local project directory within config.py and import it by uncommenting the import line at the top of this file
         '''
        for commit in Repository(LOCAL_PROJECT_DIRECTORY).traverse_commits():
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
        if args.getAll == True:
            groupNicknames = []

            for groupNickname in configGroup:
                groupNicknames.append(groupNickname)
        
        else:
            groupNicknames = [args.nickname]

        if args.v:
            s = "collecting records from the following repositories: "
            for name in groupNicknames:
                s+= f"{name}, "
            
            s += "...\n"
            print(s)
            time.sleep(2.5)


        for groupNickname in groupNicknames:
            if args.v:
                print(f"Collecting records from repository: {groupNickname}")
                time.sleep(1)

            # pull information from config
            self.LOCAL_PROJECT_DIRECTORY = configGroup[groupNickname]["LOCAL_PROJECT_DIRECTORY"]

            try:
                self.CONTRIBUTORS = configGroup[groupNickname]["CONTRIBUTORS"]
            except:
                raise Exception((
                    "-----------------------------------------------------------------------------------\n"
                    "You specified to use the -useContributors option and we are not able to locate"
                    "the dict containing contributors,\n please verify the CONTRIBUTORS format "
                    "in config.py is correct and/or declared.\n"
                    "if you would like to use this script without using contributor profiles,\n"
                    "drop the -useContributors option from the command.\n"
                    "------------------------------------------------------------------------------------\n "
                ))

            self.ALIAS_TO_NAME = {alias: name for name, l in self.CONTRIBUTORS.items() for alias in l}

            self.REPO_LINK = configGroup[groupNickname]["REPO_LINK"]
            self.IGNORE_DIRECTORY = configGroup[groupNickname]["IGNORE_DIRECTORY"]
            self.OK_FILE_TYPES = configGroup[groupNickname]["OK_FILE_TYPES"]
            
            records = []
            
            commitsObject = Repository(self.LOCAL_PROJECT_DIRECTORY).traverse_commits()
            for commit in commitsObject:
                organization = self.REPO_LINK.split('github.com/')[1].split(commit.project_name)[0]
                
                if startDate != None and endDate != None:
                    dateEnd = datetime.strptime(endDate,'%m/%d/%Y').date()
                    dateStart = datetime.strptime(startDate,'%m/%d/%Y').date()
                    dateDifferenceDays = (dateEnd - dateStart).days

                else:
                    # hard-coded 150 years - gets all commits of any repo
                    days = 55000
                    dateDifferenceDays = days
                    dateEnd = datetime.now().date()
                    dateStart = dateEnd - timedelta(days)

                committer_date = datetime.fromisoformat(str(commit.committer_date)).date()
                how_long_ago = (dateEnd - committer_date).days
                # Skip commits that were too long ago
                if how_long_ago > dateDifferenceDays:
                    continue

                # # Skip commits with too many lines (default 1000)
                # if (commit.insertions+commit.deletions) > maxLines:
                #     if args.v:
                #         print("-"*70)
                #         if self.REPO_LINK != "":
                #             print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- {self.REPO_LINK}/commit/{commit.hash}")
                #         else:
                #             print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- (set your REPO_LINK variable to the URL of your online repository for ref link reporting)")
                #     continue

                for file in commit.modified_files:
                    
                    # Make sure file extension is ok
                    file_extension = '.'+file.filename.split('.')[-1]
                    if file_extension not in self.OK_FILE_TYPES:
                        sys.stdout.write(f"\rSkipping {file.filename} due to file extension"+" "*40)
                        sys.stdout.flush()
                        continue

                    contributor_name = self.ALIAS_TO_NAME.get(commit.author.name, commit.author.name)

                    d = {
                        "date":datetime.date(commit.committer_date),
                        "username": contributor_name,
                        "num_lines_changed":0,
                        "file":file.filename,
                        "path": None,
                        "branch":'|'.join(commit.branches),
                        "commitNum":commit.hash,
                        "repository":commit.project_name,
                        "organization":organization
                    }

                    for line in file.diff_parsed["added"]:
                        if line_is_significant(line[1], file_extension):
                            d["num_lines_changed"] += 1
                    
                    for line in file.diff_parsed["deleted"]:
                        if line_is_significant(line[1], file_extension):
                            d["num_lines_changed"] += 1

                    if d["num_lines_changed"] > 0:
                        records.append(d)
    
            # Remove duplicate records. records is a list of dicts
            records = [dict(t) for t in {tuple(d.items()) for d in records}]

            keys = records[0].keys()

            datestr = str(datetime.now().replace(microsecond=0)).replace(" ", "-").replace(':', '.')
            exportDir = exportDir.replace('.csv', '') + '-' + datestr + '.csv'

            with open(exportDir, 'w') as f:
                if args.v:
                    print(f"\n\nexporting {len(records)} records to csv file {exportDir} ...")
                dict_writer = csv.DictWriter(f,keys)
                dict_writer.writeheader()
                dict_writer.writerows(records)
                if args.v:
                    print("done!")
        

    # def getAcceptableFiles(self):
    #     ''' returns a list of filenames to log modified line counts from - ignoring directories and filenames declared in config.py'''
    #     acceptableFiles = []
    #     for root, dirs, files in os.walk(self.LOCAL_PROJECT_DIRECTORY):
    #         [dirs.remove(d) for d in list(dirs) if d in self.IGNORE_DIRECTORY]
    #         for file in files:
    #             file_extension = '.'+file.split('.')[-1]
    #             if file_extension in self.OK_FILE_TYPES:
    #                 acceptableFiles.append(file)
    #     return acceptableFiles
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-exportCSV', help='pass directory of where to export CSV')
    parser.add_argument('-start', help='start date for querying github repository in m/d/y format')
    parser.add_argument('-end', help='end date for querying github repository in m/d/y format')
    parser.add_argument('-maxLines', help='specify acceptable maximum lines modified from commits queried - use for accuracy (default is 1000)')
    parser.add_argument('-v', help='verbose output - show additional information', action='store_true')
    parser.add_argument('-nickname', help="enter the repository nickname set in config.py to use (this contains all of the data needed to target the correct repository)")
    parser.add_argument('-useContributors', help="Instruct the script on whether to use the declared contributors to build the report", action="store_false")
    parser.add_argument('-optionsPrint', help="use this to print the available options of a commit (shows whats available to be used as columns in a csv" ,action="store_true")
    parser.add_argument('-getAll', help="use this to get all of the repositories listed in config.py exported to one csv", action="store_true")


    args = parser.parse_args()
    if args.optionsPrint == False:

        if args.nickname == None and args.getAll == False:
            raise ValueError("\n\nYou must either use a nicknamed repo from config ( -nickname <repoName> ) or use option -getAll to collect records from all repos declared in config")

        if args.exportCSV:
            if  ".csv" not in args.exportCSV:
                raise ValueError('option -exportCSV must be used with a filename ending with extension .csv')

            if args.nickname != None and args.nickname not in list(configGroup.keys()):
                raise ValueError(f"\n\nplease choose a valid config nickname option  (these are set by you in config.py)\n options currently available are: {list(configGroup.keys())}")    

            elif args.getAll == True:
                pass
            
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
    
    else:
        print("printing options..")
        a = engine()
        a._AllOptions()
