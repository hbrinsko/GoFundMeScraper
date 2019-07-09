import requests
import pyexcel as pe
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import csv
import re
from datetime import datetime

class Text:
    def __init__(self, body):
        self.body = body

    def calculate_sentiment(self, analyzer):
        vs = analyzer.polarity_scores(self.body)
        return(vs["compound"])
        
    def calculate_length(self):
        return len(self.body.strip().lower().split())


class Goal:
    def __init__(self,raised, goal):
        self.raised = raised
        self.goal = goal

    def pct_raised(self):
        if self.goal is not 0:
            pct = round(self.raised/self.goal,2)
            return float(pct)
        else:
            return self.goal

class Campaign:
    def __init__(self, url, campaignTitle, goal, shareCount, campaignDesc, donorCount, timePeriod):
        self.url = url
        self.campaignTitle = campaignTitle
        self.goal = goal
        self.shareCount = shareCount
        self.campaignDesc = campaignDesc
        self.donorCount = donorCount
        self.timePeriod = timePeriod

def clean_goal(goalText):
    if ' of ' in goalText:
        raised, goal = goalText.strip('\n').rstrip(' goal').replace('$', '').replace(',', '').split(' of ')
        raised = int(raised.replace(' ','').strip('\n'))
        goal = goal.replace(' ','').strip('\n')
    else:
        goal = goalText.strip('\n').rstrip(' goal').replace('$', '').replace(',', '')
        raised = 0

    thousand = 'k'
    million = 'M'
    if thousand in goal:
        goal = float(goal.replace('k',''))*1000
    elif million in goal:
        goal = float(goal.replace('M',''))*1000000
    else:
        goal = float(goal)

    return raised, goal

def clean_share_count(shareCountText):
    if shareCountText:
        shareCountText = shareCountText.text.replace(' ','').strip('\n')
        if 'k' in shareCountText:
            shareCountText = float(shareCountText.replace('k',''))*1000
    else:
        shareCountText = 0
    return int(shareCountText)

def clean_donor_count(donorCountText):
    if 'Campaign created ' in donorCountText:
        if 'month' in donorCountText:
            time, suffix = donorCountText.replace('Campaign created ','').split(' month')
            time = time.replace(' ','').strip('\n')
            donorCountText = 0
        elif 'day' in donorCountText:
            time, suffix = donorCountText.replace('Campaign created ','').split(' day')
            time = time.replace(' ','').strip('\n')
            donorCountText = 0
    else:
        donorCountText, time = donorCountText.replace('Raised by ','').split(' in ')
        donorCountText = donorCountText.replace(' ','').replace(',','').strip('\n').replace('people','').replace('person','')
        time = time.replace(' ','').strip('\n')
    return(int(donorCountText), time)


def generate_urls(city, state, urls):
    url = "https://www.gofundme.com/search/us/" +  city + "-" + state + "-" "fundraising"
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    data = soup.findAll('div',attrs={'class':'react-campaign-tile-details'})
    for div in data:
      links = div.findAll('a')
      for a in links:
        this_link = a['href']
        if this_link not in urls and this_link != '':
            urls.append(this_link)
    return urls

def scrape():
    urls = []
    campaigns = []
    analyzer = SentimentIntensityAnalyzer()

    #Place (city, stateAbbreviation) tuples in a list that you would like to be scraped
    locations = [["austin","tx"], ["san-antonio", "tx"], ["dallas", "tx"], ["houston", "tx"], ["fort-worth","tx"], ["el-paso", "tx"], ["arlington", "tx"]]    
    for city, state in locations:
        generate_urls(city, state, urls)

    for url in urls:
        print(url)
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "lxml")

        #Exclude archived campaigns
        active = soup.find('div', class_="var-width-column")
        if active:
            if "no longer active" in active.text:
                print(url)
                break

        #Grabbing title 
        title = soup.find('h1', class_='campaign-title')
        if title is None:
            ctitle=Text('')
        else:
            ctitle = Text(title.text)

        
        #Grabbing goal info
        goal_class = soup.find('h2', class_='goal')
        if goal_class is None:
            cgoal = Goal(0, 0)
        else:
            raised, goal = clean_goal(goal_class.text)
            cgoal = Goal(raised, goal)

        #Grabbing share count
        cShareCount = clean_share_count(soup.find('strong', class_='js-share-count-text'))

        #Grabbing description
        desc = soup.find('div', class_='co-story')
        if desc is None:
            cDesc = Text('')
        else:
            desc = re.sub('\\s+',' ',desc.text)
            cDesc = Text(desc)

        #Grabbing donor count and time spent fundraising
        donor_count = soup.find('div', class_='campaign-status text-small')
        if donor_count is None:
            donor = ''
            time = ''
        else:
            donor, time = clean_donor_count(donor_count.text)



        c = Campaign(url, ctitle, cgoal, cShareCount, cDesc, donor, time)
        cData = {
            "url": c.url,
            "title": c.campaignTitle.body,
            "title-length": c.campaignTitle.calculate_length(),
            "title-sentiment": c.campaignTitle.calculate_sentiment(analyzer),
            "description": c.campaignDesc.body,
            "description-length": c.campaignDesc.calculate_length(),
            "description-sentiment": c.campaignDesc.calculate_sentiment(analyzer),
            "share-count": c.shareCount,
            "donor-count": c.donorCount,
            "raised": c.goal.goal,
            "pct-goal-met": c.goal.pct_raised()
        }

        campaigns.append(cData)
    return campaigns