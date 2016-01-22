'''
TO-DO:
- 
- 
- Completely rewrite comments 
'''
'''
Copyright (c) 2016 Michael Stebbins
Based on code from KainokiKaede (https://gist.github.com/KainokiKaede/7251872)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

USAGE
 1. Use movesjson2text.py to generate text file of threshold-exceeding walks, runs, bikes
 2. Set INPUT_FILENAME below to the name of the text file generated
 3. Ensure .config file has example text replaced with your actual MongoLab URL and DB name
 4. Run script. All lines from text file will be entered as separate exercise events
     into Mongolab database.
 5. Run reports in Nightscout to see your exercise data on your day-to-day plots
 6. Keep fighting the good fight, and kicking diabetes' %$$!
'''

# IMPORTS
#---------------------------------------------------------------------------------------------------
from pymongo import MongoClient
import time
import datetime


# USER INPUTS
#---------------------------------------------------------------------------------------------------
INPUT_FILENAME = 'testoutput.txt'


# FUNCTIONS
#---------------------------------------------------------------------------------------------------
def convert_time_to_utc(input_string):
    # remove the utc offset string from the main string
    create_time_base = input_string[0:19]
    time_utc = datetime.datetime.strptime(create_time_base,'%Y-%m-%d %H:%M:%S')
    # change the utc datetime to the appropriate string
    datetime_str = datetime.datetime.strftime(time_utc,'%Y-%m-%dT%H:%M:%S.000Z')
    return datetime_str


def process_bolusnormal(input_line):
    parsed_line = input_line.split(',')
    datetime_str = convert_time_to_utc(parsed_line[1])
    bolus = parsed_line[2]
    post = {
            "eventType":"Meal Bolus",
            "enteredBy":"computer",
            "insulin": bolus,
            "units": "mg/dL",
            "created_at":datetime_str
            }    
    print(post)
    return post


def process_boluswizardbolusestimate(input_line):
    parsed_line = input_line.split(',')
    datetime_str = convert_time_to_utc(parsed_line[1])
    bg    = int(parsed_line[2])
    carbs = parsed_line[3]
    bolus = parsed_line[4]
    
    temp_dict = {}

    if carbs is not '0':
        temp_dict["carbs"] = carbs

    if bg is not 0:
        temp_dict["glucose"] = bg
        temp_dict["glucoseType"] = "Finger"

    if bolus is not '0':
        temp_dict["insulin"] = bolus
        temp_dict["units"] = "mg/dl"
  
    temp_dict["eventType"] = "Meal Bolus"
    temp_dict["enteredBy"] = "computer"
    temp_dict["created_at"] = datetime_str

    post = temp_dict
    print(post)
    return post

# TODO: flesh out these functions
def process_rewind(input_line):
    parsed_line = input_line.split(',')
    datetime_str = convert_time_to_utc(parsed_line[1])
    post = {
            "eventType":"Site Change",
            "enteredBy":"computer",
            "created_at":datetime_str
            }    
    print(post)
    return post


def process_bgcapturedonpump(input_line):
    parsed_line = input_line.split(',')
    datetime_str = convert_time_to_utc(parsed_line[1])
    bg = int(parsed_line[2])
   
    post = {
            "eventType": "BG Check",
            "enteredBy":"computer",
            "glucose": bg,
            "glucoseType": "Finger",
            "units": "mg/dL",
            "created_at":datetime_str
            }    
    print(post)
    return post


def process_changetempbasalpercent(input_line):
    parsed_line = input_line.split(',')
    datetime_str = convert_time_to_utc(parsed_line[1])
    temp_basal_percent = int(parsed_line[2])
    temp_basal_duration = int(parsed_line[3])
    
    # pump reports absolute percent, nightscout wants delta percent
    # i.e., 150(%) temp basal on pump is entered as 50(%) in nightscout
    temp_basal_percent = temp_basal_percent - 100
    if temp_basal_percent < -100:
        print ('temp basal rate is impossible, must be wrong')
    else:
        post = {
                "eventType": "Temp Basal",
                "enteredBy":"computer",
                "duration": temp_basal_duration,
                "percent": temp_basal_percent,
                "created_at":datetime_str
                }    
        print(post)
        return post


# MONGOLAB DATABASE LOG-IN INFO PULLED FROM CONFIG FILE (CREATE YOUR OWN LIKE IN EXAMPLE)
with open('.config') as f:
    config = f.read().splitlines()
MONGO_URL = 'mongodb://DataIn:g8cr3Xyvg9h8@ds054298.mongolab.com:54298/mikestebbinsdb2'
DB_NAME = 'mikestebbinsdb2'
# MONGO_URL = config[0]
# DB_NAME = config[1]

#-----------------------------------------------------------------------------
# MAIN FUNCTION
#-----------------------------------------------------------------------------
print('----------------------------------------------------------------------')
time_then = time.time()

try:
    DBclient = MongoClient(MONGO_URL)
    DB = DBclient[DB_NAME]
    COLLECTION_TREATMENTS = DB['treatments']
    print("connected to MongoDB")
except:
    print ('can not connect to DB make sure MongoDB is running')

time.sleep(0.1)
   
try:
    number_of_entries = COLLECTION_TREATMENTS.count()
    print ('number of posts already existing = ',number_of_entries) 
except Exception:
    print ('error: could not count posts for some reason or another')
    number_of_entries = 0
print()         
file = open(INPUT_FILENAME, 'r')

#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------
# First, parse each line by commas and convert times to UTC, append to list

# Then, sort that list by time/date

# Then, compare delta times line by line, if some are identical or nearly (bolusnormal
# and boluswizardestimate, grab what is needed, toss the rest, make one line)



counter = 0

for line in file:
    if '***' in line:
        print('skipping header line')
    else:
        if 'BolusNormal' in line:
            post = process_bolusnormal(line)
            counter = counter + 1

        if 'BolusWizardBolusEstimate' in line:
            post = process_boluswizardbolusestimate(line)
            counter = counter + 1

        if 'Rewind' in line:
            post = process_rewind(line)
            counter = counter + 1

        if 'BGCapturedOnPump' in line:
            post = process_bgcapturedonpump(line)
            counter = counter + 1

        if 'ChangeTempBasalPercent' in line:
            post = process_changetempbasalpercent(line)
            counter = counter + 1
            
        post_id = COLLECTION_TREATMENTS.insert_one(post) 
    
time_now = time.time()
print()
print('time taken =',time_now-time_then,'seconds')
print(counter,' posts added to DB')
          
file.close()
DBclient.close()