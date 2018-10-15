import requests
from spartan_models import Race

class Athlinks:
    url = "https://api.athlinks.com/races/"

    # parameterized constructor
    def __init__(self, data):
        self.apikey = data
        self.querystring = {"format":"json","key":self.apikey}

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'Cache-Control': "no-cache"
        }

    def getRaceDetails(self, race):
        request_url = self.url + str(race.race_id)
        if(int(race.race_id) !=0):
            print("Making athlinks request: " + request_url)
            response = requests.request("GET", request_url, headers=self.headers, params=self.querystring)
            return response
        else:
            #print("Skipping request: " + request_url)
            return None




