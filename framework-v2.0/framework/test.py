import json
import urllib.request
import requests
import random
from bs4 import BeautifulSoup
def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]
    return random.choice(uastrings)
#Fakes header otherwise 403 & Formats Request w/ URL & Fake Headers Otherwise Denied & Decodes Response as Usually contains unicode characters  & Loads Beautiful Soup & Returns
webworker = lambda teamLink: BeautifulSoup(urllib.request.urlopen(urllib.request.Request(teamLink, headers={'User-Agent': GET_UA(),'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'none','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'})).read().decode("utf-8"), 'html.parser')

html=webworker("https://www.csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/update")















# import urllib.request

# get_url= urllib.request.urlopen('https://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/update')

# print("Response Status: "+ str(get_url.getcode()) )

# import requests

# url = 'https://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/update'
# #redirect(url)
# x = requests.get(url)
# print(x.status_code)