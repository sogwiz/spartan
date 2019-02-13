import org.apache.spark.sql.SparkSession        
import com.mapr.db.spark.sql._ 

val sc = new SparkContext( "local", "Spartan", "/opt/mapr/spark", Nil, Map(), Map())   

val dfEvents = sc.loadFromMapRDB("/apps/events")
dfEvents.select($"event_name").show()
dfEvents.groupBy("event_name").count().show()

System.exit(0)

case class Event (@JsonProperty("_id") id:String, 
            @JsonProperty("end_date") endDate:ODate,
            @JsonProperty("event_name") eventName: String, 
            @JsonProperty("subevents") subevents: List[String])

case class Event (_id:String, 
            event_name: String)
            end_date:java.sql.Date,
            event_name: String), 
            @JsonProperty("subevents") subevents: List[String])

val c = array_contains(column = $"RaceEntries.List.DisplayName", value = "sargon benjamin")
courseResults.filter(c).select("CourseName","EventCourseID","ResultsDate").show(50,false)
