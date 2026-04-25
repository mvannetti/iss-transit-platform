import os
import math
import json
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from skyfield.api import load, wgs84

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LOCAL_TZ = ZoneInfo("Europe/Rome")

# Primo passaggio grossolano
COARSE_STEP_SECONDS = 10

# Raffinamento intorno al candidato
REFINE_WINDOW_SECONDS = 20
REFINE_STEP_SECONDS = 1

SUN_RADIUS_KM = 696_340
MOON_RADIUS_KM = 1_737.4

stations_url = "https://celestrak.org/NORAD/elements/stations.txt"

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
user = config["users"][0]

LAT = user["lat"]
LON = user["lon"]
RADIUS_KM = user["radius_km"]
GRID_STEP_KM = user["grid_step_km"]
# Cerca nelle prossime ... ore
SEARCH_HOURS = user["search_hours"]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print(response.status_code)
    print(response.text)
    response.raise_for_status()


def generate_grid(lat, lon, radius_km, step_km):
    points = []

    for dx in range(-radius_km, radius_km + 1, step_km):
        for dy in range(-radius_km, radius_km + 1, step_km):
            distance = math.sqrt(dx**2 + dy**2)

            if distance <= radius_km:
                new_lat = lat + (dy / 111)
                new_lon = lon + (dx / (111 * math.cos(math.radians(lat))))
                points.append((new_lat, new_lon, distance))

    return points


def make_times(ts, start_dt, end_dt, step_seconds):
    times_dt = []
    current = start_dt

    while current <= end_dt:
        times_dt.append(current)
        current += timedelta(seconds=step_seconds)

    t = ts.utc(
        [d.year for d in times_dt],
        [d.month for d in times_dt],
        [d.day for d in times_dt],
        [d.hour for d in times_dt],
        [d.minute for d in times_dt],
        [d.second for d in times_dt],
    )

    return times_dt, t


def angular_radius_degrees(radius_km, distance_km):
    return math.degrees(math.asin(radius_km / distance_km))


def classify_transit(separation_deg, body_radius_deg):
    ratio = separation_deg / body_radius_deg

    if ratio <= 0.20:
        return "centrale"
    elif ratio <= 0.90:
        return "interno al disco"
    elif ratio <= 1.00:
        return "sul bordo del disco"
    else:
        return "fuori dal disco"


def check_body(
    body_name,
    body,
    body_radius_km,
    observer_ground,
    observer_space,
    iss,
    earth,
    times_dt,
    t,
):
    iss_pos = (iss - observer_ground).at(t)
    iss_alt, _, _ = iss_pos.altaz()

    body_pos = observer_space.at(t).observe(body).apparent()
    body_alt, _, body_distance = body_pos.altaz()

    separations = iss_pos.separation_from(body_pos).degrees

    candidates = []

    for i, sep in enumerate(separations):
        if iss_alt.degrees[i] <= 0:
            continue

        if body_alt.degrees[i] <= 0:
            continue

        body_radius_deg = angular_radius_degrees(body_radius_km, body_distance.km[i])

        # Margine grossolano per non perdere eventi nel primo scan
        if sep <= body_radius_deg + 0.15:
            candidates.append({
                "time": times_dt[i],
                "sep": sep,
                "body_radius_deg": body_radius_deg,
                "iss_alt": iss_alt.degrees[i],
                "body_alt": body_alt.degrees[i],
            })

    return candidates


def refine_candidate(
    candidate,
    body_name,
    body,
    body_radius_km,
    observer_ground,
    observer_space,
    iss,
    ts,
):
    start = candidate["time"] - timedelta(seconds=REFINE_WINDOW_SECONDS)
    end = candidate["time"] + timedelta(seconds=REFINE_WINDOW_SECONDS)

    times_dt, t = make_times(ts, start, end, REFINE_STEP_SECONDS)

    iss_pos = (iss - observer_ground).at(t)
    iss_alt, _, _ = iss_pos.altaz()

    body_pos = observer_space.at(t).observe(body).apparent()
    body_alt, _, body_distance = body_pos.altaz()

    separations = iss_pos.separation_from(body_pos).degrees

    inside_samples = []
    best = None

    for i, sep in enumerate(separations):
        if iss_alt.degrees[i] <= 0 or body_alt.degrees[i] <= 0:
            continue

        body_radius_deg = angular_radius_degrees(body_radius_km, body_distance.km[i])
        normalized = sep / body_radius_deg
        inside_disk = sep <= body_radius_deg

        sample = {
            "time": times_dt[i],
            "sep": sep,
            "body_radius_deg": body_radius_deg,
            "normalized": normalized,
            "iss_alt": iss_alt.degrees[i],
            "body_alt": body_alt.degrees[i],
            "inside_disk": inside_disk,
        }

        if inside_disk:
            inside_samples.append(sample)

        if best is None or sep < best["sep"]:
            best = sample

    if not inside_samples:
        return None

    first = inside_samples[0]
    last = inside_samples[-1]

    duration_seconds = (
        last["time"] - first["time"]
    ).total_seconds() + REFINE_STEP_SECONDS

    # Percorso sul disco:
    # normalized = 0 centro perfetto, 1 bordo.
    entry_pos = first["normalized"]
    closest_pos = best["normalized"]
    exit_pos = last["normalized"]

    if closest_pos <= 0.20:
        path_description = "passaggio vicino al centro"
    elif closest_pos <= 0.70:
        path_description = "passaggio interno al disco"
    elif closest_pos <= 1.00:
        path_description = "passaggio radente / vicino al bordo"
    else:
        path_description = "fuori dal disco"

    return {
        "name": body_name,
        "time": best["time"],
        "sep": best["sep"],
        "body_radius_deg": best["body_radius_deg"],
        "inside_disk": True,
        "type": classify_transit(best["sep"], best["body_radius_deg"]),
        "iss_alt": best["iss_alt"],
        "body_alt": best["body_alt"],
        "start_time": first["time"],
        "end_time": last["time"],
        "duration_seconds": duration_seconds,
        "entry_pos": entry_pos,
        "closest_pos": closest_pos,
        "exit_pos": exit_pos,
        "path_description": path_description,
    }


