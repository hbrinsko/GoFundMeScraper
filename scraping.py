import requests
import pyexcel as pe
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class Text:
    def __init__(self, body, length, sentiment):
        self.body = body
        self.length = length
        self.sentiment = sentiment

class Goal:
    def __init__(self,raised,goal):
        self.raised = raised
        self.goal = goal

    def pctRaised(self,raised,goal):
        pct = round(raised/goal,2)
        return (str(pct) + "%")

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
        time, suffix = donorCountText.replace('Campaign created ','').split(' month')
        time = time.replace(' ','').strip('\n')
        donorCountText = 0
    else:
        donorCountText, time = donorCountText.replace('Raised by ','').split(' in ')
        donorCountText = donorCountText.replace(' ','').replace(',','').strip('\n').replace('people','').replace('person','')
        time = time.replace(' ','').strip('\n')
    return(int(donorCountText), time)


def generate_urls(city, state, urls):
    url = "https://www.gofundme.com/mvc.php?route=category&term=" + city + "%2C" + state
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "lxml")
    data = soup.findAll('div',attrs={'class':'react-campaign-tile-details'})
    for div in data:
      links = div.findAll('a')
      for a in links:
        this_link = a['href']
        if this_link not in urls:
            urls.append(this_link)
    return urls

def sentiment_analyzer(s):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(s)
    return(vs["compound"])

def scrape():
    urls = []
    campagins = []
    #Place (city, stateAbbreviation) tuples in a list that you would like to be scraped
    locations = [("Austin", "TX")]    
    for city, state in locations:
        generate_urls(city, state, urls)

    for url in urls:

        req = requests.get(url)
        soup = BeautifulSoup(req.text, "lxml")

        #Grabbing title 
        title = soup.find('h1', class_='campaign-title')
        title = title.text

        length = len(title.strip().lower().split())
        desc_sent = sentiment_analyzer(title)
        ctitle = Text(title, length, desc_sent)
        
        #Grabbing goal info
        goal_class = soup.find('h2', class_='goal').text
        raised, goal = clean_goal(goal_class)
        cgoal = Goal(raised, goal)

        #Grabbing share count
        cShareCount = clean_share_count(soup.find('strong', class_='js-share-count-text'))

        #Grabbing description
        desc=soup.find('div', class_='co-story')
        desc =desc.text.strip('\n')

        length = len(desc.strip().lower().split())
        sent = sentiment_analyzer(desc)
        cDesc = Text(desc, length, sent)

        #Grabbing donor count and time spent fundraising
        donor, time = clean_donor_count(soup.find('div', class_='campaign-status text-small').text)

        c = Campaign(url, ctitle, cgoal, cShareCount, cDesc, donor, time)
        cData = {
            "url": c.url,
            "title": c.campaignTitle.body,
            "title-length": c.campaignTitle.length 
        }

        campagins.append(cData)
    return campagins