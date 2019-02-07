# Results and Rankings for Spartan Obstacle Course Racing 

I compete in Spartan races and am interested in seeing my progress over time. It's also nice to compare my ranking with friends. This repo contains the tooling to download historical race data from the spartan site and from athlinks.

## To execute
```
python spartan.py -t 4 -w true -a <ATHLINKS_API_KEY>
```

## Parameters

| Parameter | Sample Value | Purpose |
| ------------- | ------------- | ------------- |
| -t | 2 | Number of threads to execute concurrently | 
| -w | true | Whether or not to write the results to a file |
| -a | XYZABC | Athlinks API Key |

## Notes
Clean Up of wonky data
```
cat past.json | sed 's/"": "",//g' | sed 's/, "": ""//g' > past_test2.json
```

## Data Hierarchy
* Events (Spartan API) - {"event_name":"Spartan World Championship","subevents": [{"event_name": "Lake Tahoe Beast","race_id":"677643"}]}
-- subevent has the race_id 
* Race Details (Athlinks API) - 
* Race Course Result Details (Athlinks API)(contains results for each spartan athlete)

## Request Flow
1. ask Spartan API for races (Spartan.makeRequests). Events -> SubEvents -> RaceID 
-- save these results to a single file
2. Local Data Check
-- Check to see if we have the event details already stored locally (but we don't do anything with this)
-- Check to see if we have the race details already stored locallly
3. ask Athlinks for Race Details (Spartan.requestRace -> Athlinks.getRaceDetails)
-- save each race individually to unique race json file in 'races' dir
4. Local Data Check
-- Check to see if we have course races already stored locally
5. ask Athlinks for Course results (Spartan.requestRaceCourses -> CourseResult.getCourseResult)