# Se parte in automatico, invia solo alle 7 italiane.
# Se lo lanci manualmente, funziona sempre.
event_name = os.environ.get("GITHUB_EVENT_NAME", "")
local_now = datetime.now(LOCAL_TZ)

if event_name == "schedule" and local_now.hour != 7:
    raise SystemExit("Non sono le 7 in Italia, esco senza inviare.")

ts = load.timescale()
eph = load("de421.bsp")

earth = eph["earth"]
sun = eph["sun"]
moon = eph["moon"]

satellites = load.tle_file(stations_url)

iss = None
for sat in satellites:
    if "ISS" in sat.name:
        iss = sat
        break

if iss is None:
    send_telegram("Errore: ISS non trovata nei dati TLE.")
    raise SystemExit

grid_points = generate_grid(LAT, LON, RADIUS_KM, GRID_STEP_KM)

now = datetime.now(timezone.utc).replace(tzinfo=None)
end = now + timedelta(hours=SEARCH_HOURS)

coarse_times_dt, coarse_t = make_times(ts, now, end, COARSE_STEP_SECONDS)

events = []

for lat, lon, dist_km in grid_points:
    observer_ground = wgs84.latlon(lat, lon)
    observer_space = earth + observer_ground

    sun_candidates = check_body(
        "Sole",
        sun,
        SUN_RADIUS_KM,
        observer_ground,
        observer_space,
        iss,
        earth,
        coarse_times_dt,
        coarse_t,
    )

    moon_candidates = check_body(
        "Luna",
        moon,
        MOON_RADIUS_KM,
        observer_ground,
        observer_space,
        iss,
        earth,
        coarse_times_dt,
        coarse_t,
    )

    for candidate in sun_candidates:
        refined = refine_candidate(
            candidate,
            "Sole",
            sun,
            SUN_RADIUS_KM,
            observer_ground,
            observer_space,
            iss,
            ts,
        )

        if refined and refined["inside_disk"]:
            refined["lat"] = lat
            refined["lon"] = lon
            refined["dist_km"] = dist_km
            events.append(refined)

    for candidate in moon_candidates:
        refined = refine_candidate(
            candidate,
            "Luna",
            moon,
            MOON_RADIUS_KM,
            observer_ground,
            observer_space,
            iss,
            ts,
        )

        if refined and refined["inside_disk"]:
            refined["lat"] = lat
            refined["lon"] = lon
            refined["dist_km"] = dist_km
            events.append(refined)

def group_events(events, max_seconds=60):
    events_sorted = sorted(events, key=lambda e: e["time"])
    grouped = []

    for event in events_sorted:
        if not grouped:
            grouped.append(event)
            continue

        last = grouped[-1]
        delta = abs((event["time"] - last["time"]).total_seconds())

        # Se è vicino nel tempo → stesso evento
        if delta < max_seconds:
            # tieni il migliore (separazione minore)
            if event["sep"] < last["sep"]:
                grouped[-1] = event
        else:
            grouped.append(event)

    return grouped

if not events:
    text = (
        "🚀 ISS Transit Bot\n\n"
        "Controllo giornaliero completato ✅\n\n"
        "Nessun transito ISS davanti a Sole o Luna "
        f"entro {RADIUS_KM} km nelle prossime {SEARCH_HOURS} ore.\n\n"
        f"Posizione centrale:\nLat {LAT}, Lon {LON}"
    )
else:
    grouped = group_events(events)

    text = "🚀 Transiti ISS trovati:\n"

    for i, e in enumerate(grouped, 1):
        local_time = e["time"].replace(tzinfo=ZoneInfo("UTC")).astimezone(LOCAL_TZ)
        start_local = e["start_time"].replace(tzinfo=ZoneInfo("UTC")).astimezone(LOCAL_TZ)
        end_local = e["end_time"].replace(tzinfo=ZoneInfo("UTC")).astimezone(LOCAL_TZ)
        
        maps_url = f"https://www.google.com/maps?q={e['lat']:.6f},{e['lon']:.6f}"

        text += (
            f"\n🔹 Evento {i}\n"
            f"Oggetto: {e['name']}\n"
            f"Tipo: {e['type']}\n"
            f"Data/ora migliore: {local_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
            f"Inizio stimato: {start_local.strftime('%H:%M:%S')}\n"
            f"Fine stimata: {end_local.strftime('%H:%M:%S')}\n"
            f"Durata stimata: {e['duration_seconds']:.1f} s\n"
            f"Percorso: {e['path_description']}\n"
            f"Entrata disco: {e['entry_pos']:.2f} r\n"
            f"Massimo avvicinamento: {e['closest_pos']:.2f} r\n"
            f"Uscita disco: {e['exit_pos']:.2f} r\n"
            f"Distanza: {e['dist_km']:.1f} km\n"
            f"Separazione: {e['sep']:.4f}°\n"
            f"Alt ISS: {e['iss_alt']:.1f}°\n"
            f"Alt {e['name']}: {e['body_alt']:.1f}°\n"
            f"Mappa: {maps_url}\n"
        )

    text += "\n📡 Eventi raggruppati per evitare duplicati"

send_telegram(text)
