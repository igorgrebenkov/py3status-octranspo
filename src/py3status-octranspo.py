import json, requests

def main():
    stopNo = '61'
    
    payload = { 'appID': '8856da69',
                'apiKey': '63f69bfe2ea5e6e8b12511000f01d73c', 
                'routeNo': '95',
                'stopNo': '3000',
                'format': 'JSON' }

    r = requests.get('https://api.octranspo1.com/v1.2/GetNextTripsForStop', params = payload)
    
    print(r.url)
    data = r.json() 
    print("StopNo: " + data['GetNextTripsForStopResult']['StopNo'])
    print("Stop Label: " + data['GetNextTripsForStopResult']['StopLabel'])
    print("RouteNo: " + str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['RouteNo']))
    print("Trip 1: " + str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][0]['AdjustedScheduleTime']))
    print("Trip 2: " + str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][1]['AdjustedScheduleTime']))

    print("Trip 3: " + str(data['GetNextTripsForStopResult']['Route']['RouteDirection']['Trips']['Trip'][2]['AdjustedScheduleTime']))
if __name__ == "__main__": main()

