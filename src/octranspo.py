# octranspo.py 
#   - A py3status module that fetches live GPS estimates for OCTranspo bus routes.

__author__ = "Igor Grebenkov"

import json, requests

# Fetches a JSON response from the OCTranspo API
def getJSON(routeNo, stopNo):
    payload = { 
                'appID': '8856da69',
                'apiKey': '63f69bfe2ea5e6e8b12511000f01d73c', 
                'routeNo': routeNo,
                'stopNo': stopNo,
                'format': 'JSON' 
              }

    r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
    return r.json()

# Parses relevant data from the JSON response into a dict
def parseData(data, direction):
    if direction == 'east':
        dirNo = 0
    elif direction == 'west':
        dirNo = 1
        
    stopNo = data['GetNextTripsForStopResult']['StopNo']
    stopLabel = data['GetNextTripsForStopResult']['StopLabel']
    
    if type(data['GetNextTripsForStopResult']['Route']['RouteDirection']) is list:
        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Direction']

        trip1 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][0]['AdjustedScheduleTime'])

        trip2 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][1]['AdjustedScheduleTime'])

        trip3 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][2]['AdjustedScheduleTime'])
    else:
        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Direction']

        trip1 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime'])

        trip2 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime'])

        trip3 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustedScheduleTime'])

    return { 'stopNo': stopNo,
             'stopLabel': stopLabel,
             'routeNo': routeNo,
             'routeDir': routeDir,
             'trip1': trip1,
             'trip2': trip2,
             'trip3': trip3 
           }

class Py3status:
    routeNo = '3000' 
    stopNo = '95'
    direction = 'east'
    low_thresh = 15

    def OCTranspo(self):
        data = getJSON(self.routeNo, self.stopNo)
        result = parseData(data, self.direction)

        # Assign color based on trip time relative to low threshold 
        if int(result['trip1']) <= self.low_thresh:
            color1 = self.py3.COLOR_LOW
        else:
            color1 = self.py3.COLOR_HIGH
        
        if int(result['trip2']) <= self.low_thresh:
            color2 = self.py3.COLOR_LOW
        else:
            color2 = self.py3.COLOR_HIGH
        
        if int(result['trip3']) <= self.low_thresh:
            color3 = self.py3.COLOR_LOW
        else:
            color3 = self.py3.COLOR_HIGH
        
        # Output text
        ft_separator = self.py3.safe_format(' / ')
        
        ft_route_dir = self.py3.safe_format(' {routeNo} {direction} (', 
                { 
                  'routeNo': result['routeNo'], 
                  'direction': result['routeDir'][0], 
                })
        
        ft_trip1 = self.py3.safe_format('{trip1}', 
                {
                  'trip1': result['trip1'], 
                })
        
        ft_trip2 = self.py3.safe_format('{trip2}', 
                {
                  'trip2': result['trip2'], 
                })
        
        ft_trip3 = self.py3.safe_format('{trip3}', 
                {
                  'trip3': result['trip3'], 
                })

        return {
                'cached_until': self.py3.time_in(50),
                'composite': [
                    {
                      'full_text': ft_route_dir,
                      'color': self.py3.COLOR_HIGH
                    },   
                    {
                      'full_text': ft_trip1,
                      'color': color1
                    },
                    {
                      'full_text': ft_separator,
                      'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trip2,
                      'color': color2
                    },
                    {
                      'full_text': ft_separator,
                      'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trip3,
                      'color': color3
                    },
                    {
                      'full_text': self.py3.safe_format(')'),
                      'color': self.py3.COLOR_HIGH
                    }
                ]
            }

if __name__ == "__main__":
    from py3status.module_test import module_test
    module_test(Py3status)

