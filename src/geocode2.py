import requests, time
UA = {"User-Agent": "subsidence-hotspot-check/1.0"}
C = {"W-central A (33.847,-113.496)": (33.847, -113.496), "W-central B (33.938,-113.361)": (33.938, -113.361), "Bagdad? (34.58,-113.23)": (34.580, -113.23), "Tonopah-ish (33.442,-113.236)": (33.442, -113.236), "NE speck (34.606,-109.444)": (34.606, -109.444)}
for n, (la, lo) in C.items():
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse", params=dict(lat=la, lon=lo, format="jsonv2", zoom=12), headers=UA, timeout=20).json(); place = r.get("display_name", "?")[:100]
    except Exception as e: place = "geocode failed " + type(e).__name__
    time.sleep(1.1)
    q = f'[out:json][timeout:30];(way(around:3000,{la},{lo})["landuse"~"quarry|farmland|industrial"];way(around:3000,{la},{lo})["man_made"="tailings_pond"];nwr(around:3000,{la},{lo})["historic"="mine"];);out tags 80;'
    osm = "overpass unavailable"
    for server in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
        try:
            els = requests.post(server, data=q, headers=UA, timeout=40).json().get("elements", [])
            mine = sum(1 for e in els if e["tags"].get("landuse") == "quarry" or e["tags"].get("man_made") == "tailings_pond" or e["tags"].get("historic") == "mine")
            farm = sum(1 for e in els if e["tags"].get("landuse") == "farmland"); names = sorted({e["tags"].get("name") for e in els if e["tags"].get("name")})[:3]
            osm = f"mine/quarry/tailings {mine}, farmland {farm}, names {names}"; break
        except Exception as e: continue
    print(f"{n}: {place}\n    {osm}", flush=True)
