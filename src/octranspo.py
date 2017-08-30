# octranspo.py 
#   - A py3status module that fetches live GPS estimates for OCTranspo bus routes.

__author__ = "Igor Grebenkov"

import json, requests, os

# Module class
class Py3status:
    format = '{route} ({trips})'
    format_route = '{icon} {routeNo} {direction}'
    format_route_click = '{icon} {routeNo} {routeLabel} - {stopLabel} ({stopNo})'
    format_trip = '{trip}'
    format_error = '{icon} {routeNo}'

    t_icon = ''
    t_no_trip = '-'
    t_trip_separator = '/'

    routeNo = '221' 
    stopNo = '6908'
    direction = 'east'
    low_thresh = 15
    refresh_interval = 60
    max_trip_time = 60
    
    def __init__(self):
        self.button = None
        self.button_down = False
        self.UNSCHEDULED = self.t_no_trip
        self.NOGPS = '-1'
        
        # Path relative to ~ for API login details (appID, apiKey)
        # path = os.path.abspath('login')
        path = os.path.abspath('git/py3status-octranspo/login')
    
        self.login_file = open(path)
        self.appID = self.login_file.readline().rstrip('\n')
        self.apiKey = self.login_file.readline().rstrip('\n')

    # Fetches a JSON response from the OCTranspo API
    def _getJSON(self):
        payload = { 
                    'appID': self.appID,
                    'apiKey': self.apiKey, 
                    'routeNo': self.routeNo,
                    'stopNo': self.stopNo,
                    'format': 'JSON' 
                  }
        try:
            r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
            # print(r.url)
            return r.json()
        except Exception as e:
            return 'CONNECTION_ERROR'
        
    # Parses relevant data from the JSON response into a dict
    def _parseJSON(self, data):
        dirNo = 0 if self.direction == 'east' else 1
        
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
            
        tripTimes = [self.t_no_trip] * 3
        tripAges = [''] * 3

        # If there are trips, we populate tripTimes and tripAges
        if trips:
            if type(trips['Trip']) is list:
                trip_count = len(trips['Trip'])
             
                for i in range(0, trip_count):
                    trip_time = trips['Trip'][i]['AdjustedScheduleTime']

                    if int(trip_time) <= self.max_trip_time:
                        tripTimes[i] = trip_time

                    tripAges[i] = trips['Trip'][i]['AdjustmentAge']
            else:
                if trips['Trip']['AdjustedScheduleTime'] <= self.max_trip_time:
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

    # Assign self.colors based on whether time is GPS or not and based on low_thresh
    def _assignColors(self):
        self.colors = [self.py3.COLOR_SCHED] * 3
        for i in range(0, len(self.result['tripTimes'])):
            trip_time = self.result['tripTimes'][i]
            if trip_time == self.t_no_trip:
                self.colors[i] = self.py3.COLOR_SCHED
            elif self.result['tripAges'][i] == self.NOGPS:
                if int(trip_time) <= self.low_thresh:
                    self.colors[i] = self.py3.COLOR_LOW_SCHED
                else:
                    self.colors[i] = self.py3.COLOR_SCHED
            else:
                if int(trip_time) <= self.low_thresh:
                    self.colors[i] = self.py3.COLOR_LOW_GPS
                else:
                    self.colors[i] = self.py3.COLOR_GPS

    # Initialiazes the {route} string 
    def _initRouteString(self):
        # Enables button toggling
        if self.button_down:
            self.button = None
            self.button_down = False

        # Button action for showing route destination 
        if self.button:
            ft_route = self.py3.safe_format(
                    self.format_route_click,
                    {
                      'icon': self.t_icon,
                      'routeNo': self.result['routeNo'],
                      'routeLabel': self.result['routeLabel'],
                      'stopNo' : self.result['stopNo'],
                      'stopLabel': self.result['stopLabel']
                    })
            self.button_down = True
        else:
            ft_route = self.py3.safe_format(
                    self.format_route,
                    { 
                      'icon': self.t_icon,
                      'routeNo': self.result['routeNo'], 
                      'direction': self.result['routeDir'][0], 
                    })

        return ft_route

    # Initializes the {trips} string
    def _initTripsComposite(self):
        ft_trips = [' '] * 3
        for i in range(0, len(self.result['tripTimes'])):
            ft_trips[i] = self.py3.safe_format(
                    self.format_trip,
                    {
                      'trip': self.result['tripTimes'][i]
                    })
        
        ft_trips_dict = [{
                           'full_text': ft_trips[0],
                           'color': self.colors[0]
                         },
                         {
                           'full_text': self.t_trip_separator,
                           'color': self.py3.COLOR_HIGH
                         },
                         {
                           'full_text': ft_trips[1],
                           'color': self.colors[1]
                         },
                         {    
                           'full_text': self.t_trip_separator,
                           'color': self.py3.COLOR_HIGH
                         },
                         {
                           'full_text': ft_trips[2],
                           'color': self.colors[2]
                         }]

        return self.py3.composite_create(ft_trips_dict)

    # Main function run by py3status  
    def OCTranspo(self):
        data = self._getJSON()
        
        # Display {route} in COLOR_LOW_GPS if no connection established
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

        self.result = self._parseJSON(data)

        self._assignColors()

        output_composite = {
            'route': self._initRouteString(),
            'trips': self._initTripsComposite()
        } 

        return {
                'cached_until': self.py3.time_in(self.refresh_interval),
                'composite': self.py3.safe_format(self.format, output_composite)
            }
    
    # Function for button events
    def on_click(self, event):
        self.button = event['button']


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test
    module_test(Py3status)
