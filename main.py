"""
This project will scrape instagram (maybe more later) photos and descriptions 
"""

from src.instaScraper import Scraper
from src.generate_to_download import *
from src import *

import getpass


def scrape():
    """
    Scrape will run the instascraper
    This is a separate function since it SHOULD ONLY RUN ONCE
    we don't want to redownload everytime we add accounts to our machine learning
    in fact, one of my tasks is to eliminate redownloading entirely
    """
    
    
    #setup ig account
    user = input("Username: ")
    pwd = getpass.getpass()

    choice = inquire("Scrape from a list (l) or from an input (i)?")

    test = Scraper(user,pwd)
    if choice == 'l':

        #get download information
        download_path = input("Where would you like to download? (relative path preferred): ")
        if download_path == '':
            download_path = 'data'
        manifest_name = input("What is your manifest name (csv file)?: ")

        #generate download list
        if manifest_name == '':
            generate_accounts(download_path)
        else:
            generate_accounts(download_path, manifest_name)

        #run!
        test.run_predfined(download_path, "to_download.csv")
    elif choice == 'i':
        #just run it, input on the fly
        test.run(download_path)


#Input functions (more just a fun thing for me, totally an inefficient waste of time, lol)

def inquire(qn):
    #beefed up version of get input where it calculates the acceptable responses

    acceptable = []
    for i in range(0, len(qn)):
        if qn[i] == '(' and (i+2) < len(qn) and qn[i+2] == ')':
            acceptable.append(qn[i+1])
    
    #to make sure formatting conforms to my personal standards
    #first, remove in case i put the formatting in
    #this ensures we always start from an entirely bad state
    #which makes fixing it way easier since i know /everything/ is wrong
    qn = qn.rstrip(' ').rstrip(':').rstrip('?')
    #then append (since anywhere from 0-3 things were removed above)
    qn = qn + "?: "

    return get_input(qn, acceptable)

def get_input(qn, acceptable):
    #User input validation, super simple
    #tbd, i just got annoyed at writing the same while loop 10000000 times

    userInput = input(qn)
    while not userInput in acceptable:
        print("Acceptable inputs: " + ','.join(acceptable))
        userInput = input(qn)
    return userInput



if __name__ == "__main__":
    scrape()


