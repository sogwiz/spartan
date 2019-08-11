export PYTHONIOENCODING=utf8
SPARKURL="10.10.103.123:7077"
hadoop fs -rmr /user/mapr/spartan/events.json.transform
hadoop fs -rmr /user/mapr/spartan/course_results_normalized.transform
/opt/mapr/spark/spark-2.4.0/bin/spark-submit --master spark://$SPARKURL sparkjob.py