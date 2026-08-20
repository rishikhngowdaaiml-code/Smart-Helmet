import urllib.request
import json
try:
    with urllib.request.urlopen('http://ip-api.com/json/') as response:
        data = json.loads(response.read().decode())
        print(f"Lat: {data.get('lat')}, Lon: {data.get('lon')}")
        print(f"City: {data.get('city')}, {data.get('regionName')}, {data.get('country')}")
except Exception as e:
    print(e)
