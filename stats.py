from pydriller import Repository
from datetime import datetime
from config import configGroup
from datetime import timedelta
import os
import csv
import argparse
import re
import string



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
        ''' show all options of the commit object '''
        for commit in Repository(self.LOCAL_PROJECT_DIRECTORY).traverse_commits():
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

    def getReport(self, maxLines, exportDir, startDate=None, endDate=None, groupNickname=None):
            '''get a detailed report in the following format:
                    date,username,num_lines_changed,file,path,branch,commit
            option:
            maxLines - at what count of lines modified do we no longer track a commit. If a commit exceeds this amount then we will skip it.
            '''
            # pull information from config
            self.LOCAL_PROJECT_DIRECTORY = configGroup[groupNickname]["LOCAL_PROJECT_DIRECTORY"]
            # this is backwards logic - we set the script so when the useContributors option is not used, it should be set to be False
            # instead it is automatically set to True (in this particular argParsing library). So False means True here
            # !=True means !=False
            if args.useContributors != True:
                self.CONTRIBUTORS = configGroup[groupNickname]["CONTRIBUTORS"]
                self.useAll = False
            else:
                # this creates a list containing every capital and lower case alphabetical character
                # when the script matches any username containing one of these characters it will export the username + record (all github usernames require at least one of these characters so it should always match)
                l = []
                for i in string.ascii_uppercase:
                    l.append(i)
                for i in string.ascii_lowercase:
                    l.append(i)
                
                self.CONTRIBUTORS = {"all": l}
                self.useAll = True
            self.REPO_LINK = configGroup[groupNickname]["REPO_LINK"]
            self.IGNORE_DIRECTORY = configGroup[groupNickname]["IGNORE_DIRECTORY"]
            


            records = []
            
            
            commitsObject = Repository(self.LOCAL_PROJECT_DIRECTORY).traverse_commits()
            for commit in commitsObject:
               #get commits from all branches - skip commits that have already been checked
                # print("in main branch printout "+ str(commit.in_main_branch))
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

                if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:
                    for userProfiles in self.CONTRIBUTORS:
                        for userProfile in self.CONTRIBUTORS[userProfiles]:
                            # if commit.author.name == userProfile:
                            if userProfile in commit.author.name:
                                if (commit.insertions+commit.deletions) > maxLines:
                                    if args.v:
                                        print("-"*70)
                                        if self.REPO_LINK != "":
                                            print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- {self.REPO_LINK}/commit/{commit.hash}")
                                        else:
                                            print(f"skipping {commit.insertions+commit.deletions} modified lines for username {commit.author.name} ---------- github ref link -- (set your REPO_LINK variable to the URL of your online repository for ref link reporting)")

                                    break
                                for file in commit.modified_files:
                                    if file.filename in self.getAcceptableFiles():
                                        if self.useAll == True:
                                            d = {"date":datetime.date(commit.committer_date), "username":commit.author.name, "num_lines_changed":0, "file":file.filename, "path":None, "branch":next(iter(commit.branches)), "commitNum":commit.hash}
                                        elif self.useAll == False:
                                            d = {"date":datetime.date(commit.committer_date), "username":userProfiles, "num_lines_changed":0, "file":file.filename, "path":None, "branch":next(iter(commit.branches)), "commitNum":commit.hash}

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

            index = exportDir.find(".csv")
            exportDir = exportDir[:index] + str(datetime.now().replace(microsecond=0)).replace(" ", "-") + exportDir[index:]

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
        for root, dirs, files in os.walk(self.LOCAL_PROJECT_DIRECTORY):
            [dirs.remove(d) for d in list(dirs) if d in self.IGNORE_DIRECTORY]
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
    parser.add_argument('-nickname', help="enter the repository nickname set in config.py to use (this contains all of the data needed to target the correct repository)")
    parser.add_argument('-useContributors', help="Instruct the script on whether to use the declared contributors to build the report", action="store_false")

    args = parser.parse_args()
    if args.exportCSV:
        if  ".csv" not in args.exportCSV:
            raise ValueError('option -exportCSV must be used with a filename ending with extension .csv')

        if args.nickname not in list(configGroup.keys()):
            raise ValueError(f"\n\nplease choose a valid config nickname option  (these are set by you in config.py)\n options currently available are: {list(configGroup.keys())}")    


        a = engine()
        if args.start and args.end:
            if args.maxLines != None:
                if args.v:
                    print(f"specified maximum lines from any single commit is {args.maxLines}")
                a.getReport(exportDir=args.exportCSV, maxLines=args.maxLines, startDate=args.start, endDate=args.end, groupNickname=args.nickname)
            else:
                a.getReport(exportDir=args.exportCSV, maxLines=1000, startDate=args.start, endDate=args.end, groupNickname=args.nickname)
        else:
            if args.maxLines != None:
                if args.v:
                    print(f"specified maximum lines from any single commit is {args.maxLines}")
                a.getReport(exportDir=args.exportCSV, maxLines=args.maxLines, groupNickname=args.nickname)
            else:
                a.getReport(exportDir=args.exportCSV, maxLines=1000, groupNickname=args.nickname)

