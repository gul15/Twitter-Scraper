"""
        A program that reads info about requests for startup on twitter. Takes username,password and required number of tweets as input
        then prints out the csv and html file of the tweets
        
        
        Yusuf Utku Gül
        gul.yusufutku@gmail.com
"""

import csv #csv operations
from time import sleep #waiting loading pages 
from selenium.webdriver.common.keys import Keys # selenium browser operations
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions
import pandas as pd # sort dataframe
import webbrowser #display result

def create_tweet(tweet_data):           # after getting the whole tweet data from web, save it as a tuple of information
    username = tweet_data.find_element_by_xpath('.//span').text
    try:                                #some promoted posts don't have handles or dates so try and throw exception
        handle = tweet_data.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except NoSuchElementException:
        return
    try:
        date = tweet_data.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comments = tweet_data.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    responds = tweet_data.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    text = comments + responds
    replies = tweet_data.find_element_by_xpath('.//div[@data-testid="reply"]').text
    retweets = tweet_data.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    likes = tweet_data.find_element_by_xpath('.//div[@data-testid="like"]').text
    
    tweet = (username, handle, date, text, replies, retweets, likes)
    return tweet  # return as tweet info

def scroll(driver):     #scrolls down on the page for new tweets
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    


tweet_list = []         # tweets 
tweet_ids = set()       #save tweet ids in set for duplicates
isinputexist = True     #true if previous data exists

try:    #  try if previous data exists, if so save their id's before searching
    with open('tweets.csv',encoding="utf-8") as input_file: 
        isinputexist = True
        prev_data = csv.reader(input_file)
        for row in prev_data:
            tweet_id = ''.join(row)
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                tweet_list.append(row)
except:
    isinputexist = False    #no previous info
    print("No previous data found, creating new file.")
        


#User inputs, login is required for scraping due to Twitter policy
#user ="utkgl33"
user = input("Enter username:")
#my_password = "L8tvB6k7YP.."
my_password = input("Enter password:")
#required_number = 1000 # minimum tweet number to collect
required_number = int(input("Enter required number of tweets:"))


    
options = EdgeOptions() #open browser using default settings, driver is necessary
options.use_chromium = True
driver = Edge(executable_path='driver/msedgedriver.exe',options=options) 


driver.get('https://twitter.com/login') # open login page
driver.maximize_window()


username = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]') #enter username
username.send_keys(user)
password = driver.find_element_by_xpath('//input[@name="session[password]"]') #enter password
password.send_keys(my_password)
password.send_keys(Keys.RETURN) # send login
sleep(2) # wait for load

driver.get('https://twitter.com/search?q=%22request%20for%20startup%22&src=typed_query&f=live') # go to twitter page for "request for startup"

sleep(3) #wait for load

prev_len = len(tweet_list)
 
finished_counter = 0 # if no tweets are added three consecutive times it might be end of the page

while len(tweet_list)<required_number+prev_len and finished_counter<3: # if length reaches to required or page ends, finish
    prev_length = len(tweet_list)
    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')
    for x in page_cards[-15:]:
        tweet = create_tweet(x)
        if tweet:
            tweet_id = ''.join(tweet)
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                tweet_list.append(tweet)
        # check scroll position
    print(len(tweet_list)-prev_len, "tweet collected")
    if prev_length == len(tweet_list):
        finished_counter += 1
    else:
        finishedcounter = 0
    scroll(driver) #scroll down the page for new tweets
    sleep(3)
# close the web driver
driver.close()



if not isinputexist: #write with headers, no csv exists before
    headers = ["User", "User Handle", "Post Date", "Content", "Replies", "Retweets", "Likes"]
    with open('tweets.csv', 'w', newline='',encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(headers)
        writer.writerows(tweet_list)
else: #only append new data
    with open('tweets.csv', 'w+', newline='',encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(tweet_list)    



df = pd.read_csv("tweets.csv",encoding="utf-8").fillna(0) # read csv file and assign nan to 0
df.sort_values(by=["Retweets","Likes","Replies","Post Date"],inplace=True, ascending=False) #sort values
html = df.to_html("tweets.html") # print out dataframe as html page
webbrowser.open("tweets.html", new=2)  #display html page on browser
















