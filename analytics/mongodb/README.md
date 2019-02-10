# Useful queries
#Find all race entries for a particular racer (case insensitive)
db.course_results.find({"RaceEntries.List": {$elemMatch: {DisplayName: {$regex : 'Sargon Benjamin', $options: 'i'}}}})

#Find all race entries for a particular racer but only show that user's races (case insensitive)
db.course_results.find({"RaceEntries.List": {$elemMatch: {DisplayName: {$regex : 'Sargon Benjamin', $options: 'i'}}}}, {"RaceEntries.List.$":1})

