# Queries
# find course_results for user
find /apps/course_results --query '{"$where":{"$like":{"DisplayName":"sargon benjamin"}}}'
#case insensitive match
find /apps/course_results --query '{"$select":["_id"],"$where":{"$matches":{"DisplayName":"[S,s]argon [B,b]enjamin"}}}'


## Old way
find /apps/course_results --query {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}
