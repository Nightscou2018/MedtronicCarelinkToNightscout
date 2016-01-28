'''
TO-DO:
- 
- 
- completely rewrite comments
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
 1. Go to: http://moves-export.herokuapp.com/
 2. Authenticate by putting PIN number into Moves app on phone
 3. Pick export from date, and hit Start Export! button
 4. Once json text is done loading, copy text from output box
 5. Go to http://jsonlint.com/, paste in code, and hit Validate
    jsonlint will help identify problems in the file (extra commas, incomplete
    bracets, etc.) Delete out these extra elements until you have valid json.
 6. Copy valid json text from jsonlint, paste into text file in python directory.
 7. Put that filename in as INPUT_FILE below.
 8. Check all USER INPUTS below, set to appropriate values for you
 9. Run this script to generate text file of walks, runs, and bikes exceeding
    the threshold seconds set in INPUTS, with activity start time in UTC time.
10. Finally, open and run textToMongo.py to upload output file to MongoLab.
'''
'''
DATA FORMATS:
list_of_days = [date,walking steps, cycle miles, run miles, [walk segments],[bike segments],[run segments]]
[walk segments] = [['Walk','minutes','steps','start time Local',start time UTC],[next walk segment]]
[bike segments] = [['Bike','minutes',meters,'start time Local',start time UTC],[next bike segment]]
[run segments] = [['Run','minutes',meters,'start time Local',start time UTC],[next run segment]]

[list_walks] = [["Walk",duration_min_str,'steps',duration_secs,steps,time_start_local_str,time_start_utc,time_end_utc]]
[list_bikes] = [["Bike",duration_min_str,'dist_miles',duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc]]   
[list_runs] = [["Run",duration_min_str,'dist_miles',duration_secs,dist_miles,time_start_local_str,time_start_utc,time_end_utc]]   
'''

# IMPORTS
#---------------------------------------------------------------------------------------------------
import datetime
from dateutil import tz


# CONSTANTS
#---------------------------------------------------------------------------------------------------

ZONE_FROM = tz.gettz('America/Los_Angeles')  # set to timezone that you live in
ZONE_TO = tz.gettz('UTC')     # to convert timzezones from UTC to Pacific
    # timezone names: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
search_strings_list = ['BolusNormal',
                       'BolusWizardBolusEstimate',
                       'Rewind',
                       'BGCapturedOnPump',
                       'BolusSquare',
                       'ChangeTempBasalPercent']


# USER INPUTS
#---------------------------------------------------------------------------------------------------
INPUT_FILE = 'CareLink-Export-1451459738062.csv'
OUTPUT_FILE = 'testoutput.txt'


# FUNCTIONS
#---------------------------------------------------------------------------------------------------

def clean_input_file_header_lines(input_list):
    # remove the first 11 lines, as they are unused header data
    del input_list[0:11]
    return input_list
    

def create_list_from_input_text(INPUT_FILE):
    input_list = []
    with open(INPUT_FILE,newline='') as file:
        for line in file:
            input_list.append(line) 
        input_list = clean_input_file_header_lines(input_list)
        return input_list   


def parse_list_for_pertinent_lines(input_list):
    input_list_parsed_by_strings = []
    for line in input_list:
        for i in range (0, len(search_strings_list)):
            if search_strings_list[i] in line:
                input_list_parsed_by_strings.append(line)
    return input_list_parsed_by_strings


def create_list_of_pertinent_lists(input_list,search_strings_list):
    # create list of lists, length = to the number of strings being searched for
    list_of_pertinent_lists = [[] for x in range(len(search_strings_list))]
    j = 0

    for i in range (0, len(search_strings_list)):
        list_of_pertinent_lists[j] = []

        for line in input_list:
            if search_strings_list[i] in line:
                list_of_pertinent_lists[j].append(line)
        j = j + 1
    return list_of_pertinent_lists


