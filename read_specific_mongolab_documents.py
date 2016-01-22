# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 13:54:34 2015

@author: mstebbins
"""
from pymongo import MongoClient
import time
from bson.objectid import ObjectId
import ast
from random import randint

# Set to True during testing, otherwise leave false
resetParams = True
# Used to toggle the boolean telling the script where to pull the last object ID moved from
useParametersdb = True
# set script to testing or Real data
TESTorREAL = 'TEST'

timeBetweenLoops = 0.5

# MongoLab credentials, for accessing MongoLab DB via Azure             
MongoURL = 'mongodb://DataIn:q4UnAZfl6oi1XHKHRnGgfiLr@ds046818-a0.mongolab.com:46818,ds046818-a1.mongolab.com:46816/connectedobjdb?replicaSet=rs-ds046818'
DBname = 'connectedobjdb'

# ------- End of Setup -----------------------------------------------------------------
print('---------------------------------------------------------------------------------')

#Connect to MongoLab DB
try:
    DBclient = MongoClient(MongoURL)
    DB = DBclient[DBname]
    
    if TESTorREAL == 'TEST':
        rawDatadb = DB['rawDataTEST']
        formattedDatadb = DB['formattedDataTEST']
        parametersdb = DB['parametersTEST']
        faultsdb = DB['faultsTEST']
    if TESTorREAL == 'REAL':
        rawDatadb = DB['rawData']
        formattedDatadb = DB['formattedData']
        parametersdb = DB['parameters']
        faultsdb = DB['faults']

    print("connected to MongoDB")
    time.sleep(0.1)
except:
    print ('can not connect to DB make sure MongoDB is running')
    time.sleep(0.1) 
    

# Obtain all posts in RawDB with an Object ID greater than the last moved       
#formatList = list(rawDatadb.find(({'_id': {'$gt':ObjectId('56380002f2d770080f735d2b')}})))
#formatList = list(rawDatadb.find(({'_id': ObjectId('56380002f2d770080f735d2b')})))
formatList = list(rawDatadb.find(({'_id': ObjectId('5638000af2d770080f735d2c')})))
print ('lenght of list=', len(formatList))

print(formatList[0])

BigList = [formatList[0]]

for doc in BigList:
    try:  # prevent erroring out and quitting due to improperly formatted doucment         
        # Convert RawDB objectID into a separate entry in formatted DB (source tracking)           
        objectid = str(doc['_id'])
        generationDateTime = doc['_id'].generation_time
        timestamp = generationDateTime.strftime("%Y-%m-%dT%H:%M:%S.%f")
        dataInput = ast.literal_eval(doc['payload'])
    
        # Convert original RawDB status message into entry for formatted DB            
        message = dataInput['MESSAGE']
        productID = dataInput['ID']
        productLocation = dataInput['LOCATION']
    #            print(dataInput)
    #            print(message)
    #            print(productID)
    #            print(productLocation)
    #            print(timestamp)
    except Exception:
        print ('POTENTIALLY IMPROPERLY-FORMATTED DOCUMENT')
        productID = 'XXXXXX'
        print (doc)
#        continue
    
print('do other things')