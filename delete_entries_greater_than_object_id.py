
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

MONGO_URL = 'mongodb://DataIn:g8cr3Xyvg9h8@ds054298.mongolab.com:54298/mikestebbinsdb2'
DB_NAME = 'mikestebbinsdb2'

DBclient = MongoClient(MONGO_URL)
DB = DBclient[DB_NAME]  
COLLECTION_TREATMENTS = DB['treatments']      

# TIMEDATE:                   OID:
# 2015-12-01T08:00:00.000Z    565d53800000000000000000
# 2016-01-01T00:00:00.000Z    5685c1800000000000000000
# 2016-01-20T00:00:00.000Z    569ece000000000000000000
# 2016-01-22T00:00:00.000Z    56a171000000000000000000
# 2016-01-23T00:00:00.000Z    56a2c2800000000000000000
# 2016-01-25T00:00:00.000Z    56a565800000000000000000

year   = 2016
month  = 1
date   = 26
hour   = 0
minute = 0
second = 0

generated_timestamp = datetime.datetime(year,month,date,hour,minute,second)

def seconds_since_epoch(datetime_object):
    return int(datetime_object.timestamp())
    
def create_object_id_from_timestamp(generated_timestamp):
    seconds = seconds_since_epoch(generated_timestamp)    
    oid = hex(seconds)[2:] + '0000000000000000'
    return oid
    
#def write_raw_greater_than_to_text_file(outputfilename,year,month,date,hour,minute,second):
#    generated_timestamp = datetime.datetime(year,month,date,hour,minute,second)
#    oid = create_object_id_from_timestamp(generated_timestamp)
#    print(generated_timestamp)
#    print (oid)
#    
#    posts = rawDatadb.count({'_id': {'$gt':ObjectId(oid)}})      
#    print('number of posts =',posts)
#    
#    with open(outputfilename,'w') as text_file:    
#        text_file.write('---------------------------------------------------------------------------------------------------------------------------------------\n')
#        header_line = 'rawDatadb posts after'+str(generated_timestamp)+' =\n'
#        text_file.write(header_line)    
#        print('------------------------------------------------------------------------------------------------------------')
#        print('rawDatadb posts after', generated_timestamp,' =')
#        cursor = rawDatadb.find({'_id': {'$gt':ObjectId(oid)}})
#        for doc in cursor:
#    #        print(doc)
#            text_file.write(str(doc))
#            text_file.write('\n')    
               
#posts = rawDatadb.count({'_id': {'$gt':ObjectId(oid)}})
#print('rawDatadb posts after',generated_timestamp,' =',posts)

#write_raw_greater_than_to_text_file(RAWtextfilename,2016,1,27,0,0,0)

# example AND query language:
# db.inventory.find( { $and: [ { price: { $ne: 1.99 } }, { price: { $exists: true } } ] } )

#posts = rawDatadb.count({'$and':[{'_id': {'$gt':ObjectId('569ece000000000000000000')}},{'_id': {'$lt':ObjectId('56a171000000000000000000')}}]})
#print('rawDatadb posts after 2016-01-20 and before 2016-01-22 =',posts)
#
#posts = rawDatadb.count({'_id': {'$gt':ObjectId('56a2c2800000000000000000')}})
#print('rawDatadb posts after 2016-01-23 =',posts)


#with open(RAWtextfilename,'w') as text_file:
    
#    text_file.write('---------------------------------------------------------------------------------------------------------------------------------------\n')
#    text_file.write('rawDatadb posts after 2016-01-20 and before 2016-01-22 =\n')    
#    print('------------------------------------------------------------------------------------------------------------')
#    print('rawDatadb posts after 2016-01-20 and before 2016-01-22 =')
#    
#    cursor = rawDatadb.find({'$and':[{'_id': {'$gt':ObjectId('569ece000000000000000000')}},{'_id': {'$lt':ObjectId('56a171000000000000000000')}}]})
#    for doc in cursor:
#        text_file.write(str(doc))
#        text_file.write('\n')
        
#    text_file.write('---------------------------------------------------------------------------------------------------------------------------------------\n')
#    text_file.write('rawDatadb posts after to 2016-01-23 =\n')    
#    print('------------------------------------------------------------------------------------------------------------')
#    print('rawDatadb posts after 2016-01-23 =')
#    
#    cursor = rawDatadb.find({'_id': {'$gt':ObjectId('56a2c2800000000000000000')}})
#    for doc in cursor:
##        print(doc)
#        text_file.write(str(doc))
#        text_file.write('\n')



#generated_timestamp = datetime.datetime(year,month,date,hour,minute,second)        
#oid = create_object_id_from_timestamp(generated_timestamp)
oid = '56a06f8227adb02cb05bd45f'
print (oid)

posts = COLLECTION_TREATMENTS.count({'_id': {'$gt':ObjectId(oid)}})      
print('number of posts =',posts)

COLLECTION_TREATMENTS.delete_many({'_id': {'$gt':ObjectId(oid)}})  
        
DBclient.close()