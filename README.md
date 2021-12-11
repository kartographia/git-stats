this github metrics shows github statistics outputs



To use this library you must add a file named config.py that contains similar to the following:

#----------------------------------------------------------------
# the list of contributors and their relative github usernames
# Note: the key is the name that will be used in the report.
CONTRIBUTORS = {
    "person1": ["person1GithubCommitUsername1","person1GithubCommitUsername2"],
    "person2": ["person2GithubCommitUsername1"],
}
# where the current repository is located on your file system
LOCAL_PROJECT_DIRECTORY = "/home/<myusername>/<my main github directory>/<cloned repo folder>"

# The directories you wish to ignore for adding up lines changed
IGNORE_DIRECTORY = [".git", "temp", ".github", "target", "models", "data","lib"]

# the online url for the repository
REPO_LINK = "https://github.com/<username>/<repo>"

#---------------------------------------------------------------

