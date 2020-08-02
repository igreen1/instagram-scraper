"""
Hey Everyone!
This program can be used to scrape photos from any Instagram account (Offcourse, only if you follow that account or it’s an open account) and write the photo description for each photo to Excel Sheet.
"""
__author__ = "Darshan Majithiya"
#modified by Ian Green to adapt to the new Instagram website and thes specifics of my program 
__email__ = "darsh2115@gmail.com"


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import sys
import os
import requests
import shutil
from xlsxwriter import Workbook

import traceback
import csv


class Scraper:

    def __init__(self, username, password):
        """
        Initializes the driver, sets the username and password to use and navigates to instagram.com
        """
        self.username = username
        self.password = password
        #self.driver = webdriver.Chrome('chromedriver_linux64/chromedriver') # I'm using linux so firefox is better. you do you tho
        self.driver = webdriver.Firefox(executable_path="/home/augustus/Documents/gaydar/src/chromedriver_linux64/geckodriver")
        self.main_url = 'https://www.instagram.com'
        
        # check the internet connection and if the home page is fully loaded or not. 
        try:
            self.driver.get(self.main_url)
            WebDriverWait(self.driver, 10).until(EC.title_is('Instagram'))
        except TimeoutError:
            print('Loading took too much time. Please check your connection and try again.')
            sys.exit()

    def run_predfined(self, download_directory, to_download = "to_download.csv"):
        """
        Download the accounts listed in {to_download}.csv to {download_directory} 
        """

        #get through intro pages
        self.login()
        self.close_dialog_box()

        user_list = [] #the list of users to download

        #get path to to_download.csv

        to_download_path = os.path.join(download_directory, to_download)

        #fill user_list
        #TODO: don't locally store the users to save space :)
        try:
            with open(to_download_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                     #set our target up
                    
                    self.target_username = row[0]

                    try:
                        #go to their profile (no point doing all this if we can't access it/doesn't exist)
                        self.open_target_profile()
                    except:
                        print(f"Unable to open {self.target_username}")
                        continue #okay, this account is a no go, NEXT

                    #set local storate folders
                    self.dir_setup(download_directory)

                    self.base_path = os.path.join(download_directory, self.target_username) # change it as per requirement
                    self.imagesData_path = os.path.join(self.base_path, 'images') # change it as per requirement 
                    self.descriptionsData_path = os.path.join(self.base_path, 'descriptions') # change it as per requirement

                    #scrape!
                    self.download()
                    line_count+=1
                
                print(f"Processed {line_count} accounts.")


        except IOError:
            #if file cannot be opened, either have user
            #   manually input or just exit the whole thing
            print("Unable to open {to_download}")
            choice = ""
            while choice != 'e' and choice != 'm':
                choice = input("Would you like to exit (e) or manually enter accounts (m)?:")
            if choice == 'e':
                return
            else:
                self.run(download_directory)
                return
        
        self.close()

    def run_predfined_deprecated(self, download_directory, to_download = "to_download.csv"):
        """
        Download the accounts listed in {to_download}.csv to {download_directory} 
        """

        #get through intro pages
        self.login()
        self.close_dialog_box()

        user_list = [] #the list of users to download

        #get path to to_download.csv

        to_download_path = os.path.join(download_directory, to_download)

        #fill user_list
        #TODO: don't locally store the users to save space :)
        try:
            with open(to_download_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    user_list.append(row[0])
                    line_count+=1
                
                print(f"Processed {line_count} accounts.")


        except IOError:
            #if file cannot be opened, either have user
            #   manually input or just exit the whole thing
            print("Unable to open {to_download}")
            choice = ""
            while choice != 'e' and choice != 'm':
                choice = input("Would you like to exit (e) or manually enter accounts (m)?:")
            if choice == 'e':
                return
            else:
                self.run(download_directory)
                return
        
        #download each user in user-list
        for user in user_list:
            #set our target up
            self.target_username = user

            try:
                #go to their profile (no point doing all this if we can't access it/doesn't exist)
                self.open_target_profile()
            except:
                print(f"Unable to open {self.target_username}")
                continue #okay, this account is a no go, NEXT

            #set local storate folders
            self.dir_setup(download_directory)

            self.base_path = os.path.join(download_directory, self.target_username) # change it as per requirement
            self.imagesData_path = os.path.join(self.base_path, 'images') # change it as per requirement 
            self.descriptionsData_path = os.path.join(self.base_path, 'descriptions') # change it as per requirement

            #scrape!
            self.download()
    
        self.close()


    def run(self, download_directory):
        """
        This function will run the program, allowing for scraping of multiple
            instagram files without having to restart
        """

        self.login()
        self.close_dialog_box()

        userinput = ''
        #loop until user asks to exit
        while True:
            try:
                userinput = input("Enter profile to scrape: ")
                if(userinput == 'e' or userinput == 'exit'):
                    break

                #set our target up
                self.target_username = userinput

                #set local storate spots

                self.dir_setup(download_directory)

                self.base_path = os.path.join(download_directory, self.target_username) # change it as per requirement
                self.imagesData_path = os.path.join(self.base_path, 'images') # change it as per requirement 
                self.descriptionsData_path = os.path.join(self.base_path, 'descriptions') # change it as per requirement

                #scrape!
                self.open_target_profile()
                self.download()
            except Exception as e:
                traceback.print_tb(e.__traceback__)

        self.close()

    def close(self):
        self.driver.close()

    def download(self):
        # check if the directory to store data exists.
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        if not os.path.exists(self.imagesData_path):
            os.mkdir(self.imagesData_path)
        if not os.path.exists(self.descriptionsData_path):
            os.mkdir(self.descriptionsData_path)
        self.download_posts()

    def dir_setup(self, download_directory):
        """
        Takes a relative path and ensures each step of the path is created
            ex: downloads/test1/test2 will 
                1) check if downloads exists, create it if not
                2) check if test1 exists, create it if not
                3) check if test2 exists, create it if not
        """

        working_path = ''

        for next_folder in download_directory.split("/"):
            working_path += (next_folder)
            if not os.path.exists(working_path):
                os.mkdir(working_path)
            working_path += '/'

    def login(self):
        """
        Inputs the usernamen and password on the login landing page. Checks that it all works well and returns
        """

        # check if the login page is fully loaded or not.
        
        try:
            #WebDriverWait(self.driver, 10).until(EC.title_contains('Login')) #idk what the OG author was doing here,,,, probably old instagram
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located( (By.NAME, "username") ))
        except TimeoutError:
            print('Loading took too much time. Please check your connection and try again.')
            sys.exit()  

        try: 
            username_input = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[2]/div/label/input")
            #/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[2]/div/label/input
            #username_input = self.driver.find_element_by_xpath('//input[@name = "username"]')
        except Exception:
            print('Unable to find the username field.')
            sys.exit()    

        try: 
            password_input = self.driver.find_element_by_xpath('//input[@name = "password"]')
        except Exception:
            print('Unable to find the password field.')
            sys.exit() 
        
        # sending the credentials
        try:
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
        except Exception:
            print('Please check your connection and try again.')
            sys.exit()

        print('Logging in...')
        password_input.submit() 
        

        #check if login was successful
        #instagram redirects to ig.com/accounts

        try:
            #WebDriverWait(self.driver, 10).until(EC.title_contains('Login')) #idk what the OG author was doing here,,,, probably old instagram
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located( (By.XPATH, "/html/body/div[1]/section/main/div/div/div/section/div/div[1]/div/span") ))
        except TimeoutError:
            print('Loading took too much time. Please check your connection and try again.')
            sys.exit()  


        print('Login Successful!')

        
        

    def close_dialog_box(self):
        ''' Close the Notification Dialog '''
        try:
            close_btn = self.driver.find_element_by_xpath('//button[text()="Not Now"]')
            close_btn.click()
        except Exception:
            pass 


    def open_target_profile(self):  
        target_profile_url  = self.main_url + '/' + self.target_username
        print('Redirecting to {0} profile...'.format(self.target_username))
        
        # check if the target user profile is loaded. 
        try:
            self.driver.get(target_profile_url) 
            WebDriverWait(self.driver, 10).until(EC.title_contains(self.target_username))
        except TimeoutError:
            print('Some error occurred while trying to load the target username profile.')
            sys.exit()  
        

    def load_fetch_posts(self):
        '''Load and fetch target account posts'''

        image_list = [] # to store the posts

        # get the no of posts
        try:
            no_of_posts = str(self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span").text).replace(',','')
            #no_of_posts = str(self.driver.find_element_by_xpath('//span[@id = "react-root"]//header/section/ul/li//span[@class = "g47SY "]').text).replace(',', '') 
            self.no_of_posts = int(no_of_posts)
            print('{0} has {1} posts'.format(self.target_username, self.no_of_posts))   
        except Exception as e:
            print('Some exception occurred while trying to find the number of posts.')
            sys.exit()

        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_images = soup.find_all('img', attrs = {'class': 'FFVAD'}) 
        
            for img in all_images:
                if img not in image_list:
                    image_list.append(img)

            if self.no_of_posts > 12: # 12 posts loads up when we open the profile
                no_of_scrolls = round(self.no_of_posts/12) + 6 # extra scrolls if any error occurs while scrolling.

                # Loading all the posts
                print('Loading all the posts...')
                for __ in range(no_of_scrolls):
                    
                    # Every time the page scrolls down we need to get the source code as it is dynamic
                    self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(2) # introduce sleep time as per your internet connection as to give the time to posts to load
                    
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    all_images = soup.find_all('img') 
        
                    for img in all_images:
                        if img not in image_list:
                            image_list.append(img)
        except Exception as e:
            raise e
            print('Some error occurred while scrolling down and trying to load all posts.')
            sys.exit()  
        
        return image_list

    
    def download_descriptions(self, image_list):
        ''' Writing the descriptions in excel file '''
        print('writing the descriptions to excel...')
        workbook = Workbook(os.path.join(self.descriptionsData_path, 'descriptions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row, 0, 'Image name')       # 3 --> row number, column number, value
        worksheet.write(row, 1, 'Description')
        worksheet.write(row, 2, 'URL')
        row += 1
        for index, image in enumerate(image_list, start = 1):
            filename = 'image_' + str(index) + '.jpg'
            try:
                description = image.get('alt')
                url = image.get('src')
            except KeyError:
                description = 'No caption exists'

            if description == '':
                description = 'No caption exists'

            worksheet.write(row, 0, filename)
            worksheet.write(row, 1, description)
            worksheet.write(row, 2, url)
            row += 1
        workbook.close()


    def download_posts(self):
        ''' To download all the posts of the target account ''' 

        image_list = self.load_fetch_posts()
        self.download_descriptions(image_list)
        no_of_images = len(image_list)
        print("There are " + str(no_of_images) + " number of images")
        for index, img in enumerate(image_list, start = 1):
            filename = 'image_' + str(index) + '.jpg'
            image_path = os.path.join(self.imagesData_path, filename)
            link = img.get('src')
            if(not "http" in link):
                continue
            print(link)
            response = requests.get(link, stream = True)
            print('Downloading image {0} of {1}'.format(index, no_of_images))
            try:
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)
            except Exception as e:
                print(e)
                print('Couldn\'t download image {0}.'.format(index))
                print('Link for image {0} ---> {1}'.format(index, link))
        print('Download completed!')
