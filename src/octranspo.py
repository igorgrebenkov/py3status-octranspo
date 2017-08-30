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
def parseJSON(data, direction):
    if direction == 'east':
        dirNo = 0
    elif direction == 'west':
        dirNo = 1
        
    stopNo = data['GetNextTripsForStopResult']['StopNo']
    stopLabel = data['GetNextTripsForStopResult']['StopLabel']

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

    tripTimes = ['-'] * 3
    tripAges = ['-'] * 3

    # If there are trips, we populate tripTimes and tripAges
    if trips:
        if type(trips['Trip']) is list:
            trip_cnt = len(trips['Trip'])
    
            # Populate list of trip times and their adjustment ages
            for i in range(0, trip_cnt):
                tripTimes[i] = trips['Trip'][i]['AdjustedScheduleTime']
                tripAges[i] = trips['Trip'][i]['AdjustmentAge']
        else:
            tripTimes[0] = trips['Trip']['AdjustedScheduleTime']
            tripAges[0] = trips['Trip']['AdjustmentAge']
        
    return { 'stopNo': stopNo,
             'stopLabel': stopLabel,
             'routeLabel': routeLabel,
             'routeNo': routeNo,
             'routeDir': routeDir,
             'tripTimes': tripTimes,
             'tripAges': tripAges,
           }

# Module class
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
                    })
            return {
                     'full_text': ft_error,
                     'color': self.py3.COLOR_LOW_GPS
                   }

        result = parseJSON(data, self.direction)

        # Assign colors based on whether time is GPS or not and based on low_thresh
        colors = [self.py3.COLOR_SCHED] * 3

        for i in range(0, len(result['tripAges'])):
            if result['tripTimes'][i] == '-':
                colors[i] = self.py3.COLOR_SCHED
            elif result['tripAges'][i] == '-1':
                if int(result['tripTimes'][i]) <= self.low_thresh:
                    colors[i] = self.py3.COLOR_LOW_SCHED
                else:
                    colors[i] = self.py3.COLOR_SCHED
            else:
                if int(result['tripTimes'][i]) <= self.low_thresh:
                    colors[i] = self.py3.COLOR_LOW_GPS
                else:
                    colors[i] = self.py3.COLOR_GPS
        
        # Enables button toggling
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
        
        # Init and populate display strings for trip times
        ft_trips = [' '] * 3
        for i in range(0, len(result['tripTimes'])):
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
