"""Name candidate clusters and check for mining/quarry land use within 3 km using OpenStreetMap (Nominatim + Overpass). Sends only coordinates."""
import requests, time, sys
UA = {"User-Agent": "subsidence-hotspot-check/1.0"}
C = {"Willcox basin core (D+A)": (32.103, -109.784), "N of Willcox (D+D+A)": (32.46, -109.96), "South / Elfrida? (D+A)": (31.728, -109.70),
     "East basin 1 (D only)": (32.213, -109.168), "East basin 2 (D only)": (32.310, -109.419),
     "Eloy-Picacho core": (32.650, -111.591), "S of Buckeye (2 D tracks)": (33.162, -112.659),
     "Sahuarita-A": (31.861, -111.130), "Sahuarita-B": (31.983, -111.058), "Ray?": (33.148, -110.968), "Morenci?": (33.127, -109.346),
     "Imperial Valley cluster": (32.406, -115.259), "(31.14,-112.89)": (31.140, -112.888)}
for n, (la, lo) in C.items():
    try:
        r = requests.get("https://nominatim.openstreetmap.org/reverse", params=dict(lat=la, lon=lo, format="jsonv2", zoom=12), headers=UA, timeout=30).json()
        place = r.get("display_name", "?")[:90]
    except Exception as e: place = f"geocode failed {type(e).__name__}"
    time.sleep(1.1)
    q = f'[out:json][timeout:40];(way(around:3000,{la},{lo})["landuse"~"quarry|industrial"];way(around:3000,{la},{lo})["industrial"~"mine"];way(around:3000,{la},{lo})["man_made"="tailings_pond"];nwr(around:3000,{la},{lo})["historic"="mine"];way(around:3000,{la},{lo})["landuse"="farmland"];);out tags 200;'
    try:
        els = requests.post("https://overpass-api.de/api/interpreter", data=q, headers=UA, timeout=90).json().get("elements", [])
        mine = sum(1 for e in els if e["tags"].get("landuse") == "quarry" or e["tags"].get("industrial") == "mine" or e["tags"].get("man_made") == "tailings_pond" or e["tags"].get("historic") == "mine")
        farm = sum(1 for e in els if e["tags"].get("landuse") == "farmland"); names = sorted({e["tags"].get("name") for e in els if e["tags"].get("name")})[:3]
        osm = f"OSM within 3 km: quarry/mine/tailings features {mine}, farmland polygons {farm}, names {names}"
    except Exception as e: osm = f"overpass failed {type(e).__name__}"
    print(f"{n}: {place}\n    {osm}")
    time.sleep(1.0)
