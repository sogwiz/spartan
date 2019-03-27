# Queries
# find course_results for user
find /apps/course_results --query '{"$where":{"$like":{"DisplayName":"sargon benjamin"}}}'
#case insensitive match
find /apps/course_results --query '{"$select":["event_id","RaceID","CourseName","CoursePattern","DisplayName","TicksString"],"$where":{"$matches":{"DisplayName":"[S,s]argon [B,b]enjamin"}}}'

#Drill Query
select event_id,RaceID,CourseName,CoursePattern,DisplayName,TicksString from dfs.`/apps/course_results` where DisplayName='sargon benjamin'


## Old way
find /apps/course_results --query {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}
