import os
import json
from spartan_models import Race

def getRaceDetails(race):
    directory = "races"
    filename = os.path.join(directory, str(race.race_id)+".json")
    with open(filename, 'r') as f:
        race_dict = json.load(f)
        return race_dict

def getExistingEvents():
    directory = "course_results"
    events = {}
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                #print(os.path.join(directory, filename))
                entry = str(filename.split("_")[1])
                events[entry]=True
                #events[]
                continue
            else:
                continue
    except:
        print ("Exception while reading from " + directory + " . Continuing...")
    return events

def getExistingRaces():
    directory = "races"
    races = {}
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                #print(os.path.join(directory, filename))
                entry = str(filename.split(".")[0])
                races[entry]=True
                #events[]

                continue
            else:
                continue
    except:
        print ("Exception while reading from " + directory + " . Continuing...")
    return races

def getExistingCourses():
    directory = "course_results"
    
    course_ids = []
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".json") :
                file = os.path.join(directory, filename)
                with open(file, 'r') as f:
                    course_results = json.load(f)
                for course in course_results:
                    course_ids.append(course['CourseID'])
            else:
                continue
    except:
        print ("Exception while reading from " + directory + " . Continuing...")
    return course_ids


#print("Length : " + str(len(races)) )
#existing_courses = getExistingCourses()
#courses = [123, 342342, 1187893]
#for course in courses:
#    if course in existing_courses:
#        print("already seen course " + str(course))
#print(str(len(existing_courses)))