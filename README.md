

# Required Libraries
* python version 3+
* pydriller https://pypi.org/project/PyDriller/


# Running this project
Run this project via a command-line that has access to a python3 installation, enter the project directory where **stats.py** file is located and run the command with the following options: 

## Options
### note: -getAll and -nickname are optionally required which means that either one or the other must be used, but not both. 
* `-exportCSV <path/to/file.csv>` -- directory and filename with csv file extension to export to -- **required**
* `-getAll` -- get all of the repositories listed in config.py exported to one csv -- Default is False -- **optionally required**
* `-nickname` -- enter the repository nickname set in config.py to use (this contains all of the data needed to target the correct repository) -- **optionally required**
* `-start <m/d/y format date>` -- start date for querying GitHub repository (m/d/y format - if not declared all records will be returned) -- **optional**
* `-end <m/d/y format date>` -- end date for querying GitHub repository (m/d/y format - if not declared all records will be returned) --**optional**
* `-maxLines <int>` -- declare a maximum number of lines modified per tracked commit (default is 1000) -- **optional**
* `-v` -- verbose output -- **optional**
* `-useContributors` -- Instruct the script on whether to use the declared contributors to build the report -- Default is False **optional**




example: `python3 stats.py -exportCSV /home/kartographia/file.csv -nickname BlueWave -end 12/1/2021 -start 11/1/2021 -v`



# Other requirements for this project 
You will need to create a config.py file that has the following stored in a dictionary key-pair for each of the repositories you would like to track:
* the nickname for this repository group
* The repository link you would like to track - variable String REPO_LINK
* The repository location on your file system - variable String LOCAL_PROJECT_DIRECTORY
* The directories you wish to ignore when adding up the "modified lines" count - list object IGNORE_DIRECTORY

# Optional feature for this project 
* The list of nicknamed contributors and their relative GitHub Usernames - dictionary (key-value pairs) object CONTRIBUTORS

These will automatically be imported into the main script from your created `config.py` file when running the simple command in the command-line.

**See example config.py file below**

```
#------------------------------------------------------------------------------------
configGroup = {
    #------------------------ Project 1 ----------------------------------------
    # the list of contributors and their relative github usernames
    # Note: the key is the name that will be used in the report.
    # use command "git shortlog --summary --numbered --email" to get the usernames associated with each email.
    "project1Nickname":{
        "CONTRIBUTORS": {
            "person1": ["person1GithubCommitUsername1","person1GithubCommitUsername2"],
            "person2": ["person2GithubCommitUsername1"],
        },
        # where the current repository is located on your file system
        "LOCAL_PROJECT_DIRECTORY": "/home/<myusername>/<my main github directory>/<cloned repo folder>",

        # The directories you wish to ignore for adding up lines changed
        "IGNORE_DIRECTORY" :[".git", "temp", ".github", "target", "models", "data","lib"],

        # the online url for the repository
        "REPO_LINK": "https://github.com/<username>/<repo>"
    },

    #------------------------ Project 2 ----------------------------------------
    # the list of contributors and their relative github usernames
    # Note: the key is the name that will be used in the report.
    # use command "git shortlog --summary --numbered --email" to get the usernames associated with each email.
    "project2Nickname":{
        "CONTRIBUTORS": {
            "person1": ["person1GithubCommitUsername1","person1GithubCommitUsername2"],
            "person2": ["person2GithubCommitUsername1"],
        },
        # where the current repository is located on your file system
        "LOCAL_PROJECT_DIRECTORY": "/home/<myusername>/<my main github directory>/<cloned repo folder>",

        # The directories you wish to ignore for adding up lines changed
        "IGNORE_DIRECTORY" :[".git", "temp", ".github", "target", "models", "data","lib"],

        # the online url for the repository
        "REPO_LINK": "https://github.com/<username>/<repo>"
    },
    
    #------------------------ Project 3 ----------------------------------------
    "project3Nickname":{
        "CONTRIBUTORS": {
            "person1": ["person1GithubCommitUsername1","person1GithubCommitUsername2"],
            "person2": ["person2GithubCommitUsername1"],
        },
        # where the current repository is located on your file system
        "LOCAL_PROJECT_DIRECTORY": "/home/<myusername>/<my main github directory>/<cloned repo folder>",

        # The directories you wish to ignore for adding up lines changed
        "IGNORE_DIRECTORY" :[".git", "temp", ".github", "target", "models", "data","lib"],

        # the online url for the repository
        "REPO_LINK": "https://github.com/<username>/<repo>"
    },

    #------------------------ Project 4 (for use without -useContributors tag) ----------------------------------------
    "project4Nickname":{
        # where the current repository is located on your file system
        "LOCAL_PROJECT_DIRECTORY": "/home/<myusername>/<my main github directory>/<cloned repo folder>",

        # The directories you wish to ignore for adding up lines changed
        "IGNORE_DIRECTORY" :[".git", "temp", ".github", "target", "models", "data","lib"],

        # the online url for the repository
        "REPO_LINK": "https://github.com/<username>/<repo>"
    },
}
#------------------------------------------------------------------------------------

```


You can also rename this [config.py example file ](config.py.example) to config.py and add your details to the file.

