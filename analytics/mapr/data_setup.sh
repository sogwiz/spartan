DATA_DIR=/user/mapr/spartan
TABLE_EVENTS=/apps/events
TABLE_RACES=/apps/races
TABLE_COURSE_RESULTS=/apps/course_results
TMP_DATA_DIR=/tmp/data

cd /tmp/
rm -rf $TMP_DATA_DIR
mkdir $TMP_DATA_DIR
cd $TMP_DATA_DIR
unzip /tmp/data.zip 

hadoop fs -rm -r $DATA_DIR
hadoop fs -mkdir $DATA_DIR

#this is needed to avoid maprdb format issues with empty key names
cat events.json | sed 's/"": "",//g' | sed 's/, "": ""//g' > events2.json
mv events2.json events.json

hadoop fs -copyFromLocal $TMP_DATA_DIR/races $DATA_DIR
hadoop fs -copyFromLocal $TMP_DATA_DIR/course_results $DATA_DIR
hadoop fs -copyFromLocal $TMP_DATA_DIR/events.json $DATA_DIR

# create the mapr db tables
maprcli table delete -path $TABLE_EVENTS 
maprcli table delete -path $TABLE_RACES 
maprcli table delete -path $TABLE_COURSE_RESULTS

maprcli table create -path $TABLE_EVENTS -tabletype json
maprcli table create -path $TABLE_RACES -tabletype json
maprcli table create -path $TABLE_COURSE_RESULTS -tabletype json

#load data into events table
mapr importJSON -idfield "id" -src $DATA_DIR/events.json -dst $TABLE_EVENTS -mapreduce false

#load data into races table
#mapr importJSON -idfield "RaceID" -src $DATA_DIR/races/* -dst $TABLE_RACES -mapreduce false
mapr importJSON -src $DATA_DIR/races/* -dst $TABLE_RACES -mapreduce false

#load data into course_results table
#mapr importJSON -idfield "CourseID" -src $DATA_DIR/course_results/* -dst $TABLE_COURSE_RESULTS -mapreduce false
mapr importJSON -src $DATA_DIR/course_results/* -dst $TABLE_COURSE_RESULTS -mapreduce false