def convert_to_utc_timedate(input_timedate):
    # determine if month, date, or hour is single digit instead of zero-padded, fix if so
    # example: 1/1/15 3:24:48 should become 01/01/15 03:24:48
    if input_timedate.find('/') < 2:  # between month and date
        input_timedate = '0'+input_timedate[0:]
    if input_timedate.find('/',3) < 5:  # between date and year
        input_timedate = input_timedate[0:3]+'0'+input_timedate[3:]
    if input_timedate.find(':') < 11:  # between hour and minute
        input_timedate = input_timedate[0:11]+'0'+input_timedate[11:]

    time_local = datetime.datetime.strptime(input_timedate,'%m/%d/%y %H:%M:%S')            
    time_utc = time_local.replace(tzinfo=ZONE_FROM)
    time_utc = time_utc.astimezone(ZONE_TO)
    return time_utc


def parse_data_type_00(master_parsed_list,list_of_pertinent_lists):
    # [0] BolusNormal
    for line in list_of_pertinent_lists[0]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3]
        timestamp_utc = convert_to_utc_timedate(timestamp)   
        # try:
        temp = [x for x in parsed_line if 'AMOUNT=' in x]
        temp = temp[0].split('=')
        bolus_delivered = temp[1]
        result = ['BolusNormal',timestamp_utc,bolus_delivered]
        print(result)
        master_parsed_list.append(result)
        # except:
        #     print(parsed_line)
        #     counter = counter + 1

    # print('unrecorded BolusNormal lines =',counter)
    return master_parsed_list


def parse_data_type_01(master_parsed_list,list_of_pertinent_lists):
    # [1] BolusWizardBolusEstimate
    # BG_INPUT=0, BG_UNITS=mg dl, CARB_INPUT=35, CARB_UNITS=grams, CARB_RATIO=12, INSULIN_SENSITIVITY=50, BG_TARGET_LOW=80, BG_TARGET_HIGH=120, BOLUS_ESTIMATE=2.9, CORRECTION_ESTIMATE=0, FOOD_ESTIMATE=2.9, UNABSORBED_INSULIN_TOTAL=0, UNABSORBED_INSULIN_COUNT=2, ACTION_REQUESTOR=paradigm link or b key
    for line in list_of_pertinent_lists[1]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3] 
        timestamp_utc = convert_to_utc_timedate(timestamp)
        # try:
        temp = [x for x in parsed_line if 'BG_INPUT=' in x]
        temp = temp[0].split('=')
        bg_input = temp[1]

        temp = [x for x in parsed_line if 'CARB_INPUT=' in x]
        temp = temp[0].split('=')
        carb_input = temp[1]

        temp = [x for x in parsed_line if 'BOLUS_ESTIMATE=' in x]
        temp = temp[0].split('=')
        bolus_estimate = temp[1]

        result = ['BolusWizardBolusEstimate',timestamp_utc,bg_input,carb_input,bolus_estimate]
        print(result)            
        master_parsed_list.append(result)
        # except:
        #     print(parsed_line)
        #     counter = counter + 1
    # print('unrecorded BolusWizardBolusEstimate lines =',counter)
    return master_parsed_list


def parse_data_type_02(master_parsed_list,list_of_pertinent_lists):
    # [2] Rewind
    for line in list_of_pertinent_lists[2]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3] 
        timestamp_utc = convert_to_utc_timedate(timestamp)
        result = ['Rewind',timestamp_utc]
        print(result)            
        master_parsed_list.append(result)       
    # print('unrecorded Rewind lines =',counter)
    return master_parsed_list    


def parse_data_type_03(master_parsed_list,list_of_pertinent_lists):
    # [3] BGCapturedOnPump
    for line in list_of_pertinent_lists[3]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3] 
        timestamp_utc = convert_to_utc_timedate(timestamp)
        # try:
        temp = [x for x in parsed_line if 'AMOUNT=' in x]
        temp = temp[0].split('=')
        bg_captured_on_pump = temp[1]          
        result = ['BGCapturedOnPump',timestamp_utc,bg_captured_on_pump]
        print(result)            
        master_parsed_list.append(result) 
        # except:
        #     print(parsed_line)
        #     counter = counter + 1
    # print('unrecorded BGCapturedOnPump lines =',counter)
    return master_parsed_list    


