
To execute
python spartan1.py -t 4 -w true -a <ATHLINKS_API_KEY>

Clean Up of wonky data
cat past.json | sed 's/"": "",//g' | sed 's/, "": ""//g' > past_test2.json