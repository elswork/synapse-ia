import requests

STATIONS = {
    "noticias": [],
    "nacional": [],
    "electronica": [],
    "rock": [
        {"name": "Radio Paradise Rock", "url": "http://stream.radioparadise.com/rock-128"}
    ],
    "urbano": [],
    "pop": [],
    "world": [
        {"name": "KEXP (Seattle)", "url": "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"},
        {"name": "FIP (France)", "url": "https://stream.radiofrance.fr/fip/fip.m3u8"}
    ],
    "relax": [],
    "ambient": [
        {"name": "SomaFM Drone Zone", "url": "http://ice1.somafm.com/dronezone-128-mp3"}
    ],
    "concentracion": [
        {"name": "FreeCodeCamp Radio", "url": "https://coderadio-admin.freecodecamp.org/radio/8010/radio.mp3"},
        {"name": "SomaFM Def Con", "url": "http://ice1.somafm.com/defcon-128-mp3"},
        {"name": "Binaural Beats", "url": "https://stream.zeno.fm/4t9z2v7g128uv"}
    ],
    "chill": [],
    "lofi": [
        {"name": "Lofi Girl Radio", "url": "https://stream.zeno.fm/0r0xa792kwyvv"}
    ],
    "jazz": [
        {"name": "Jazz24", "url": "https://live.jazz24.org/jazz24-mp3"},
        {"name": "Swiss Jazz", "url": "http://stream.srg-ssr.ch/m/rsj/mp3_128"}
    ],
    "clasica": [
        {"name": "WQXR New York", "url": "http://stream.wqxr.org/wqxr"},
        {"name": "Swiss Classic", "url": "http://stream.srg-ssr.ch/m/rsc_de/mp3_128"}
    ],
    "blues": [
        {"name": "Blues Radio", "url": "http://pub1.streamguys.com:80/blues"},
        {"name": "GotRadio Blues", "url": "https://playerservices.streamtheworld.com/api/livestream-redirect/GOTRADIO_BLUES_BABE.mp3"}
    ]
}

def check_url(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code < 400:
            return True, response.status_code
        return False, response.status_code
    except Exception as e:
        return False, str(e)

results = {}
for genre, stations in STATIONS.items():
    results[genre] = []
    for st in stations:
        ok, status = check_url(st['url'])
        results[genre].append({"name": st['name'], "url": st['url'], "ok": ok, "status": status})
        print(f"[{'OK' if ok else 'FAIL'}] {st['name']} ({status})")

import json
with open('radio_results.json', 'w') as f:
    json.dump(results, f, indent=4)
