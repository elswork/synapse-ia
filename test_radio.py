import requests

STATIONS = {
    "noticias": [],
    "nacional": [],
    "electronica": [],
    "rock": [
        {"name": "Radio Paradise Rock", "url": "https://stream.radioparadise.com/rock-128"}
    ],
    "urbano": [],
    "pop": [],
    "world": [
        {"name": "KEXP (Seattle)", "url": "https://kexp-mp3-128.streamguys1.com/kexp128.mp3"},
        {"name": "FIP (France)", "url": "https://stream.radiofrance.fr/fip/fip.m3u8"}
    ],
    "relax": [],
    "ambient": [
        {"name": "SomaFM Drone Zone", "url": "https://ice1.somafm.com/dronezone-128-mp3"}
    ],
    "concentracion": [
        {"name": "Deep Focus", "url": "http://streaming.radionomy.com/DeepFocus"},
        {"name": "Binaural Beats", "url": "http://streaming.radionomy.com/BinauralBeats"},
        {"name": "Brain.fm (Sim)", "url": "http://ice.somafm.com/defcon"}
    ],
    "chill": [],
    "lofi": [
        {"name": "Lofi Girl Radio", "url": "http://play.sas-media.ru/play_256"}
    ],
    "jazz": [
        {"name": "Jazz24", "url": "https://live.wpmudev.org/jazz24/jazz24.mp3"},
        {"name": "Swiss Jazz", "url": "http://stream.srg-ssr.ch/m/rsj/mp3_128"}
    ],
    "clasica": [
        {"name": "WQXR New York", "url": "http://stream.wqxr.org/wqxr"},
        {"name": "Swiss Classic", "url": "http://stream.srg-ssr.ch/m/rsc_de/mp3_128"}
    ],
    "blues": [
        {"name": "Blues Radio", "url": "http://ice.streamguys.com/blues"},
        {"name": "GotRadio Blues", "url": "http://clt01.cdnstream.com/1458_128"}
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
