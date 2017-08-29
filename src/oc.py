import json, requests

class Py3status:
    
    format = '{routeNo} {direction} - {trip1} / {trip2} / {trip3}'
    routeNo = '0' 
    stopNo = '0'
    direction = ''
    
    def octranspo(self):
        payload = { 'appID': '8856da69',
                    'apiKey': '63f69bfe2ea5e6e8b12511000f01d73c', 
                    'routeNo': self.routeNo,
                    'stopNo': self.stopNo,
                    'format': 'JSON' }
        
        r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
        data = r.json()
        
        if self.direction == 'east':
            dirNo = 0
        elif self.direction == 'west':
            dirNo = 1

        self.stopNo = data['GetNextTripsForStopResult']['StopNo']
        self.stopLabel = data['GetNextTripsForStopResult']['StopLabel']
        
        if type(data['GetNextTripsForStopResult']['Route']['RouteDirection']) is list:
            self.routeNo = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['RouteNo'])

            self.routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Direction']

            self.trip1 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][0]['AdjustedScheduleTime'])

            self.trip2 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][1]['AdjustedScheduleTime'])

            self.trip3 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection'][dirNo]['Trips']['Trip'][2]['AdjustedScheduleTime'])
        else:
            self.routeNo = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])

            self.routeDir = data['GetNextTripsForStopResult']['Route']['RouteDirection']['Direction']

            self.trip1 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime'])

            self.trip2 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime'])

            self.trip3 = str(
                    data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustedScheduleTime'])
            
        self.full_text = self.routeNo + " (" + self.trip1 + " / " + self.trip2 + " / " + self.trip3 + ")"
        
        full_text = self.py3.safe_format(self.format, 
                {'routeNo': self.routeNo, 'direction': self.routeDir[0], 'trip1': self.trip1, 'trip2': self.trip2, 'trip3': self.trip3})

        return {
                'full_text': full_text,
                'cached_until': self.py3.CACHE_FOREVER
        }
