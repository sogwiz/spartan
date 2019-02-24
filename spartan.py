import requests
import json
import jsonlines
import sys
import getopt
import time
import os.path
from concurrent.futures import ThreadPoolExecutor
import threading
from spartan_models import Race
from spartan2 import Athlinks
from spartan3 import CourseResult
from utils import getExistingEvents, getExistingRaces, getRaceDetails, getExistingCourses, normalizeCourseResults, str2bool


class Spartan:
    response = ""
    url = "https://api.spartan.com/api/events/upcoming_past_planned_groups/"
    #querystring = {"ulimit": "0", "plimit": "1000","country": "USA", "page": "0"}
    querystring = {"ulimit": "0", "plimit": "100", "page": "0"}
    headers = {
        'Pragma': "no-cache",
        'Origin': "https://www.spartan.com",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "en",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'Accept': "application/json, text/plain, */*",
        'Referer': "https://www.spartan.com/en/race/results-photos/past-races",
        'Connection': "keep-alive",
        'Cache-Control': "no-cache"
    }

    def makeRequests(self, writeToFile):
        self.response = requests.request(
            "GET", self.url, headers=self.headers, params=self.querystring)
        races = []
        for item in self.response.json()['past_events']:
            for subevent in item['subevents']:
                # get the subevents.race_id
                subevent_id = subevent.get('id')
                event_id = subevent.get('parent_event_id')
                race_id = subevent.get('race_id')
                race = Race(race_id, event_id, subevent_id)
                races.append(race)
                print("event_id: " + race.event_id + " \t subevent_id: " +
                      race.subevent_id + " \t race_id: " + race.race_id)
        if(writeToFile == True):
            pastevents = self.response.json()['past_events']
            for i, event in enumerate(pastevents):
                pastevents[i]['_id'] = str(event['id'])
                # remove empty keys
                # d = dict( [(k,v) for k,v in event.items() if len(v)>0])
                # pastevents[i]=d
            with open('events.json', 'w') as outfile:
                json.dump(pastevents, outfile)
        return races


def requestRace(race, raceDetailsList, writefiles, athlinks):
    print("requestRace " + str(race.race_id) +
          " assigned to thread: {}".format(threading.current_thread().name))
    # make a request to athlinks to get the list of courses
    # this can be done in parallel

    raceDetails = athlinks.getRaceDetails(race)
    if(raceDetails is not None):
        raceDetailsJson = raceDetails.json()
        # raceDetailsJson['_id']= str(race)
        raceDetailsJson['subevent_id'] = race.subevent_id
        raceDetailsJson['event_id'] = race.event_id
        raceDetailsJson['_id'] = str(raceDetailsJson['RaceID'])
        raceDetailsList.append(raceDetailsJson)

        directory = 'races'
        filename = 'races' + '/' + str(race.race_id) + '.json'
        if(writefiles == True):
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(filename, 'w') as writer:
                json.dump(raceDetailsJson, writer)
    return "finished race request: " + str(race.race_id)


def requestRaceCourses(race, existing_courses, apikey, writefiles):
    
    for course in race['Courses']:
        courseResultsList = []
        courseResult = CourseResult(apikey)
        # time.sleep(1)
        if course['CourseID'] in existing_courses:
            print("skipping course " + str(course['CourseID']))
        else:
            print("need to fetch data for course " +
                    str(course['CourseID']) + "\t and race = " + str(race['RaceID']))
            page = 1
            resultCount = 0
            shouldContinuePaging = True
            resultJson = None
            while shouldContinuePaging:    
                result = courseResult.getCourseResult(
                    race['RaceID'], course['CourseID'], page)
                if(result is not None):
                    if page == 1:
                        resultJson = result.json()
                        resultCount = int(resultJson['ResultCount'])
                        resultJson['subevent_id'] = race['subevent_id']
                        resultJson['event_id'] = race['event_id']
                        resultJson['_id'] = str(course['CourseID'])
                    else:
                        pageResult = result.json()
                        resultJson['RaceEntries']['List'].extend(pageResult['RaceEntries']['List'])
                    
                    #let's say there's 1700 results, and we've already gotten 2 pages of data
                    #1700 < 2*1000, so we'll stop at this point
                    if resultCount < page*500:
                        shouldContinuePaging = False
                    
                    page+=1
            courseResultsList.append(resultJson)
                    
        if(writefiles == True):
            filename = "event_" + \
                str(race['event_id']) + "_race_" + \
                str(race['RaceID']) + \
                "_course_" + str(course['CourseID']) + ".json"
            directory = 'course_results'
            file = directory + '/'+filename
            # check if len of courseResultsList!=0 as well
            if len(courseResultsList) != 0:
                if os.path.isfile(file):
                    print("File already exists! " + file +
                          " for course " + str(course['CourseID']))
                else:
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(file, 'w') as outfile:
                        json.dump(courseResultsList, outfile)


def main():
    apikey = ''
    writefiles = False
    threads = 1
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:w:t:h", [
                                   "apikey=", "writefiles=", "threads="])
    except getopt.GetoptError:
        print('spartan.py -a <Athlinks API Key> -w <Write To File = True/False> -t <Threads Count>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'spartan.py -a <Athlinks API Key> -w <Write To File = True/False> -t <Threads Count>')
            sys.exit()
        elif opt in ("-a", "--apikey"):
            apikey = arg
        elif opt in ("-w", "--writefiles"):
            writefiles = str2bool(arg)
        elif opt in ("-t", "--threads"):
            threads = int(arg)
    print('Write To Files : ', str(writefiles))
    print('Threads count : ', str(threads))

    spartan = Spartan()
    races = spartan.makeRequests(writefiles)

    #existing_events variable isn't used for anything
    existing_events = getExistingEvents()
    existing_races = getExistingRaces()

    #existing_events = []
    #existing_races = []

    total_races = sum(race.race_id != '0' for race in races)
    print("total races " + str(total_races))
    print("num existing races " + str(len(existing_races)))
    print("num existing events " + str(len(existing_events)))

    athlinks = Athlinks(apikey)
    raceDetailsList = []

    # this WILL wait until all are done
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for race in races:
            if(race.race_id in existing_races):
                # print("found a match with " + race.race_id)
                # merge the two lists into one rather than append
                raceDetailsList.append(getRaceDetails(race))
            else:
                if(str(race.race_id) !="0"):
                    executor.submit(requestRace, race,
                                    raceDetailsList, writefiles, athlinks)

            # for each courseId of race, make a request to athlinks
            # this can be done in parallel
            # print(str(len(raceDetailsList)))
    
    existing_courses = getExistingCourses()

    start = time.time()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for race in raceDetailsList:
            executor.submit(requestRaceCourses,race, existing_courses, apikey, writefiles)

    end = time.time()
    #print("\n\n\n****\nGetting Courses took: " + str(end - start) + "\n*****\n\n")
    print("Completed data fetch")
    print("Normalizing course results....")
    normalizeCourseResults()


if __name__ == "__main__":
    main()
