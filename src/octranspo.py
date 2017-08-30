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
        
        trip_list = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'] 
    else:
        routeLabel = data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteLabel']

        routeNo = str(
                data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])

        routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Direction']

        trip_list = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'] 

    trip_cnt = len(trip_list)
    
    # Populate list of trip times and their adjustment ages
    for i in range(0, trip_cnt):
        tripTimes.append(trip_list[i]['AdjustedScheduleTime'])
        tripAges.append(trip_list[i]['AdjustmentAge'])
        
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
        
        # if result['trip1_age'] == "-1":
        #     color1 = self.py3.COLOR_SCHED
        # else:
        #     color1 = self.py3.COLOR_GPS

        # if result['trip2_age'] == "-1":
        #     color2 = self.py3.COLOR_SCHED
        # else:
        #     color2 = self.py3.COLOR_GPS

        # if result['trip3_age'] == "-1":
        #     color3 = self.py3.COLOR_SCHED
        # else:
        #     color3 = self.py3.COLOR_GPS

        # # Assign color based on trip time relative to low_threshold 
        # if int(result['trip1']) <= self.low_thresh:
        #     color1 = self.py3.COLOR_LOW
        
        # if int(result['trip2']) <= self.low_thresh:
        #     color2 = self.py3.COLOR_LOW
        
        # if int(result['trip3']) <= self.low_thresh:
        #     color3 = self.py3.COLOR_LOW
        
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
                  'trip1': result['tripTimes'][0], 
                })
        
        ft_trip2 = self.py3.safe_format('{trip2}', 
                {
                  'trip2': result['tripTimes'][1], 
                })
        
        ft_trip3 = self.py3.safe_format('{trip3}', 
                {
                  'trip3': result['tripTimes'][2], 
                })

        ft_separator = self.py3.safe_format(' / ')

        return {
                'cached_until': self.py3.time_in(50),
                'composite': [
                    {
                      'full_text': ft_route_dir,
                      # 'color': self.py3.COLOR_HIGH
                    },   
                    {
                      'full_text': ft_trip1,
                      # 'color': color1
                    },
                    {
                      'full_text': ft_separator,
                      # 'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trip2,
                      # 'color': color2
                    },
                    {
                      'full_text': ft_separator,
                      # 'color': self.py3.COLOR_HIGH
                    },
                    {
                      'full_text': ft_trip3,
                      # 'color': color3
                    },
                    {
                      'full_text': self.py3.safe_format(')'),
                      # 'color': self.py3.COLOR_HIGH
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
