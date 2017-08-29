import json, requests

def main():
    send_url = 'http://freegeoip.net/json'
    r = requests.get(send_url)
    j = json.loads(r.text)
    lat = j['latitude']
    lon = j['longitude']

    print(str(lat) + " " + str(lon))
if __name__ == "__main__": main()

