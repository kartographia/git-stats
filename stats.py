from pydriller import Repository
from datetime import datetime
from config import CONFIG_GROUP
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


class Engine:

    def _all_commit_stats(self):
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

    def _all_options(self):
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

    def get_report(self, max_lines, export_dir, start_date=None, end_date=None):
        '''get a detailed report in the following format:
                date,username,num_lines_changed,file,path,branch,commit
        option:
        max_lines - at what count of lines modified do we no longer track a commit. If a commit exceeds this amount then we will skip it.
        '''
        if args.getAll == True:
            group_nicknames = []

            for group_nickname in CONFIG_GROUP:
                group_nicknames.append(group_nickname)
        
        else:
            group_nicknames = [args.nickname]

        if args.v:
            s = "collecting records from the following repositories: "
            for name in group_nicknames:
                s+= f"{name}, "
            
            s += "...\n"
            print(s)
            time.sleep(2.5)

        # list of file types that were ignored by the script 
        self.ignored_file_types = []
        records = []

        for group_nickname in group_nicknames:
            if args.v:
                print(f"Collecting records from repository: {group_nickname}")
                time.sleep(1)

            # pull information from config
            self.LOCAL_PROJECT_DIRECTORY = CONFIG_GROUP[group_nickname]["LOCAL_PROJECT_DIRECTORY"]


            if args.useContributors == True:
                try:
                    self.CONTRIBUTORS = CONFIG_GROUP[group_nickname]["CONTRIBUTORS"]
                    self.ALIAS_TO_NAME = {alias: name for name, l in self.CONTRIBUTORS.items() for alias in l}

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

            self.REPO_LINK = CONFIG_GROUP[group_nickname]["REPO_LINK"]
            self.OK_FILE_TYPES = CONFIG_GROUP[group_nickname]["OK_FILE_TYPES"]
            
            
            commits_object = Repository(self.LOCAL_PROJECT_DIRECTORY).traverse_commits()
            for commit in commits_object:
                organization = self.REPO_LINK.split('github.com/')[1].split(commit.project_name)[0].strip('/')
                
                if start_date != None and end_date != None:
                    date_end = datetime.strptime(end_date,'%m/%d/%Y').date()
                    date_start = datetime.strptime(start_date,'%m/%d/%Y').date()
                    date_difference_days = (date_end - date_start).days

                else:
                    # hard-coded 150 years - gets all commits of any repo
                    days = 55000
                    date_difference_days = days
                    date_end = datetime.now().date()
                    date_start = date_end - timedelta(days)

                committer_date = datetime.fromisoformat(str(commit.committer_date)).date()
                how_long_ago = (date_end - committer_date).days

                # Skip commits that were too long ago
                if how_long_ago > date_difference_days:
                    continue

                # Make sure not too many lines (using total lines changed for the entire commit)
                if commit.insertions + commit.deletions > max_lines:
                    
                    if args.v:
                        print("-"*70)
                        if self.REPO_LINK != "":
                            print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- {self.REPO_LINK}/commit/{commit.hash}")
                        else:
                            print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- (set your REPO_LINK variable to the URL of your online repository for ref link reporting)")
                    continue

                for file in commit.modified_files:
                    
                    # Make sure file extension is ok
                    file_extension = '.'+file.filename.split('.')[-1]
                    if file_extension not in self.OK_FILE_TYPES:
                        if args.v:
                            sys.stdout.write(f"\rSkipping {file.filename} due to file extension"+" "*40)
                            sys.stdout.flush()
                        self.ignored_file_types.append(file_extension) if file_extension not in self.ignored_file_types else self.ignored_file_types
                        continue


                    if args.useContributors:
                        contributor_name = self.ALIAS_TO_NAME.get(commit.author.name, commit.author.name)
                    else:
                        contributor_name = None

                    d = {
                        "date":datetime.date(commit.committer_date),
                        "username": commit.author.name,
                        "contributor": contributor_name,
                        "num_lines_changed":0,
                        "file":file.filename,
                        "path": None,
                        "branch":'|'.join(commit.branches),
                        "commit_number":commit.hash,
                        "repository":commit.project_name,
                        "organization":organization,
                        "filetype":file_extension,
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
        export_dir = export_dir.replace('.csv', '') + '-' + datestr + '.csv'

        with open(export_dir, 'w') as f:
            if args.v:
                print(f"\n\nexporting {len(records)} records to csv file {export_dir} ...")
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writeheader()
            dict_writer.writerows(records)
        if args.v:
            print("done!")
            print(f"ignored file types were:\n\n {self.ignored_file_types}")
        
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-exportCSV', help='pass directory of where to export CSV')
    parser.add_argument('-start', help='start date for querying github repository in m/d/y format')
    parser.add_argument('-end', help='end date for querying github repository in m/d/y format')
    parser.add_argument('-maxLines', help='specify acceptable maximum lines modified from commits queried - use for accuracy (default is 1000)')
    parser.add_argument('-v', help='verbose output - show additional information', action='store_true')
    parser.add_argument('-nickname', help="enter the repository nickname set in config.py to use (this contains all of the data needed to target the correct repository)")
    parser.add_argument('-useContributors', help="Instruct the script on whether to use the declared contributors to build the report", action="store_true")
    parser.add_argument('-optionsPrint', help="use this to print the available options of a commit (shows whats available to be used as columns in a csv" ,action="store_true")
    parser.add_argument('-getAll', help="use this to get all of the repositories listed in config.py exported to one csv", action="store_true")


    args = parser.parse_args()

    if args.optionsPrint == False:

        if args.nickname == None and args.getAll == False:
            raise ValueError("\n\nYou must either use a nicknamed repo from config ( -nickname <repoName> ) or use option -getAll to collect records from all repos declared in config")

        if args.exportCSV == None:
            raise ValueError("\n\n Please specify an absolute path to directory to export CSV to, including filename and extension")
            
        else:
            if  ".csv" not in args.exportCSV:
                raise ValueError('option -exportCSV must be used with a filename ending with extension .csv')

            if args.nickname != None and args.nickname not in list(CONFIG_GROUP.keys()):
                raise ValueError(f"\n\nplease choose a valid config nickname option  (these are set by you in config.py)\n options currently available are: {list(CONFIG_GROUP.keys())}")    

            elif args.getAll == True:
                pass
            a = Engine()
            if args.start and args.end:
                if args.maxLines != None:
                    if args.v:
                        print(f"specified maximum lines from any single commit is {args.maxLines}")
                    a.get_report(export_dir=args.exportCSV, max_lines=args.maxLines, start_date=args.start, end_date=args.end)
                else:
                    a.get_report(export_dir=args.exportCSV, max_lines=1000, start_date=args.start, end_date=args.end)
            else:
                if args.maxLines != None:
                    if args.v:
                        print(f"specified maximum lines from any single commit is {args.maxLines}")
                    a.get_report(export_dir=args.exportCSV, max_lines=args.maxLines)
                else:
                    a.get_report(export_dir=args.exportCSV, max_lines=1000)
    
    else:
        print("printing options..")
        a = Engine()
        a._all_options()
