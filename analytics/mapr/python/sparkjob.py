# must first run this
# export PYTHONIOENCODING=utf8
# example cmd to run this
# /opt/mapr/spark/spark-2.4.0/bin/spark-submit --master spark://10.10.103.123:7077 sparkjob.py /user/mapr/spartan/events.json

from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import sys

sc = SparkContext('local')
spark = SparkSession(sc)

# A JSON dataset is pointed to by path.
# The path can be either a single text file or a directory storing text files
# /user/mapr/spartan/events.json
path = "/user/mapr/spartan/events.json"
eventsDF = spark.read.json(path)
eventsDF.printSchema()
eventsDF.show()
outDF = eventsDF.select("event_name","start_date","venue.city").orderBy("event_name")
outDF.coalesce(1).write.format('json').save(path+".transform")

pathCR = "/user/mapr/spartan/course_results_normalized"
courseResultsDF = spark.read.json(pathCR)
eliteDF = courseResultsDF.filter(courseResultsDF.CourseName.contains('Elite')).orderBy('RankO','DisplayName')
eventsDF = eventsDF.select('_id','venue')
joinDF = eventsDF.join(eliteDF,eventsDF._id==eliteDF.event_id)

pathRaces = "/user/mapr/spartan/races"
racesDF = spark.read.json(pathRaces)
dfRaceSub = racesDF.select('RaceName','RaceDate','subevent_id','event_id','RaceID')
finalDF = dfRaceSub.join(joinDF,dfRaceSub.subevent_id==joinDF.subevent_id)

#causes pyspark.sql.utils.AnalysisException: u'Found duplicate column(s) when inserting into maprfs
finalDF.coalesce(1).write.format('json').save(pathCR+".transform")
