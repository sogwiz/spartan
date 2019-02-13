from mapr.ojai.storage.ConnectionFactory import ConnectionFactory
from mapr.ojai.storage.ConnectionFactory import ConnectionFactory
import getopt
import sys
import time
import logging

class SpartanQuery:
    
    def __init__(self, urlConn):
        self.connection_string = urlConn

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
        #query_dict = {"$select":["CourseID","CourseName","RaceID"],"$where":{"$matches":{"RaceEntries.List[].DisplayName":"(?i)"+user}}}
        #query_dict = {"$select":["CourseID","CourseName","RaceID","RaceEntries.List[].DisplayName"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%"}}}
        query_dict = {"$where":{"$like":{"DisplayName":"sargon%benjamin"}}}

        start = time.time()
        query_result = document_store.find(query_dict,options=self.options)

        iterations = 0
        raceEntries = 0
        raceIds = list()
        courseIds = list()

        print(query_result.get_query_plan())

        for item in query_result:
            iterations+=1
            #print (item.as_dictionary())

            row = item.as_dictionary()
            courseId = row['CourseID']
            courseIds.append(courseId)
            courseName = row['CourseName']
            raceIds.append(row['RaceID'])
            #racers = row['RaceEntries']['List']
            print("Race : " + str(row['RaceID']) + " Course: " + str(courseId) + " " + courseName + " event_id: " + str(row['event_id']))
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
    
    def queryRaceInfo(self, raceIds):
        connection = ConnectionFactory.get_connection(self.connection_string)
        document_store = connection.get_store(store_path='/apps/races')
        query_dict = {"$select":["RaceID","RaceName","StateProvName","WebSite"],"$where":{"$in":{"RaceID":raceIds}}}
        start = time.time()
        query_result = document_store.find(query_dict,options=self.options)

        iterations = 0
        for item in query_result:
            iterations+=1
            print (item.as_dictionary())
        
        end = time.time()
        print("Duration = " + str(end - start))
        print("iterations is " + str(iterations))
        connection.close()


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
            print('queries.py -d <DAG_URL:PORT> -u <USER> -p <PASSWORD>')
            print("eg -u '10.10.99.151:5678?auth=basic;user=mapr;password=mapr;ssl=false'")
            sys.exit()
        elif opt in ("-u", "--urlconnection"):
            urlString = arg
        elif opt in ("-p", "--password"):
            password = arg
    
    spartanQuery = SpartanQuery(urlString)
    #spartanQuery.queryResultsByUser("robert killian")
    spartanQuery.queryResultsByUser("sargon benjamin")
    #raceIds = [677643,730535,689075]
    #spartanQuery.queryRaceInfo(raceIds)


if __name__ == "__main__":
    main()