def parse_data_type_04(master_parsed_list,list_of_pertinent_lists):
    # [4] BolusSquare
    for line in list_of_pertinent_lists[4]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3]
        timestamp_utc = convert_to_utc_timedate(timestamp)

        if ('Dual/Square' in parsed_line) or ('Square' in parsed_line):          
            try:
                temp = parsed_line.index('Square')
            except:
                pass
            try:
                temp = parsed_line.index('Dual/Square')
            except:
                pass
            bolus_delivered = parsed_line[temp+2]
            bolus_duration = parsed_line[temp+3]

        else:
            # print(parsed_line)
            # counter = counter + 1 
            pass
        result = ['BolusSquare',timestamp_utc,bolus_delivered,bolus_duration]
        print(result)            
        master_parsed_list.append(result)         
    # print('unrecorded BolusSquare lines =',counter)
    return master_parsed_list    


def parse_data_type_05(master_parsed_list,list_of_pertinent_lists):
    # [5] ChangeTempBasalPercent
    for line in list_of_pertinent_lists[5]:
        parsed_line = line.split(',')
        timestamp = parsed_line[3]
        timestamp_utc = convert_to_utc_timedate(timestamp)

        # try:
        temp = [x for x in parsed_line if 'PERCENT_OF_RATE=' in x]
        temp = temp[0].split('=')
        basal_percent = temp[1]

        temp = [x for x in parsed_line if 'DURATION=' in x]
        temp = temp[0].split('=')
        duration = temp[1]
        duration_minutes = int((int(duration))/60000)

        result = ['ChangeTempBasalPercent',timestamp_utc,basal_percent,duration_minutes]
        print(result)            
        master_parsed_list.append(result) 

        # except:
        #     print(parsed_line)
        #     counter = counter + 1 
           
    # print('unrecorded ChangeTempBasalPercent lines =',counter)
    return master_parsed_list

def write_file_header_info(search_strings_list):
    out_file.write('***'+'BolusNormal,timestamp_utc,bolus_delivered_in_units\n')
    out_file.write('***'+'BolusWizardBolusEstimate,timestamp_utc,bg_input,carb_input,bolus_estimate\n')
    out_file.write('***'+'Rewind,timestamp_utc\n')
    out_file.write('***'+'BGCapturedOnPump,timestamp_utc,bg_captured_on_pump\n')
    out_file.write('***'+'BolusSquare,timestamp_utc,bolus_delivered,bolus_duration\n')
    out_file.write('***'+'ChangeTempBasalPercent,timestamp_utc,basal_percent,duration_minutes\n')
    

def write_to_text_file(input_list):
    for each in input_list:
        for list_value in each:
            out_file.write(str(list_value))
            out_file.write(',')
        out_file.write('\n')    

# MAIN
#---------------------------------------------------------------------------------------------------

input_list = create_list_from_input_text(INPUT_FILE)
input_list_parsed_by_strings = parse_list_for_pertinent_lines(input_list)

print('length of list parsed by strings =',len(input_list_parsed_by_strings))

list_of_pertinent_lists = create_list_of_pertinent_lists(input_list,search_strings_list)

# Parse each of the lists contained in list_of_pertinent_lists based on that data type's format
# Keep appending each item as a new list in the master list
master_parsed_list = []

# [0] BolusNormal
master_parsed_list = parse_data_type_00(master_parsed_list,list_of_pertinent_lists)
# [1] BolusWizardBolusEstimate
master_parsed_list = parse_data_type_01(master_parsed_list,list_of_pertinent_lists)
# [2] Rewind
master_parsed_list = parse_data_type_02(master_parsed_list,list_of_pertinent_lists)
# [3] BGCapturedOnPump
master_parsed_list = parse_data_type_03(master_parsed_list,list_of_pertinent_lists)
# [4] BolusSquare
master_parsed_list = parse_data_type_04(master_parsed_list,list_of_pertinent_lists)
# [5] ChangeTempBasalPercent
master_parsed_list = parse_data_type_05(master_parsed_list,list_of_pertinent_lists)

out_file = open(OUTPUT_FILE,'w')
write_file_header_info(search_strings_list)
write_to_text_file(master_parsed_list)
out_file.close()