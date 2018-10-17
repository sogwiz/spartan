# Results and Rankings for Spartan Obstacle Course Racing 

I compete in Spartan races and am interested in seeing my progress over time. It's also nice to compare my ranking with friends. This repo contains the tooling to download historical race data from the spartan site and from athlinks.

## To execute
```
python spartan.py -t 4 -w true -a <ATHLINKS_API_KEY>
```

## Parameters

| Parameter | Sample Value | Purpose |
| ------------- | ------------- | ------------- |
| -t | 2 | Number of threads to execute concurrently | 
| -w | true | Whether or not to write the results to a file |
| -a | XYZABC | Athlinks API Key |

## Notes
Clean Up of wonky data
```
cat past.json | sed 's/"": "",//g' | sed 's/, "": ""//g' > past_test2.json
```