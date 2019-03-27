# Data Setup
```
ssh to_your_node
su mapr
maprlogin password
cd /tmp/
vi data_setup.sh //copy the contents of data_setup.sh to this file
chmod 755 data_setup.sh
./data_setup.sh
```

# Queries
# find course_results for user
find /apps/course_results --query '{"$where":{"$like":{"DisplayName":"sargon benjamin"}}}'
#case insensitive match
find /apps/course_results --query '{"$select":["event_id","RaceID","CourseName","CoursePattern","DisplayName","TicksString"],"$where":{"$matches":{"DisplayName":"[S,s]argon [B,b]enjamin"}}}'

## Drill Query
```
select event_id,RaceID,CourseName,CoursePattern,DisplayName,TicksString from dfs.`/apps/course_results` where DisplayName='sargon benjamin'
```

## Old way
find /apps/course_results --query {"$select":["RaceEntries.List[1].EventCourseID"],"$where":{"$like":{"RaceEntries.List[].DisplayName":"sargon%benjamin"}}}
