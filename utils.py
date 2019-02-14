import os
import json
from spartan_models import Race
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import threading
import time

def getRaceDetails(race):
    directory = "races"
    filename = os.path.join(directory, str(race.race_id)+".json")
    with open(filename, 'r') as f:
        race_dict = json.load(f)
        return race_dict

#20190206: SB: I think this function tries to see the events by looking
#at the filename of the course_results and then splitting to get the event id
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

def normalizeCourseResultsHelper(directory,filename, newDir):
    print("filename " + filename) 
    start = time.time()
    #      " assigned to thread: {}".format(threading.current_thread().name))
    course_results_racers = {}
    file = os.path.join(directory, filename)
    with open(file, 'r') as f:
        course_results = json.load(f)
        course_results_racers[filename] = list()
        newFile = os.path.join(newDir, filename)
        #why are there multiple course_result objects in each json file?
        for course_result in course_results:
            racers = course_result['RaceEntries']['List']
            del course_result['RaceEntries']
            for racer in racers:
                course_result_racer = {}
                course_result_racer.update(course_result)
                course_result_racer.update(racer)
                course_result_racer['_id'] = str(course_result['CourseID']) + "_" + str(course_result_racer["RacerID"])
                course_result_racer['CourseID'] = str(course_result['_id'])
                course_result_racer['CourseName'] = str(course_result['CourseName'])
                course_results_racers[filename].append(course_result_racer)
            with open(newFile, 'w') as outfile:
                json.dump(course_results_racers[filename], outfile)
    end = time.time()
    #print("Conversion " + filename + " : " + str(end - start))


def normalizeCourseResults(directory='course_results'):
    newDir = 'course_results_normalized'
    if not os.path.exists(newDir):
        os.makedirs(newDir)

    start = time.time()
    try:
        # this WILL wait until all are done
        # ThreadPoolExecutor with 4 threads took 279 seconds
        # ProcessPoolExecutor with 4 processes took 179 seconds
        with ProcessPoolExecutor(max_workers=4) as executor:
            for filename in os.listdir(directory):
                if filename.endswith(".json") :
                    executor.submit(normalizeCourseResultsHelper,directory,filename,newDir)
                    #normalizeCourseResultsHelper(directory,filename,newDir)                    
                else:
                    continue
    except Exception as inst:
        print ("Exception while reading from " + directory + " . Continuing...")
        print (type(inst))
        #print (inst.args)
        print (inst)
    
    end = time.time()
    print("\n\nTime to Complete : " + str(end-start))


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return False
#print("Length : " + str(len(races)) )
#existing_courses = getExistingCourses()
#courses = [123, 342342, 1187893]
#for course in courses:
#    if course in existing_courses:
#        print("already seen course " + str(course))
#print(str(len(existing_courses)))
#normalizeCourseResults('course_results')