from pydriller import Repository
from datetime import datetime
from config import CONTRIBUTORS
from config import BLUEWAVE_DIRECTORY
from config import IGNORE_DIRECTORY
from config import REPO_LINK
from pprint import pprint
from datetime import timedelta
import os
import csv

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
dmm_unit_complexity
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

    def getCommitsOfUsers(self,days=None, giveFilename = False, startDate=None, endDate=None, csv=False):
        '''gets the total commits of the users in config over the past days specified and prints them '''
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
        if csv == True:
            return statisticsString, loggedContributors, dateEnd, dateStart
        else:
            return statisticsString, loggedContributors


    def printReportToConsole(self,days=None, startDate=None, endDate=None):
        '''print the commits report to console '''
        if days != None:
            string1, contributorReport =  self.getCommitsOfUsers(days=days, csv=False)
        elif startDate and endDate != None:
            string1, contributorReport =  self.getCommitsOfUsers(startDate=startDate, endDate=endDate, csv=False)

        print(string1)
        pprint(contributorReport)


    def exportCommitsOfUsers(self,days=None, startDate=None, endDate=None):
        '''gets the total commits of the users in config over the past days specified and exports them to csv format'''
        string1, contributorReport,dateStart,dateEnd =  self.getCommitsOfUsers(days,datePicker=True,giveFilename=True, csv=True)

        with open(f'reports/activityReport{dateStart}___{dateEnd}.csv', 'w') as f:
            for key in contributorReport.keys():
                f.write("%s,%s\n"%(key,contributorReport[key]))




    def getAcceptableFiles(self):

        acceptableFiles = []
        for root, dirs, files in os.walk(BLUEWAVE_DIRECTORY):
            [dirs.remove(d) for d in list(dirs) if d in IGNORE_DIRECTORY]
            for file in files:
                acceptableFiles.append(file)
        return acceptableFiles
    
    
    def testCommitsOfUsersSize(self,days=None, giveFilename = False, startDate=None, endDate=None, csv=False, userResearch = None):
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
                            print("-"*70)
                            if file.filename in self.getAcceptableFiles():
                                if len(file.diff_parsed["added"]) > 300:
                                    print("found a big commit insert "+str(commit.insertions) + " filename "+file.filename)
                                    print("github commit link for viewing "+ f"{REPO_LINK}/commit/{commit.hash}")

                                    with open(f"temp/reports/exportedInsertionsCommit{datetime.now().date()}.txt","w+") as f:
                                        for line in file.diff_parsed["added"]:
                                            f.writelines(line[1])
                                            if "console.log" in line[1]:
                                                userResearchReport["total insertions"]["logging"] = userResearchReport["total insertions"]["logging"] + 1 

                                            elif "#" in line[1]:
                                                userResearchReport["total insertions"]["comments"] = userResearchReport["total insertions"]["comments"] + 1 
                                            
                                            elif (line[1].isspace() == True):
                                                pass

                                            else:
                                                userResearchReport["total insertions"]["code"] = userResearchReport["total insertions"]["code"] + 1 
                                
                                if len(file.diff_parsed["deleted"]) > 300:
                                    print("found a big commit delete "+str(commit.deletions)+ " filename "+file.filename)
                                    print("github commit link for viewing "+ f"{REPO_LINK}/commit/{commit.hash}")

                                    with open(f"temp/reports/exportedDeletionsCommit{datetime.now().date()}.txt","w+") as f:
                                        for line in file.diff_parsed["deleted"]:
                                            f.writelines(line[1])
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



if __name__ == "__main__":
    engineA = engine()
    # engineA.getNumberModifications()
    # engineA.printAllCommitStats()
    # engineA.printReportToConsole(300)
    # engineA.printReportToConsole(startDate="2021-12-1", endDate="2021-12-10")
    engineA.testCommitsOfUsersSize(days=300,userResearch="Kenneth")
    # engineA.exportCommitsOfUsers(10)
    # 
