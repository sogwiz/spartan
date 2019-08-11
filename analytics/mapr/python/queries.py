from mapr.ojai.storage.ConnectionFactory import ConnectionFactory
from mapr.ojai.storage.ConnectionFactory import ConnectionFactory
import getopt
import sys
import time
import logging
import re
import datetime
import json

class SpartanQuery:
    
    def __init__(self, urlConn):
        self.connection_string = urlConn
        self.races = list()
        self.course_results = list()
        self.events = list()


        #10.10.99.151:5678?auth=basic;user=mapr;password=mapr;ssl=false
        self.options = {
            'ojai.mapr.query.include-query-plan': True,
            'ojai.mapr.query.timeout-milliseconds': 120000,
            'ojai.mapr.query.result-as-document': True
        }

    def queryResultsByUser(self, user):
        connection = ConnectionFactory.get_connection(self.connection_string)
        document_store = connection.get_store(store_path='/apps/course_results')
        #query_dict = {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}
        query_dict = {"$select":["event_id","RaceID","CourseName","CoursePattern","DisplayName","TicksString","RankO"],"$orderby": {"RaceID": "asc"},"$where":{"$matches":{"DisplayName":"(?i)"+user}}}
        #query_dict = {"$select":["CourseID","CourseName","RaceID","RaceEntries.List[].DisplayName"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%"}}}
        #query_dict = {"$select":["_id","event_id","RaceID","CourseName","CoursePattern","DisplayName","TicksString","RankO","RankG","RankA","RacerID","BibNum"],"$orderby": {"RaceID": "asc"},"$where":{"$like":{"DisplayName":user}}}

        start = time.time()
        query_result = document_store.find(query_dict,options=self.options)

        iterations = 0
        raceEntries = 0
        course_results = list()
        #courseIds = list()

        print(query_result.get_query_plan())

        for item in query_result:
            iterations+=1
            #print (item.as_dictionary())

            row = item.as_dictionary()
            course_results.append(row)
            #courseId = row['CourseID']
            #courseIds.append(courseId)
            courseName = row['CourseName']
            #racers = row['RaceEntries']['List']
            print(" Race : " + str(row['RaceID']) + " CoursePattern: " + str(row['CoursePattern']) + " " + courseName + " Time : " + str(row['TicksString'])  +" Rank: " + str(row['RankO']) +" event_id: " + str(row['event_id']))
            #print("Race : " + str(row['RaceID']) + " Course: " + str(courseId) + " " + courseName + " with " + str(len(racers)))

            #raceEntries+=len(racers)
            #for racer in racers:
            #    if racer['DisplayName'].lower() == 'sargon benjamin':
            #        print("Race : " + str(row['RaceID']) + " Course: " + str(courseId) + " " + courseName + " with " + str(len(racers)))
            #        print ("Found match with " + str(racer))
        end = time.time()
        print("Duration = " + str(end - start))
        print("iterations is " + str(iterations))
        connection.close()
        return course_results
    
    def queryRaceInfo(self, raceIds):
        connection = ConnectionFactory.get_connection(self.connection_string)
        document_store = connection.get_store(store_path='/apps/races')
        #query_dict = {"$select":["RaceID","RaceName","RaceDate","StateProvName","Latitude","Longitude"],"$orderby": {"RaceDate": "asc"},"$where":{"$in":{"RaceID":raceIds}}}
        query_dict = {"$orderby": {"RaceDate": "asc"},"$where":{"$in":{"RaceID":raceIds}}}
        start = time.time()
        query_result = document_store.find(query_dict,options=self.options)
        races = list()
        iterations = 0
        for item in query_result:
            iterations+=1
            row = item.as_dictionary()
            races.append(row)
        
        end = time.time()
        logging.info("Duration = " + str(end - start))
        logging.info("iterations is " + str(iterations))
        connection.close()
        return races

    def queryEventInfo(self, eventIds):
        connection = ConnectionFactory.get_connection(self.connection_string)
        document_store = connection.get_store(store_path='/apps/events')

        query_dict = {"$select":["_id","id","event_name","start_date","end_date","venue"],"$orderby": {"end_date": "asc"},"$where":{"$in":{"_id":eventIds}}}
        start = time.time()
        query_result = document_store.find(query_dict,options=self.options)
        events = list()
        iterations = 0
        for item in query_result:
            iterations+=1
            row = item.as_dictionary()
            #print (row['_id']+"_" + str(row['venue']))
            events.append(row)
        
        end = time.time()
        logging.info("Duration = " + str(end - start))
        logging.info("iterations is " + str(iterations))
        connection.close()
        return events


    def parseDateString(self, dateStr):
        dateMillis = re.search(r'\((.*?)\)',dateStr).group(1)
        dateTime = datetime.datetime.fromtimestamp(float(dateMillis)/1000.0)
        return dateTime

    def flattenInfo(self):
        flatList = list()
        row = {}
        for race in self.races:
            eventId = race['event_id']
            course_result = next((x for x in self.course_results if x['event_id'] == eventId), None)
            event = next((x for x in self.events if x['id'] == eventId), None)

            #course_result.update(race)
            #course_result.update(event)
            row = course_result
            row['race'] = race
            row['event'] = event
            dateTimeStr = self.parseDateString(race['RaceDate']).strftime("%m/%d/%Y, %H:%M:%S")
            row['MetaRaceDateTime'] = dateTimeStr
            row['MetaEventUrl'] = "https://www.spartan.com/en/race/detail/"+str(eventId)+"/overview"
            flatList.append(row)
        return flatList



def main():
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
    urlString = ''
    password = ''
    

    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:h", [
                                   "urlconnection=", "password="])
    except getopt.GetoptError:
        print("queries.py -u <DB URL Conn String> -p <PASSWORD>")
    
    for opt, arg in opts:
        if opt == '-h':
            print('queries.py -u <DAG_URL:PORT>')
            print("eg -u '10.10.99.151:5678?auth=basic;user=mapr;password=mapr;ssl=false'")
            sys.exit()
        elif opt in ("-u", "--urlconnection"):
            urlString = arg
        elif opt in ("-p", "--password"):
            password = arg

    logging.info("url string is " + urlString)
    
    spartanQuery = SpartanQuery(urlString)
    spartanQuery.course_results = spartanQuery.queryResultsByUser("sargon benjamin")
    raceIds = [cr['RaceID'] for cr in spartanQuery.course_results]
    eventIds = [cr['event_id'] for cr in spartanQuery.course_results]
    spartanQuery.races = spartanQuery.queryRaceInfo(raceIds)
    spartanQuery.events = spartanQuery.queryEventInfo(eventIds)
    flattened = spartanQuery.flattenInfo()

    with open('result.json','w') as json_file:
        json.dump(flattened,json_file)
    
if __name__ == "__main__":
    main()

