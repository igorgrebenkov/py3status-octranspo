# octranspo.py 
#   - A py3status module that fetches live GPS estimates for OCTranspo bus routes.

__author__ = "Igor Grebenkov"

import json, requests, os

# Fetches a JSON response from the OCTranspo API
def getJSON(appID, apiKey, routeNo, stopNo):
    payload = { 
                'appID': appID,
                'apiKey': apiKey, 
                'routeNo': routeNo,
                'stopNo': stopNo,
                'format': 'JSON' 
              }
    try:
        r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
        return r.json()
    except Exception as e:
        return 'CONNECTION_ERROR'

# Parses relevant data from the JSON response into a dict
def parseData(data, direction):
    if direction == 'east':
        dirNo = 0
    elif direction == 'west':
        dirNo = 1
        
    stopNo = data['GetNextTripsForStopResult']['StopNo']
    stopLabel = data['GetNextTripsForStopResult']['StopLabel']
    tripTimes = []
    tripAges = []

    if type(data['GetNextTripsForStopResult']['Route']['RouteDirection']) is list:
        routeLabel = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteLabel']

        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Direction']

        trips = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips'] 
    else:
        routeLabel = data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteLabel']

        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Direction']

        trips = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips'] 
    
    if not trips:
        tripTimes = ['-1'] * 3
        tripAges = [''] * 3
    elif type(trips['Trip']) is list:
        trip_cnt = len(trips['Trip'])
    
        # Populate list of trip times and their adjustment ages
        for i in range(0, trip_cnt):
            tripTimes.append(trips['Trip'][i]['AdjustedScheduleTime'])
            tripAges.append(trips['Trip'][i]['AdjustmentAge'])
    else:
        tripTimes.append(trips['Trip']['AdjustedScheduleTime'])
        tripAges.append(trips['Trip']['AdjustmentAge'])
        
    return { 'stopNo': stopNo,
             'stopLabel': stopLabel,
             'routeLabel': routeLabel,
             'routeNo': routeNo,
             'routeDir': routeDir,
             'tripTimes': tripTimes,
             'tripAges': tripAges,
           }

class Py3status:
    routeNo = '3000' 
    stopNo = '95'
    direction = 'east'
    low_thresh = 15
    
    def __init__(self):
        self.button = None
        self.button_down = False
    
        path = os.path.abspath('git/py3status-octranspo/login')
    
        self.login_file = open(path)
        self.appID = self.login_file.readline().rstrip('\n')
        self.apiKey = self.login_file.readline().rstrip('\n')
    
    def OCTranspo(self):
        data = getJSON(self.appID, self.apiKey, self.routeNo, self.stopNo)
        
        # Display routeNo in red if no connection established
        if data == 'CONNECTION_ERROR':
            ft_error = self.py3.safe_format('  {routeNo}',
                    {
                      'routeNo': self.routeNo,
                      'stopNo': self.stopNo
                    })
            return {
                     'full_text': ft_error,
                     'color': self.py3.COLOR_LOW
                   }

        result = parseData(data, self.direction)

        colors = [self.py3.COLOR_SCHED] * 3

        for i in range(0, len(result['tripAges'])):
            if result['tripAges'][i] == "-1":
                colors[i] = self.py3.COLOR_SCHED
            else:
                colors[i] = self.py3.COLOR_GPS
            
            if int(result['tripTimes'][i]) <= self.low_thresh:
                colors[i] = self.py3.COLOR_LOW
        
        # For button toggling
        if self.button_down:
            self.button = None
            self.button_down = False

        # Button action for showing route destination 
        if self.button:
            ft_route_dir = self.py3.safe_format('  {routeNo} {routeLabel} - {stopLabel} (',
                    {
                        'routeNo': result['routeNo'],
                        'routeLabel': result['routeLabel'],
                        'stopLabel': result['stopLabel']
                    })
            self.button_down = True
        else:
            ft_route_dir = self.py3.safe_format(' {routeNo} {direction} (', 
                    { 
                      'routeNo': result['routeNo'], 
                      'direction': result['routeDir'][0], 
                    })

        ft_trips = [' '] * 3
        
        for i in range(0, len(result['tripTimes'])):
            if int(result['tripTimes'][i]) > 0:
                ft_trips[i] = self.py3.safe_format(result['tripTimes'][i])

        ft_separator = self.py3.safe_format(' / ')

        return {
                'cached_until': self.py3.time_in(50),
                'composite': [
                    {
                      'full_text': ft_route_dir,
                      'color': self.py3.COLOR_HIGH
                    },   
                    {
                      'full_text': ft_trips[0],
                      'color': colors[0]
                    },
                    {
                      'full_text': ft_separator,
                      'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trips[1],
                      'color': colors[1]
                    },
                    {
                      'full_text': ft_separator,
                      'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trips[2],
                      'color': colors[2]
                    },
                    {
                      'full_text': self.py3.safe_format(')'),
                      'color': self.py3.COLOR_HIGH
                    }
                ]
            }

    def on_click(self, event):
        self.button = event['button']

if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)
