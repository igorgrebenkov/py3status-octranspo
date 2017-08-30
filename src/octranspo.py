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
    dirNo = 0 if direction == 'east' else 1
    
    stopNo = data['GetNextTripsForStopResult']['StopNo']
    stopLabel = data['GetNextTripsForStopResult']['StopLabel']
    
    route_direction = data['GetNextTripsForStopResult']['Route']['RouteDirection']
    
    # if 'RouteDirection' is a list, then we have to index the proper direction
    if type(route_direction) is list:
        routeLabel = route_direction[dirNo].get('RouteLabel') 
        routeNo = route_direction[dirNo].get('RouteNo')
        routeDir = route_direction[dirNo].get('Direction')
        trips = route_direction[dirNo].get('Trips') 
    else:
        routeLabel = route_direction.get('RouteLabel') 
        routeNo = route_direction.get('RouteNo')
        routeDir = route_direction.get('Direction')
        trips = route_direction.get('Trips') 
        
    tripTimes = ['-'] * 3
    tripAges = [''] * 3

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
    format = '{route} ({trips})'
    format_route = '{icon} {routeNo} {direction}'
    format_route_click = '{icon} {routeNo} {routeLabel} {separator} {stopLabel} ({stopNo})'
    format_trip = '{trip}'
    format_error = '{icon} {routeNo}'

    t_icon = ''
    t_separator = '-'
    t_trip_separator = '/'

    routeNo = '95' 
    stopNo = '3000'
    direction = 'east'
    low_thresh = 15
    
    def __init__(self):
        self.button = None
        self.button_down = False
        self.UNSCHEDULED = '-'
        self.NOGPS = '-1'
        
        # Path relative to ~ for API login details (appID, apiKey)
        path = os.path.abspath('git/py3status-octranspo/login')
    
        self.login_file = open(path)
        self.appID = self.login_file.readline().rstrip('\n')
        self.apiKey = self.login_file.readline().rstrip('\n')

    def OCTranspo(self):
        data = getJSON(self.appID, self.apiKey, self.routeNo, self.stopNo)
        
        # Display routeNo in red if no connection established
        if data == 'CONNECTION_ERROR':
            ft_error = self.py3.safe_format(
                    self.format_error,
                    {
                      'icon': self.t_icon,
                      'routeNo': self.routeNo
                    })
            return {
                     'full_text': ft_error,
                     'color': self.py3.COLOR_LOW_GPS
                   }

        result = parseJSON(data, self.direction)

        # Assign colors based on whether time is GPS or not and based on low_thresh
        colors = [self.py3.COLOR_SCHED] * 3

        for i in range(0, len(result['tripAges'])):
            trip_time = result['tripTimes'][i]

            if trip_time == self.UNSCHEDULED:
                colors[i] = self.py3.COLOR_SCHED
            elif result['tripAges'][i] == self.NOGPS:
                if int(trip_time) <= self.low_thresh:
                    colors[i] = self.py3.COLOR_LOW_SCHED
                else:
                    colors[i] = self.py3.COLOR_SCHED
            else:
                if int(trip_time) <= self.low_thresh:
                    colors[i] = self.py3.COLOR_LOW_GPS
                else:
                    colors[i] = self.py3.COLOR_GPS
        
        # Enables button toggling
        if self.button_down:
            self.button = None
            self.button_down = False

        # Button action for showing route destination 
        if self.button:
            ft_route_dir = self.py3.safe_format(
                    self.format_route_click,
                    {
                        'icon': self.t_icon,
                        'separator': self.t_separator,
                        'routeNo': result['routeNo'],
                        'routeLabel': result['routeLabel'],
                        'stopNo' : result['stopNo'],
                        'stopLabel': result['stopLabel']
                    })
            self.button_down = True
        else:
            ft_route_dir = self.py3.safe_format(
                    self.format_route,
                    { 
                      'icon': self.t_icon,
                      'routeNo': result['routeNo'], 
                      'direction': result['routeDir'][0], 
                    })

        # Init and populate display strings for trip times
        ft_trips = [' '] * 3
        for i in range(0, len(result['tripTimes'])):
            ft_trips[i] = self.py3.safe_format(
                    self.format_trip,
                    {
                      'trip': result['tripTimes'][i]
                    })
        
        ft_trips_display = [{
                             'full_text': ft_trips[0],
                             'color': colors[0]
                           },
                           {
                             'full_text': self.t_trip_separator,
                             'color': self.py3.COLOR_HIGH
                           },
                           {
                            'full_text': ft_trips[1],
                            'color': colors[1]
                          },
                          {
                            'full_text': self.t_trip_separator,
                            'color': self.py3.COLOR_HIGH
                          },
                          {
                            'full_text': ft_trips[2],
                            'color': colors[2]
                          }]

        composites = {
            'route': self.py3.composite_create(ft_route_dir),
            'trips': self.py3.composite_create(ft_trips_display)
        } 

        return {
                'cached_until': self.py3.time_in(50),
                'composite': self.py3.safe_format(self.format, composites)
            }

    def on_click(self, event):
        self.button = event['button']

if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)
