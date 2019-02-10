# Queries
find /apps/course_results --query {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}