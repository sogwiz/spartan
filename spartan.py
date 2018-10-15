import requests
import json
import jsonlines
import sys
import getopt
import time
import os.path
from spartan_models import Race
from spartan2 import Athlinks
from spartan3 import CourseResult
from utils import getExistingEvents, getExistingRaces, getRaceDetails, getExistingCourses


class Spartan:
    response = ""
    url = "https://api.spartan.com/api/events/upcoming_past_planned_groups/"
    querystring = {"ulimit": "0", "plimit": "5",
                   "country": "USA", "page": "0"}
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
            with open('past_test.json', 'w') as outfile:
                json.dump(pastevents, outfile)
        return races


def main():
    apikey = ''
    writefiles = False
    threads = 1
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:w:t:h", ["apikey=", "writefiles=", "threads="])
    except getopt.GetoptError:
        print('spartan1.py -a <Athlinks API Key> -w <Write To File = True/False> -t <Threads Count>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('spartan1.py -a <Athlinks API Key> -w <Write To File = True/False> -t <Threads Count>')
            sys.exit()
        elif opt in ("-a", "--apikey"):
            apikey = arg
        elif opt in ("-w", "--writefiles"):
            writefiles = bool(arg)
        elif opt in ("-t", "--threads"):
            threads = arg
    print('Write To Files : ', str(writefiles))
    print('Threads count : ', str(threads))

    spartan = Spartan()
    races = spartan.makeRequests(writefiles)

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
    for race in races:
        # make a request to athlinks to get the list of courses
        # this can be done in parallel
        if(race.race_id in existing_races):
            # print("found a match with " + race.race_id)
            # merge the two lists into one rather than append
            raceDetailsList.append(getRaceDetails(race))
            continue

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
                    # writer.write_all(raceDetailsList)

        # for each courseId of race, make a request to athlinks
        # this can be done in parallel
        # print(str(len(raceDetailsList)))

    existing_courses = getExistingCourses()

    for race in raceDetailsList:
        courseResultsList = []
        for course in race['Courses']:
            courseResult = CourseResult(apikey)
            # time.sleep(1)
            if course['CourseID'] in existing_courses:
                print("skipping course " + str(course['CourseID']))
            else:
                print("need to fetch data for course " +
                        str(course['CourseID']) + "\t and race = " + str(race['RaceID']))
                result = courseResult.getCourseResult(
                    race['RaceID'], course['CourseID'])
                if(result is not None):
                    resultJson = result.json()
                    resultJson['subevent_id'] = race['subevent_id']
                    resultJson['event_id'] = race['event_id']
                    resultJson['_id'] = str(course['CourseID'])
                    courseResultsList.append(resultJson)
        if(writefiles == True):
            filename = "event_" + \
                str(race['event_id']) + "_race_" + \
                str(race['RaceID']) + ".json"
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

                # writer.write_all(courseResultsList)


if __name__ == "__main__":
    main()
