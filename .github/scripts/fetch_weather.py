import os
import json
import time
import requests

OUTPUT_DIR = "data"
LATEST_FILE = os.path.join(OUTPUT_DIR, "latest_weather.json")

# 20 şehir: isim, enlem, boylam
CITIES = [
    ("Istanbul",     41.01, 28.97),
    ("Ankara",       39.93, 32.86),
    ("Izmir",        38.42, 27.14),
    ("Bursa",        40.19, 29.06),
    ("Antalya",      36.89, 30.71),
    ("Adana",        37.00, 35.32),
    ("Konya",        37.87, 32.48),
    ("Gaziantep",    37.07, 37.38),
    ("Sanliurfa",    37.16, 38.79),
    ("Mersin",       36.80, 34.63),
    ("Diyarbakir",   37.91, 40.24),
    ("Kayseri",      38.73, 35.49),
    ("Samsun",       41.29, 36.33),
    ("Denizli",      37.78, 29.09),
    ("Eskisehir",    39.78, 30.52),
    ("Malatya",      38.35, 38.31),
    ("Kahramanmaras",37.58, 36.94),
    ("Erzurum",      39.90, 41.27),
    ("Van",          38.49, 43.38),
    ("Trabzon",      41.00, 39.72),
]

def fetch_all_cities():
    lats = ",".join(str(c[1]) for c in CITIES)
    lons = ",".join(str(c[2]) for c in CITIES)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lats}&longitude={lons}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
        f"&timezone=Europe/Istanbul"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    iso_time = time.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        raw = fetch_all_cities()
    except Exception as e:
        print(f"[-] API hatası: {e}")
        return

    # Open-Meteo çoklu konum için liste döndürür
    results = raw if isinstance(raw, list) else [raw]

    output = {
        "fetched_at": iso_time,
        "city_count": len(CITIES),
        "cities": []
    }

    for city, data in zip(CITIES, results):
        name, lat, lon = city
        current = data.get("current", {})
        output["cities"].append({
            "name": name,
            "latitude": lat,
            "longitude": lon,
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "wind_kmh": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "observed_at": current.get("time"),
        })

    # 1) Zaman damgalı dosya (arşiv)
    archive_path = os.path.join(OUTPUT_DIR, f"weather_{timestamp}.json")
    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # 2) latest_weather.json (hep güncel, üzerine yazar)
    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[+] {len(output['cities'])} şehir kaydedildi")
    print(f"[+] Arşiv: {archive_path}")
    print(f"[+] Güncel: {LATEST_FILE}")

    # Konsolda da özet göster
    print("\nSıcaklıklar:")
    for c in output["cities"]:
        print(f"  {c['name']:15s} {c['temperature_c']:>5}°C  nem %{c['humidity_pct']}")

if __name__ == "__main__":
    main()
