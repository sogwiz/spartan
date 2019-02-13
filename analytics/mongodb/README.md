# Useful queries
#Find all race entries for a particular racer (case insensitive)
db.course_results.find({DisplayName: {$regex : 'Sargon Benjamin', $options: 'i'}})

#NO LONGER USED as schema has changed: Find all race entries for a particular racer and project only that user's races (case insensitive)
db.course_results.find({"RaceEntries.List": {$elemMatch: {DisplayName: {$regex : 'Sargon Benjamin', $options: 'i'}}}}, {"RaceEntries.List.$":1})
https://docs.mongodb.com/manual/reference/operator/projection/positional/#project-array-values

#events.json to mongo
mongoimport --db spartandb --collection events --file ~/dev/playground/spartan/events.json --jsonArray

#races folder to mongo
#Used the import feature in Studio 3T to select all the json files and do the import

#course_results_normalized folder
#Used the import feature in Studio 3T to select all the json files and do the import
