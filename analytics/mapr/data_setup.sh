#usage: ./data_setup.sh xlarge (will download the xlarge data set 3+million rows in course_results, 280mb)
#usage: ./data_setup.sh small (will download the small data set 700,000 rows in course_results, 73mb)
#usage: ./data_setup.sh (will download the normal sized data set 2.5million rows in course_results, 186mb)
# spartan data set on mapr

DATA_DIR=/user/mapr/spartan
TABLE_EVENTS=/apps/events
TABLE_RACES=/apps/races
TABLE_COURSE_RESULTS=/apps/course_results
STREAM_LOG_EVENTS=/apps/events_log
STREAM_LOG_RACES=/apps/races_log
STREAM_LOG_COURSE_RESULTS=/apps/course_results_log

TMP_DATA_DIR=/tmp/data

cd /tmp/
rm -f data.zip

#first parameter is the file size to use (small, xlarge)
FILE=""

#if no params supplied, then use the medium file
if [[ $# -eq 0 ]] ; then
    echo "Using medium File"
    FILE="https://s3-us-west-2.amazonaws.com/anaik-kops-test/data.zip"
else
    #this is the big file. To use this, just supply any parameter to the shell script
    echo "Using File in folder $1"
    FILE="https://s3-us-west-2.amazonaws.com/anaik-kops-test/$1/data.zip" 
fi

echo "Downloading $FILE"

wget $FILE

rm -rf $TMP_DATA_DIR
mkdir $TMP_DATA_DIR
cd $TMP_DATA_DIR
unzip /tmp/data.zip 


hadoop fs -rm -r $DATA_DIR
hadoop fs -mkdir $DATA_DIR
echo "Removed and created $DATA_DIR"
sleep 5

#this is needed to avoid maprdb format issues with empty key names
cat events.json | sed 's/"": "",//g' | sed 's/, "": ""//g' > events2.json
mv events2.json events.json

hadoop fs -copyFromLocal $TMP_DATA_DIR/races $DATA_DIR
hadoop fs -copyFromLocal $TMP_DATA_DIR/course_results_normalized $DATA_DIR
hadoop fs -copyFromLocal $TMP_DATA_DIR/events.json $DATA_DIR
echo "Copied files from $TMP_DATA_DIR to $DATA_DIR"

# create the mapr db tables
maprcli table delete -path $TABLE_EVENTS 
maprcli table delete -path $TABLE_RACES 
maprcli table delete -path $TABLE_COURSE_RESULTS
echo "Deleted tables $TABLE_EVENTS $TABLE_RACES $TABLE_COURSE_RESULTS"

maprcli stream delete -path $STREAM_LOG_EVENTS 
maprcli stream delete -path $STREAM_LOG_RACES
maprcli stream delete -path $STREAM_LOG_COURSE_RESULTS
echo "Deleted changelog streams $STREAM_LOG_EVENTS $STREAM_LOG_RACES $STREAM_LOG_COURSE_RESULTS"


maprcli table create -path $TABLE_EVENTS -tabletype json
maprcli table create -path $TABLE_RACES -tabletype json
maprcli table create -path $TABLE_COURSE_RESULTS -tabletype json
echo "Created tables $TABLE_EVENTS $TABLE_RACES $TABLE_COURSE_RESULTS"

#create a secondary indexes
maprcli table index add -path $TABLE_COURSE_RESULTS -index racer_display_name -indexedfields DisplayName -includedfields CourseID,CourseName,CoursePattern,RaceID,event_id,Age,BibNum,RacerID,RankO,RankA,RankG,Ticks,TicksString
maprcli table index add -path $TABLE_COURSE_RESULTS -index racer_id -indexedfields RacerID -includedfields CourseID,CourseName,CoursePattern,RaceID,event_id,Age,BibNum,DisplayName,RankO,RankA,RankG,Ticks,TicksString
echo "Created secondary indexes on tables"

#create change data capture logs as streams
LOG="LOG"
maprcli stream create -path $STREAM_LOG_EVENTS -ischangelog true -json
maprcli stream create -path $STREAM_LOG_RACES -ischangelog true -json
maprcli stream create -path $STREAM_LOG_COURSE_RESULTS -ischangelog true -json
echo "Created change log streams $STREAM_LOG_EVENTS $STREAM_LOG_RACES $STREAM_LOG_COURSE_RESULTS"

maprcli table changelog add -path $TABLE_COURSE_RESULTS -changelog "$STREAM_LOG_COURSE_RESULTS:changeTopic" -json
maprcli table changelog add -path $TABLE_EVENTS -changelog "$STREAM_LOG_EVENTS:changeTopic" -json
maprcli table changelog add -path $TABLE_RACES -changelog "$STREAM_LOG_RACES:changeTopic" -json
echo "Added changelogs to tables"

echo "Now loading data into tables..."
#load data into events table
mapr importJSON -idfield "id" -src $DATA_DIR/events.json -dst $TABLE_EVENTS -mapreduce false

#load data into races table
mapr importJSON -src $DATA_DIR/races/* -dst $TABLE_RACES -mapreduce false

#load data into course_results table
#mapr importJSON -idfield "CourseID" -src $DATA_DIR/course_results_normalized/* -dst $TABLE_COURSE_RESULTS -mapreduce false
mapr importJSON -src $DATA_DIR/course_results_normalized/* -dst $TABLE_COURSE_RESULTS -mapreduce false



