# from datetime import datetime, timedelta
# import time
# now = datetime.now()
# now_plus_10 = now + timedelta(seconds= 60)
# i=0
# while datetime.now()<now_plus_10:
#     time.sleep(10)
#     i+=1
#     print(i)

import urllib
import json
from urllib.request import urlopen
from datetime import date
import pandas as pd


link = "http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/getallfilename"
f = urlopen(link)
myfile = f.read()
files=json.loads(myfile)['Name']

today = date.today()

# dd/mm/YY
current_date= today.strftime("%Y-%m-%d")
print("current_date=", current_date)



filtered_lst=[]
for element in files:
    if current_date in element:
        filtered_lst.append(element)

print(filtered_lst)
filenames=[]
for file in filtered_lst:
        filename = file.split("/")[2]
        print(filename) 
        filenames.append(filename)



print(filenames)
sl=list(range(1,len(filenames)+1)) 
print(sl)   



df = pd.DataFrame(
{'SL' : sl,
    'filenames' : filenames
print(df)  
json_records = df.reset_index().to_json(orient ='records')
data = []
data= json.loads(json_records)
context = {'f': data, 't':data_1, 'g':data_2, 'y':data_3}
# print(files)
# if 'Resources/Results/2022-01-12PredictionReport.csv' in files:
#     print('True')
