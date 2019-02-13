# Queries
# find course_results for user
find /apps/course_results --query {"$where":{"$like":{"DisplayName":"sargon%benjamin"}}}

## Old way
find /apps/course_results --query {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}
