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
    
    if type(data['GetNextTripsForStopResult']['Route']['RouteDirection']) is list:
        routeLabel = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteLabel']

        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Direction']

        trip1 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][0]['AdjustedScheduleTime'])


        trip2 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][1]['AdjustedScheduleTime'])

        trip3 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][2]['AdjustedScheduleTime'])
    
        trip1_age = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][0]['AdjustmentAge']
        trip2_age = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][1]['AdjustmentAge']
        trip3_age = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][2]['AdjustmentAge']
    else:
        routeLabel = data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteLabel']

        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Direction']

        trip1 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime'])

        trip2 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime'])

        trip3 = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustedScheduleTime'])

        trip1_age = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustmentAge']
        trip2_age = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustmentAge']
        trip3_age = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustmentAge']

    return { 'stopNo': stopNo,
             'stopLabel': stopLabel,
             'routeLabel': routeLabel,
             'routeNo': routeNo,
             'routeDir': routeDir,
             'trip1': trip1,
             'trip2': trip2,
             'trip3': trip3,
             'trip1_age': trip1_age,
             'trip2_age': trip2_age,
             'trip3_age': trip3_age
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

        # Assign color based on trip time relative to low_threshold 
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

        if result['trip1_age'] == "-1":
            result['trip1'] += " S"

        if result['trip2_age'] == "-1":
            result['trip2'] += " S"

        if result['trip3_age'] == "-1":
            result['trip3'] += " S"
        
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
        
        # Output text
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

        ft_separator = self.py3.safe_format(' / ')

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

    def on_click(self, event):
        self.button = event['button']
