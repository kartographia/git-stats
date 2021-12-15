from pydriller import Repository
from datetime import datetime
from config import CONTRIBUTORS
from config import BLUEWAVE_DIRECTORY
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
    def __init__(self):
        pass
        
    def printAllCommitStats(self):
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

    def printAllOptions(self):
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

    def getOverviewReport(self,maxLines, days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False):
        '''gets the total commits of the users in config over the past days specified and prints them 
        option:
        maxLines - at what count of lines modified do we no longer track a commit. If a commit exceeds this amount then we will skip it.
        '''
        loggedContributors = {}
        commitsObject = Repository(REPO_LINK).traverse_commits()
        for commit in commitsObject:
            #get commits from all branches - skip commits that have already been checked
            # print("in main branch printout "+ str(commit.in_main_branch))
            if startDate != None and endDate != None:
                dateEnd = datetime.strptime(endDate,'%Y-%m-%d').date()
                dateStart = datetime.strptime(startDate,'%Y-%m-%d').date()
                dateDifferenceDays = (dateEnd - dateStart).days

            elif days != None:
                dateDifferenceDays = days
                dateEnd = datetime.now().date()
                dateStart = dateEnd - timedelta(days)

            if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:
                for userProfiles in CONTRIBUTORS:
                    if userProfiles not in loggedContributors:
                        loggedContributors[userProfiles] = {"total commits":0,"total insertions":{"code":0, "comments":0, "logging":0},"total deletions":{"code":0, "comments":0, "logging":0}}
                    for userProfile in CONTRIBUTORS[userProfiles]:
                        if commit.author.name == userProfile:
                            loggedContributors[userProfiles]["total commits"] = loggedContributors[userProfiles]["total commits"] + 1
                            if (commit.insertions+commit.deletions) > maxLines:
                                print("-"*70)
                                print(f"skipping {commit.insertions+commit.deletions} modified lines for user {userProfile} ---------- github ref link -- {REPO_LINK}/commit/{commit.hash}")
                                break
                            for file in commit.modified_files:
                                if file.filename in self.getAcceptableFiles():

                                    for line in file.diff_parsed["added"]:
                                        if "console.log" in line[1]:
                                            loggedContributors[userProfiles]["total insertions"]["logging"] = loggedContributors[userProfiles]["total insertions"]["logging"] + 1 

                                        elif "#" in line[1]:
                                            loggedContributors[userProfiles]["total insertions"]["comments"] = loggedContributors[userProfiles]["total insertions"]["comments"] + 1 
                                        
                                        elif (line[1].isspace() == True):
                                            pass

                                        else:
                                            loggedContributors[userProfiles]["total insertions"]["code"] = loggedContributors[userProfiles]["total insertions"]["code"] + 1 
                                    
                                    
                                    for line in file.diff_parsed["deleted"]:
                                        if "console.log" in line[1]:
                                            loggedContributors[userProfiles]["total deletions"]["logging"] = loggedContributors[userProfiles]["total deletions"]["logging"] + 1 

                                        elif "#" in line[1]:
                                            loggedContributors[userProfiles]["total deletions"]["comments"] = loggedContributors[userProfiles]["total deletions"]["comments"] + 1 

                                        elif (line[1].isspace() == True or line[1] == ""):
                                            pass

                                        else:
                                            loggedContributors[userProfiles]["total deletions"]["code"] = loggedContributors[userProfiles]["total deletions"]["code"] + 1 
            
                            break

        statisticsString = f"statistics between {datetime.now().date() - timedelta(dateDifferenceDays)} and {datetime.now().date()}"
        if csvFormat == True:
            return statisticsString, loggedContributors, dateEnd, dateStart
        else:
            return statisticsString, loggedContributors

    def getDetailedReport(self,maxLines, days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False):
            '''get a detailed report in the following format:
                    date,username,num_lines_changed,file,path,branch,commit
            option:
            maxLines - at what count of lines modified do we no longer track a commit. If a commit exceeds this amount then we will skip it.
            '''
            dataStructure = []
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
                                        dataStructure.append(d)
                
                                break

            statisticsString = f"statistics between {datetime.now().date() - timedelta(dateDifferenceDays)} and {datetime.now().date()}"
            if csvFormat == True:
                return dataStructure, dateEnd, dateStart
            else:
                return statisticsString, dataStructure





    def exportOverviewReportToCsv(self,maxLines, days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False):
        ''' for exporting data to CSV format 
        following this structure:
        loggedContributors[userProfiles] = {"total commits":0,"total insertions":{"code":0, "comments":0, "logging":0},"total deletions":{"code":0, "comments":0, "logging":0}}

        '''

        if days != None:
            string1, overviewReport, dateStart, dateEnd =  self.getOverviewReport(maxLines, days=days, csvFormat=False)
       
        elif startDate and endDate != None:
            string1, overviewReport, dateStart, dateEnd =  self.getOverviewReport(maxLines, startDate=startDate, endDate=endDate, csvFormat=True)
       
        with open(f'temp/reports/overviewActivityReport{dateStart}___{dateEnd}.csv', 'w') as f:
                for key in overviewReport.keys():
                    f.write("%s,%s\n"%(key,overviewReport[key]))
        pass
    
    def exportDetailedReportToCsv(self, exportDir, maxLines=1000, giveFilename = False, startDate=None, endDate=None):
        ''' for exporting data to CSV format 
        date,username,num_lines_changed,file,path,branch'''

        
  
        if startDate and endDate != None:
            detailedReport, dateStart, dateEnd =  self.getDetailedReport(maxLines, startDate=startDate, endDate=endDate, csvFormat=True)
       
        else:
            detailedReport, dateStart, dateEnd =  self.getDetailedReport(maxLines, csvFormat=True)
        keys = detailedReport[0].keys()


        with open(exportDir, 'w') as f:
            if args.v:
                print(f"exporting {len(detailedReport)} records to csv file {exportDir} ...")
            dict_writer = csv.DictWriter(f,keys)
            dict_writer.writeheader()
            dict_writer.writerows(detailedReport)
            if args.v:
                print("done!")



    def getAcceptableFiles(self):

        acceptableFiles = []
        for root, dirs, files in os.walk(BLUEWAVE_DIRECTORY):
            [dirs.remove(d) for d in list(dirs) if d in IGNORE_DIRECTORY]
            for file in files:
                acceptableFiles.append(file)
        return acceptableFiles
    

    def printReportToConsole(self,maxLines, days=None, startDate=None, endDate=None):
        '''print the commits report to console '''
        if days != None:
            string1, contributorReport =  self.getCommitsOfUsers(maxLines, days=days, csvFormat=False)
        elif startDate and endDate != None:
            string1, contributorReport =  self.getCommitsOfUsers(maxLines, startDate=startDate, endDate=endDate, csvFormat=False)

        print(string1)
        pprint(contributorReport)


    def reportAdditionsPerFile(self,days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False, userResearch = None):
        '''gets information about a single user and reports based on their commits - this function is for debugging purposes - objective is to find inaccuracies in reports'''
        commitsObject = Repository(REPO_LINK).traverse_commits()
        for commit in commitsObject:
            #get commits from all branches - skip commits that have already been checked
            # print("in main branch printout "+ str(commit.in_main_branch))
            if startDate != None and endDate != None:
                dateEnd = datetime.strptime(endDate,'%Y-%m-%d').date()
                dateStart = datetime.strptime(startDate,'%Y-%m-%d').date()
                dateDifferenceDays = (dateEnd - dateStart).days

            elif days != None:
                dateDifferenceDays = days
                dateEnd = datetime.now().date()
                dateStart = dateEnd - timedelta(days)

            if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:
                    try:
                        userResearchReport
                    except:
                        userResearchReport = {"username":userResearch, "repo":REPO_LINK, "total commits":0,"total insertions":{"code":0, "comments":0, "logging":0},"total deletions":{"code":0, "comments":0, "logging":0}}
                    
                    if commit.author.name == userResearch:
                        userResearchReport["total commits"] = userResearchReport["total commits"] + 1
                        # print(f"found commit by {userResearch}")
                        for file in commit.modified_files:
                            if file.filename in self.getAcceptableFiles():
                                uniqueFilenameInt = random.randint(1000,9999)

                                if len(file.diff_parsed["added"]) > 300:
                                    print("-"*70)
                                    print("found a big commit insert "+str(commit.insertions) + " filename "+file.filename)
                                    print("github commit link for viewing "+ f"{REPO_LINK}/commit/{commit.hash}")
                                    print("insertions logged to "+f"temp/reports/exportedInsertionsCommit{datetime.now().date()}{uniqueFilenameInt}.txt")

                                    with open(f"temp/reports/exportedInsertionsCommit{datetime.now().date()}{uniqueFilenameInt}.txt","w+") as f:
                                        for line in file.diff_parsed["added"]:
                                            f.writelines(f"{line[1]}\n")
                                            if "console.log" in line[1]:
                                                userResearchReport["total insertions"]["logging"] = userResearchReport["total insertions"]["logging"] + 1 

                                            elif "#" in line[1]:
                                                userResearchReport["total insertions"]["comments"] = userResearchReport["total insertions"]["comments"] + 1 
                                            
                                            elif (line[1].isspace() == True):
                                                pass

                                            else:
                                                userResearchReport["total insertions"]["code"] = userResearchReport["total insertions"]["code"] + 1 
                                
                                if len(file.diff_parsed["deleted"]) > 300:
                                    print("-"*70)
                                    print("found a big commit delete "+str(commit.deletions)+ " filename "+file.filename)
                                    print("github commit link for viewing "+ f"{REPO_LINK}/commit/{commit.hash}")
                                    print("deletions logged to "+f"temp/reports/exportedDeletionsCommit{datetime.now().date()}{uniqueFilenameInt}.txt")

                                    with open(f"temp/reports/exportedDeletionsCommit{datetime.now().date()}{uniqueFilenameInt}.txt","w+") as f:
                                        for line in file.diff_parsed["deleted"]:
                                            f.writelines(f"{line[1]}\n")
                                            if "console.log" in line[1]:
                                                userResearchReport["total deletions"]["logging"] = userResearchReport["total deletions"]["logging"] + 1 

                                            elif "#" in line[1]:
                                                userResearchReport["total deletions"]["comments"] = userResearchReport["total deletions"]["comments"] + 1 

                                            elif (line[1].isspace() == True or line[1] == ""):
                                                pass

                                            else:
                                                userResearchReport["total deletions"]["code"] = userResearchReport["total deletions"]["code"] + 1 
                    
                            break

        statisticsString = f"statistics between {datetime.now().date() - timedelta(dateDifferenceDays)} and {datetime.now().date()}"
        print(statisticsString)
        pprint(userResearchReport)  

    def reportFilesEdittedPerCommit(self, alertCount, userResearch, days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False):
        '''gets information about a single user and reports based on their commits - this function is for debugging purposes - objective is to find inaccuracies in reports
        
        primary focus is whether a user is touching more than the specified number of files at a time. Best accuracy has been above 3 files.
        
        note: this has not turned up to be a way to resolving or gaining information for our use-case but may be useful elsewhere.
        '''
        commitsObject = Repository(REPO_LINK).traverse_commits()
        for commit in commitsObject:
            if startDate != None and endDate != None:
                dateEnd = datetime.strptime(endDate,'%Y-%m-%d').date()
                dateStart = datetime.strptime(startDate,'%Y-%m-%d').date()
                dateDifferenceDays = (dateEnd - dateStart).days

            elif days != None:
                dateDifferenceDays = days
                dateEnd = datetime.now().date()
                dateStart = dateEnd - timedelta(days)

            if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:

                    if commit.author.name == userResearch:
                        acceptableFilesCounted = 0
                        for file in commit.modified_files:
                            if file.filename in self.getAcceptableFiles():
                                acceptableFilesCounted += 1
                            
                            break
                        if acceptableFilesCounted > alertCount:
                            print(f"found {acceptableFilesCounted} files touched in commit {REPO_LINK}/commit/{commit.hash} ")
                            print("-"*70)

    def reportLinesModifiedPerCommit(self, alertCount, userResearch, days=None, giveFilename = False, startDate=None, endDate=None, csvFormat=False):
        '''gets information about a single user and reports based on their commits - this function is for debugging purposes - objective is to find inaccuracies in reports
        
        primary focus is logging commits that have a high number of lines modified.
        
        note: this has turned out extremely valuable for our use-case.
        '''
        commitsObject = Repository(REPO_LINK).traverse_commits()
        for commit in commitsObject:
            if startDate != None and endDate != None:
                dateEnd = datetime.strptime(endDate,'%Y-%m-%d').date()
                dateStart = datetime.strptime(startDate,'%Y-%m-%d').date()
                dateDifferenceDays = (dateEnd - dateStart).days

            elif days != None:
                dateDifferenceDays = days
                dateEnd = datetime.now().date()
                dateStart = dateEnd - timedelta(days)

            if (dateEnd - datetime.fromisoformat(str(commit.committer_date)).date()).days < dateDifferenceDays:

                    if commit.author.name == userResearch:
                        if (commit.insertions+commit.deletions) > alertCount:
                            print(f"found {commit.insertions+commit.deletions} lines modified in commit {REPO_LINK}/commit/{commit.hash} ")
                            print("-"*70)



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
                print(f"specified maximum lines from any one commit is {args.maxLines}")
                a.exportDetailedReportToCsv(exportDir=args.exportCSV, maxLines=args.maxLines, startDate=args.start, endDate=args.end)
            else:
                a.exportDetailedReportToCsv(exportDir=args.exportCSV, maxLines=1000, startDate=args.start, endDate=args.end)
        else:
            if args.maxLines != None:
                print(f"specified maximum lines from any one commit is {args.maxLines}")
                a.exportDetailedReportToCsv(exportDir=args.exportCSV, maxLines=args.maxLines)
            else:
                a.exportDetailedReportToCsv(exportDir=args.exportCSV, maxLines=1000)


    # engineA = engine()
    # engineA.printAllCommitStats()
    # engineA.printReportToConsole(300)
    # engineA.printReportToConsole(1000, startDate="2021-1-1", endDate="2021-12-10")

    # engineA.reportAdditionsPerFile(days=300,userResearch="Kenneth")
    # engineA.reportFilesEdittedPerCommit(alertCount=3, userResearch="Kenneth", days=300)
    # engineA.reportLinesModifiedPerCommit(alertCount=100, userResearch="Kenneth", days=300)

