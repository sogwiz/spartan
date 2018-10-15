import requests
from spartan_models import Race

class CourseResult:

    url = "https://api.athlinks.com/results/list/"

    def __init__(self, data):
        self.apikey = data
        self.querystring = {"format":"json","key":self.apikey, "page":"1","pageSize":"1000"}

    headers = {
        'Referer': "https://www.spartan.com/en/race/detail/3690/results?fullResults=true",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'Cache-Control': "no-cache",
        'Postman-Token': "264878c7-6a9e-4ba1-a9bb-90d0b0131871"
        }

    def getCourseResult(self, race_id, course_id):
        request_url = self.url + str(race_id) + "/" + str(course_id) + "/A"
        print("Making request for course results URL : " + request_url)
        response = requests.request("GET", request_url, headers=self.headers, params=self.querystring)
        if(response.status_code!=requests.codes.ok):
            print("Error in response with error code: " + str(response.status_code))
            print(response.text)
            return None
        return response