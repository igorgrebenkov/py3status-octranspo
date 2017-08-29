import json, requests

class Py3status:
    def __init__(self):
        
        payload = { 'appID': '8856da69',
                    'apiKey': '63f69bfe2ea5e6e8b12511000f01d73c', 
                    'routeNo': '61',
                    'stopNo': '6908',
                    'format': 'JSON' }
        
        r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
        data = r.json()

        self.stopNo = data['GetNextTripsForStopResult']['StopNo']
        self.stopLabel = data['GetNextTripsForStopResult']['StopLabel']
        self.routeNo = str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo'])
        self.trip1 = str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime'])
        self.trip2 = str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime'])
        self.trip3 = str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustedScheduleTime'])
        self.full_text = self.routeNo + " (" + self.trip1 + " / " + self.trip2 + " / " + self.trip3 + ")"
    
    def octranspo(self):
        return {
            'full_text': self.full_text,
            'cached_until': self.py3.CACHE_FOREVER
        }
