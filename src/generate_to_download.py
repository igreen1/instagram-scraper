"""
This program will generate the accounts that need to be downloaded and store them in to_download.csv (name change from previous versions!)
    Ideally, this will eliminate the need for the user to input the names twice and keep track of what is downloaded
"""

import os
import csv


def generate_accounts(dir_loc, manifest_name = "manifest.csv", to_download_name = "to_download.csv"):
    """
    Will check a directory for its manifest.csv
    then go through the contents looking to see if a similar directory exists
    if not,,,, do a lil output and add it to to_download.csv 
    place to_download.csv in the same dir as manifest.csv (keep it all contained)
    """

    #check directory
    if not os.path.exists(dir_loc):
        print("Error in generate accounts: no such directory")
        return

    #check manifest
    mani_path = os.path.join(dir_loc, manifest_name)
    if not os.path.exists(mani_path):
        print("Error in generate_accounts: manifest missing")

    #create and clear to_download.csv ('w' clears the file)
    download_list_path = os.path.join(dir_loc, to_download_name)
    to_download = open(download_list_path, "w")

    #open manifest. This file could be massive, so load one at a time :)

    with open(mani_path) as mani_file:
        csv_reader = csv.reader(mani_file, delimiter=',')

        #for debugging and the like
        line_count = 0
        missing_count = 0
        found_count = 0

        for row in csv_reader:

            #get the username and then find the folder it should correspond to
            username = row[0]
            user_path = os.path.join(dir_loc,username)

            #if no correpsonding folder, add it download
            if not os.path.exists(user_path):
                to_download.write(username+"\n")
                missing_count += 1
            else:
                found_count+=1

            line_count += 1

    to_download.close()