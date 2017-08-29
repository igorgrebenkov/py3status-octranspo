import json, requests

def getJSON(routeNo, stopNo):
    payload = { 'appID': '8856da69',
                'apiKey': '63f69bfe2ea5e6e8b12511000f01d73c', 
                'routeNo': routeNo,
                'stopNo': stopNo,
                'format': 'JSON' }

    r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
    return r.json()

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
             'trip3': trip3 }
        
class Py3status:
    format = '{routeNo} {direction} - {trip1} / {trip2} / {trip3}'
    routeNo = '3000' 
    stopNo = '95'
    direction = 'east'

    def OCTranspo(self):
        data = getJSON(self.routeNo, self.stopNo)
        result = parseData(data, self.direction)
        full_text = self.py3.safe_format(self.format, 
                { 'routeNo': result['routeNo'], 
                  'direction': result['routeDir'][0], 
                  'trip1': result['trip1'], 
                  'trip2': result['trip2'], 
                  'trip3': result['trip3']
                })

        return {
                'full_text': full_text,
                'cached_until': self.py3.time_in(50) }

if __name__ == "__main__":
    from py3status.module_test import module_test
    module_test(Py3status)
