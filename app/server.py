from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timedelta, date
import json, mimetypes, traceback, threading, hashlib, os, sqlite3, urllib.request, urllib.error
import swisseph as swe

BASE = Path(__file__).resolve().parent
APP_VERSION = "4.1 PHKS Cloud Test + Dynamic Deep Analysis"
APP_NAME = "HelaJyotishyaPHKS"
PORT = int(os.environ.get("PORT", "8765"))


# --- Desktop local data store (SQLite) ---
def _user_data_dir():
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    p = Path(root) / "HelaJyotishya" / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p

DB_PATH = _user_data_dir() / "hela_jyotishya.sqlite3"
DB_LOCK = threading.RLock()

def _db_connect():
    con = sqlite3.connect(str(DB_PATH), timeout=10)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)")
    return con

def localdb_get_all():
    with DB_LOCK:
        con=_db_connect()
        try:
            rows=con.execute("SELECT key,value FROM app_state ORDER BY key").fetchall()
            out={}
            for k,v in rows:
                try: out[k]=json.loads(v)
                except Exception: out[k]=v
            return out
        finally: con.close()

def localdb_set(key, value):
    key=str(key or "").strip()
    if not key or len(key)>200: raise ValueError("Invalid storage key")
    payload=json.dumps(value, ensure_ascii=False, separators=(",",":"))
    if len(payload.encode("utf-8")) > 12_000_000: raise ValueError("Stored value is too large")
    with DB_LOCK:
        con=_db_connect()
        try:
            con.execute("INSERT INTO app_state(key,value,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at", (key,payload,datetime.now().isoformat(timespec="seconds")))
            con.commit()
        finally: con.close()

def localdb_delete(key):
    with DB_LOCK:
        con=_db_connect()
        try:
            con.execute("DELETE FROM app_state WHERE key=?", (str(key),)); con.commit()
        finally: con.close()

def localdb_restore(state):
    if not isinstance(state, dict): raise ValueError("Backup data is invalid")
    with DB_LOCK:
        con=_db_connect()
        try:
            con.execute("BEGIN")
            con.execute("DELETE FROM app_state")
            now=datetime.now().isoformat(timespec="seconds")
            for k,v in state.items():
                key=str(k)[:200]
                payload=json.dumps(v, ensure_ascii=False, separators=(",",":"))
                if len(payload.encode("utf-8")) > 12_000_000: continue
                con.execute("INSERT OR REPLACE INTO app_state(key,value,updated_at) VALUES(?,?,?)", (key,payload,now))
            con.commit()
        except Exception:
            con.rollback(); raise
        finally: con.close()

def localdb_info():
    with DB_LOCK:
        con=_db_connect()
        try:
            count=con.execute("SELECT COUNT(*) FROM app_state").fetchone()[0]
        finally: con.close()
    try: size=DB_PATH.stat().st_size
    except Exception: size=0
    return {"records":count,"bytes":size,"file":str(DB_PATH)}

# --- PHKS Creation commercial access control ---
ACCESS_MODE = os.environ.get("HELA_ACCESS_MODE", "paid").strip().lower()
TRIAL_LIMIT = max(1, int(os.environ.get("HELA_TRIAL_LIMIT", "10")))
PUBLISHER = os.environ.get("HELA_PUBLISHER", "PHKS Creation")
SUPPORT_WHATSAPP = os.environ.get("HELA_WHATSAPP", "+94715954563")
TRIAL_USAGE_KEY = "__phks_trial_calculation_usage__"

def _trial_usage():
    try:
        return int(localdb_get_all().get(TRIAL_USAGE_KEY, 0) or 0)
    except Exception:
        return 0

def _trial_remaining():
    return max(0, TRIAL_LIMIT - _trial_usage())

def _trial_consume():
    if ACCESS_MODE != "trial": return
    used = _trial_usage()
    if used >= TRIAL_LIMIT:
        raise PermissionError(f"Trial limit reached. PHKS Creation WhatsApp {SUPPORT_WHATSAPP}")
    localdb_set(TRIAL_USAGE_KEY, used + 1)

def commercial_state():
    return {
        "ok": True, "mode": ACCESS_MODE, "publisher": PUBLISHER,
        "whatsapp": SUPPORT_WHATSAPP, "trial_limit": TRIAL_LIMIT,
        "trial_used": _trial_usage() if ACCESS_MODE == "trial" else 0,
        "trial_remaining": _trial_remaining() if ACCESS_MODE == "trial" else None,
        "paid_only": ["porondam", "muhurta"] if ACCESS_MODE == "trial" else []
    }

swe.set_sid_mode(swe.SIDM_LAHIRI)

RASHI = ["මේෂ","වෘෂභ","මිථුන","කටක","සිංහ","කන්‍යා","තුලා","වෘශ්චික","ධනු","මකර","කුම්භ","මීන"]
RASHI_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
NAK = ["අස්විද","බෙරණ","කැති","රෙහෙණ","මුවසිරස","අද","පුනාවස","පුෂ","අස්ලිය","මා","පුවපල්","උත්‍රපල්","හත","සිත","සා","විසා","අනුර","දෙට","මුල","පුවසල","උත්‍රසල","සුවණ","දෙනට","සියාවස","පුවපුටුප","උත්‍රපුටුප","රේවතී"]
NAK_EN = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
PLANETS = {
    "Sun": ("රවි", swe.SUN),
    "Moon": ("චන්ද්‍ර", swe.MOON),
    "Mars": ("කුජ", swe.MARS),
    "Mercury": ("බුධ", swe.MERCURY),
    "Jupiter": ("ගුරු", swe.JUPITER),
    "Venus": ("ශුක්‍ර", swe.VENUS),
    "Saturn": ("ශනි", swe.SATURN),
    "Rahu": ("රාහු", swe.MEAN_NODE),
}
PLANET_ORDER = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
PLANET_SI = {"Sun":"රවි","Moon":"චන්ද්‍ර","Mars":"කුජ","Mercury":"බුධ","Jupiter":"ගුරු","Venus":"ශුක්‍ර","Saturn":"ශනි","Rahu":"රාහු","Ketu":"කේතු"}
DASHA_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_SI = {"Ketu":"කේතු","Venus":"ශුක්‍ර","Sun":"රවි","Moon":"චන්ද්‍ර","Mars":"කුජ","Rahu":"රාහු","Jupiter":"ගුරු","Saturn":"ශනි","Mercury":"බුධ"}
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
NAK_LORD = [DASHA_LORDS[i % 9] for i in range(27)]

GANA = ["Deva","Manushya","Rakshasa","Manushya","Deva","Manushya","Deva","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Rakshasa","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva"]
GANA_SI = {"Deva":"දේව","Manushya":"මනුෂ්‍ය","Rakshasa":"රාක්ෂස"}
RAJJU = ["Pada","Kati","Nabhi","Kantha","Siro","Kantha","Nabhi","Kati","Pada","Pada","Kati","Nabhi","Kantha","Siro","Kantha","Nabhi","Kati","Pada","Pada","Kati","Nabhi","Kantha","Siro","Kantha","Nabhi","Kati","Pada"]
RAJJU_SI = {"Pada":"පාද","Kati":"කටි","Nabhi":"නාභි","Kantha":"කණ්ඨ","Siro":"ශිර"}
VEDHA_PAIRS = {(1,18),(2,17),(3,16),(4,15),(5,23),(6,22),(7,21),(8,20),(9,19),(10,27),(11,26),(12,25),(13,24)}
RASHI_LORD = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
FRIENDS = {
    "Sun":{"Moon","Mars","Jupiter"}, "Moon":{"Sun","Mercury"},
    "Mars":{"Sun","Moon","Jupiter"}, "Mercury":{"Sun","Venus"},
    "Jupiter":{"Sun","Moon","Mars"}, "Venus":{"Mercury","Saturn"},
    "Saturn":{"Mercury","Venus"}
}


def norm(x):
    return x % 360


def rashi_info(lon):
    lon = norm(lon)
    idx = int(lon // 30)
    return {"index": idx, "number": idx+1, "name": RASHI[idx], "english": RASHI_EN[idx], "degree": round(lon % 30, 4)}


def nak_info(lon):
    lon = norm(lon)
    span = 360/27
    idx = min(26, int(lon // span))
    inside = lon - idx*span
    pada = min(4, int(inside / (span/4)) + 1)
    return {"index":idx, "number":idx+1, "name":NAK[idx], "english":NAK_EN[idx], "pada":pada, "inside_degree":round(inside,4), "lord":NAK_LORD[idx], "gana":GANA[idx]}


def navamsa_info(lon):
    lon = norm(lon)
    sign = int(lon // 30)
    part = min(8, int((lon % 30) // (30/9)))
    modality = sign % 3
    if modality == 0:
        start = sign
    elif modality == 1:
        start = (sign + 8) % 12
    else:
        start = (sign + 4) % 12
    nav_sign = (start + part) % 12
    return {"index":nav_sign, "number":nav_sign+1, "name":RASHI[nav_sign], "english":RASHI_EN[nav_sign], "navamsa_part":part+1}


def local_to_utc(d, t, tz):
    local = datetime.strptime(f"{d} {t}", "%Y-%m-%d %H:%M")
    return local - timedelta(hours=tz)


def jd_from_dt(dt):
    hour = dt.hour + dt.minute/60 + dt.second/3600
    return swe.julday(dt.year, dt.month, dt.day, hour)


def is_sri_lanka_coords(lat, lon):
    return 5.5 <= float(lat) <= 10.2 and 79.3 <= float(lon) <= 82.2


def sri_lanka_historical_offset(local_dt):
    if local_dt < datetime(1906, 1, 1):
        return None
    if local_dt < datetime(1942, 1, 5, 0, 0):
        return 5.5
    if local_dt < datetime(1942, 9, 1, 0, 0):
        return 6.0
    if local_dt < datetime(1945, 10, 16, 2, 0):
        return 6.5
    if local_dt < datetime(1996, 5, 25, 0, 0):
        return 5.5
    if local_dt < datetime(1996, 10, 26, 0, 30):
        return 6.5
    if local_dt < datetime(2006, 4, 15, 0, 30):
        return 6.0
    return 5.5


def effective_timezone_offset(data):
    entered = float(data.get("timezone_offset", 5.5))
    try:
        local_dt = datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
    except Exception:
        return entered, "manual"
    if is_sri_lanka_coords(data.get("latitude", 0), data.get("longitude", 0)):
        auto = sri_lanka_historical_offset(local_dt)
        if auto is not None:
            return auto, "Asia/Colombo historical"
    return entered, "manual"


def calc_ut_compat(jd, pid, flags):
    result = swe.calc_ut(jd, pid, flags)
    if not isinstance(result, (tuple, list)) or len(result) < 2:
        raise RuntimeError("Swiss Ephemeris returned an unexpected calc_ut result")
    data = result[0]
    retflag = result[1]
    serr = result[2] if len(result) >= 3 else ""
    if data is None or len(data) < 4:
        raise RuntimeError("Swiss Ephemeris returned incomplete planetary data")
    return data, retflag, serr


def planet_positions(jd):
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    for key, (si, pid) in PLANETS.items():
        data, retflag, serr = calc_ut_compat(jd, pid, flags)
        lon = norm(data[0])
        out[key] = {
            "key": key,
            "name": si,
            "longitude": round(lon, 6),
            "rashi": rashi_info(lon),
            "nakshatra": nak_info(lon),
            "navamsa": navamsa_info(lon),
            "retrograde": bool(data[3] < 0)
        }
    klon = norm(out["Rahu"]["longitude"] + 180)
    out["Ketu"] = {
        "key": "Ketu",
        "name": "කේතු",
        "longitude": round(klon, 6),
        "rashi": rashi_info(klon),
        "nakshatra": nak_info(klon),
        "navamsa": navamsa_info(klon),
        "retrograde": True
    }
    return out


def ascendant(jd, lat, lon):
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    a = norm(ascmc[0])
    return {"longitude": round(a, 6), "rashi": rashi_info(a), "nakshatra": nak_info(a), "navamsa": navamsa_info(a)}


def whole_sign_house(planet_sign, lagna_sign):
    return ((planet_sign - lagna_sign) % 12) + 1


def dasha_timeline(birth_dt_local, moon_lon):
    n = nak_info(moon_lon)
    lord = n["lord"]
    span = 360/27
    fraction_elapsed = n["inside_degree"] / span
    elapsed_years = DASHA_YEARS[lord] * fraction_elapsed
    current_start = birth_dt_local - timedelta(days=elapsed_years * 365.2425)
    start_lord_index = DASHA_LORDS.index(lord)
    periods = []
    cursor = current_start
    for k in range(12):
        l = DASHA_LORDS[(start_lord_index + k) % 9]
        end = cursor + timedelta(days=DASHA_YEARS[l] * 365.2425)
        periods.append({
            "lord": l,
            "name": DASHA_SI[l],
            "years": DASHA_YEARS[l],
            "start": cursor.date().isoformat(),
            "end": end.date().isoformat()
        })
        cursor = end
    today = date.today()
    current = next((p for p in periods if date.fromisoformat(p["start"]) <= today < date.fromisoformat(p["end"])), None)
    return {"birth_nakshatra_lord": lord, "periods": periods, "current": current}


def fixed_sign_chart(planets, lagna, chart_type="rashi"):
    cells = [{"sign_index": i, "sign": RASHI[i], "planets": []} for i in range(12)]
    for p in planets.values():
        ref = p["rashi"] if chart_type == "rashi" else p.get("navamsa", p["rashi"])
        label = p["name"] + (" ℞" if p.get("retrograde") and chart_type == "rashi" else "")
        cells[ref["index"]]["planets"].append(label)
    lag_ref = lagna["rashi"] if chart_type == "rashi" else lagna.get("navamsa", lagna["rashi"])
    lag_label = "ලග්න" if chart_type == "rashi" else "නවාංශ ලග්න"
    cells[lag_ref["index"]]["planets"].insert(0, lag_label)
    return cells


def house_summary(planets, lagna_idx):
    houses = []
    for h in range(1, 13):
        sign_index = (lagna_idx + h - 1) % 12
        plist = [p["name"] for p in planets.values() if p["house"] == h]
        houses.append({
            "house": h,
            "rashi": RASHI[sign_index],
            "lord": DASHA_SI.get(RASHI_LORD[sign_index], RASHI_LORD[sign_index]),
            "planets": plist
        })
    return houses


def house_strength(planets, house_nums):
    return [p for p in planets.values() if p.get("house") in house_nums]


def lord_house_for_sign(sign_index, planets):
    lord = RASHI_LORD[sign_index % 12]
    p = planets.get(lord)
    return lord, (p.get("house") if p else None)


def planet_house_text(planets, key):
    p = planets.get(key, {})
    return p.get("house"), p.get("rashi", {}).get("name", "")


def expanded_reading(lagna, planets, dasha, reference=False):
    lag_i = lagna["rashi"]["index"]
    lag = lagna["rashi"]["name"]
    moon = planets["Moon"]["rashi"]["name"]
    nak = planets["Moon"]["nakshatra"]["name"]
    pada = planets["Moon"]["nakshatra"].get("pada", "")
    houses = {h: [p["name"] for p in planets.values() if p.get("house") == h] for h in range(1,13)}

    lag_lord, lag_lord_house = lord_house_for_sign(lag_i, planets)
    second_lord, second_lord_house = lord_house_for_sign((lag_i+1)%12, planets)
    third_lord, third_lord_house = lord_house_for_sign((lag_i+2)%12, planets)
    fourth_lord, fourth_lord_house = lord_house_for_sign((lag_i+3)%12, planets)
    fifth_lord, fifth_lord_house = lord_house_for_sign((lag_i+4)%12, planets)
    sixth_lord, sixth_lord_house = lord_house_for_sign((lag_i+5)%12, planets)
    seventh_lord, seventh_lord_house = lord_house_for_sign((lag_i+6)%12, planets)
    eighth_lord, eighth_lord_house = lord_house_for_sign((lag_i+7)%12, planets)
    ninth_lord, ninth_lord_house = lord_house_for_sign((lag_i+8)%12, planets)
    tenth_lord, tenth_lord_house = lord_house_for_sign((lag_i+9)%12, planets)
    eleventh_lord, eleventh_lord_house = lord_house_for_sign((lag_i+10)%12, planets)
    twelfth_lord, twelfth_lord_house = lord_house_for_sign((lag_i+11)%12, planets)

    current = dasha.get("current")
    current_lord = current.get("lord") if current else ""
    current_planet = planets.get(current_lord) if current_lord else None
    next_period = None
    if current and dasha.get("periods"):
        for i, period in enumerate(dasha["periods"]):
            if period.get("start") == current.get("start") and i + 1 < len(dasha["periods"]):
                next_period = dasha["periods"][i+1]
                break

    mars_house = planets["Mars"].get("house")
    rahu_house = planets["Rahu"].get("house")
    ketu_house = planets["Ketu"].get("house")
    sat_house = planets["Saturn"].get("house")
    jup_house = planets["Jupiter"].get("house")
    ven_house = planets["Venus"].get("house")
    merc_house = planets["Mercury"].get("house")
    sun_house = planets["Sun"].get("house")
    moon_house = planets["Moon"].get("house")
    retro = [p["name"] for p in planets.values() if p.get("retrograde")]

    def lord_si(x): return DASHA_SI.get(x, x)
    def house_planets(h): return ", ".join(houses[h]) if houses[h] else "ප්‍රධාන ග්‍රහයක් නොමැත"

    summary = [
        f"මෙම කේන්දරයේ ලග්නය {lag}, චන්ද්‍ර රාශිය {moon}, ජන්ම නැකත {nak} සහ {pada} වන පාදය ලෙස පෙනේ.",
        f"ලග්නාධිපති {lord_si(lag_lord)} {lag_lord_house} වන භාවයේ පිහිටීම නිසා ජීවිතයේ මූලික දිශාව එම භාවයට අදාළ කරුණු සමඟ දැඩිව බැඳී පවතී.",
        f"රැකියාව හා සමාජ ස්ථානය බලන 10 වන භාවයේ අධිපති {lord_si(tenth_lord)} {tenth_lord_house} වන භාවයේ සිටින බැවින් වෘත්තීය ප්‍රගතිය එම භාවයේ කරුණු හරහා වර්ධනය විය හැක.",
        f"මුදල් හා ලාභ සඳහා 2 වන භාවයේ අධිපති {lord_si(second_lord)} {second_lord_house} වන භාවයේත් 11 වන භාවයේ අධිපති {lord_si(eleventh_lord)} {eleventh_lord_house} වන භාවයේත් පිහිටා ඇත.",
    ]
    if current:
        line=f"දැනට {current['name']} මහා දශාව ක්‍රියාත්මක වේ"
        if current.get('start') or current.get('end'):
            line += f" ({current.get('start','')} සිට {current.get('end','')} දක්වා)"
        summary.append(line + ".")
    if retro:
        summary.append("වක්‍රගති ග්‍රහ ලෙස " + ", ".join(retro) + " සටහන් වේ. සාම්ප්‍රදායිකව වක්‍ර ග්‍රහයක ප්‍රතිඵල නැවත නැවත සිතීම, ප්‍රමාදය හෝ අභ්‍යන්තරව වැඩි බලයක් ලෙස පළවිය හැකි බව සලකයි.")

    personality=(
        f"{lag} ලග්නය පුද්ගලයා පිටතට පෙන්වන හැසිරීම, තීරණ ගැනීම සහ ජීවිතයට ප්‍රතිචාර දක්වන ආකාරය ගැන මූලික ඉඟියක් දෙයි. "
        f"ලග්නාධිපති {lord_si(lag_lord)} {lag_lord_house} වන භාවයේ සිටීම නිසා එම භාවයේ කරුණු ජීවිතයේ නැවත නැවත ඉස්මතු විය හැක. "
        f"චන්ද්‍රයා {moon_house} වන භාවයේ සිටීමෙන් මනස වැඩිපුර යොමු වන අංශය පෙන්වයි. "
        "උදාහරණයක් ලෙස, ලග්නාධිපති 10 හෝ 11 වැනි භාවයක තිබේ නම් වෘත්තීය නම, ජාල සම්බන්ධතා සහ අරමුණු ඉටු කිරීම ගැන දැඩි අවධානයක් ඇති විය හැක; 4 වැනි භාවයක නම් නිවස, පවුල සහ අභ්‍යන්තර සැනසීම වැඩි වැදගත්කමක් ගනී."
    )
    mind=(
        f"චන්ද්‍ර රාශිය {moon} සහ ජන්ම නැකත {nak} එකට බලන විට හැඟීම් පාලනය, මතකය, අභ්‍යන්තර ආරක්ෂාව සහ දෛනික මානසික රටාව විග්‍රහ කරයි. "
        f"චන්ද්‍රයා {moon_house} වන භාවයේ සිටීම නිසා එම භාවයට අදාළ සිදුවීම් මනසට ඉක්මනින් බලපාන්න පුළුවන්. "
        "උදාහරණයක් ලෙස, වැඩ හෝ අධ්‍යාපනයේ කුඩා ප්‍රමාදයක් වුණත් දිගටම සිතන ස්වභාවයක් තිබේ නම් ඒ කාලවල නිදාගැනීම, සැලසුම් ලියා තැබීම සහ තීරණ එකවර නොගැනීම ප්‍රායෝගිකව උපකාරී වේ."
    )
    family=(
        f"2 වන භාවයේ අධිපති {lord_si(second_lord)} {second_lord_house} වන භාවයේ සිටීම පවුල, වචන භාවිතය, ඉතිරි කිරීම සහ පවුල් වගකීම් ගැන කියවීමට භාවිතා කරයි. "
        f"4 වන භාවයේ අධිපති {lord_si(fourth_lord)} {fourth_lord_house} වන භාවයේ සිටීම නිවස, මව්පාර්ශවය, ඉඩකඩම් සහ අභ්‍යන්තර සැනසීම සම්බන්ධ කරුණු පෙන්වයි. "
        "උදාහරණයක් ලෙස, 2 සහ 4 භාව අධිපතිවරුන් වෘත්තීය භාව සමඟ සම්බන්ධ නම් පවුලේ වගකීම් සහ රැකියා තීරණ එකිනෙකට සෘජුව බලපාන කාල එන්න පුළුවන්."
    )
    siblings=(
        f"3 වන භාවය සහ එහි අධිපති {lord_si(third_lord)} {third_lord_house} වන භාවයේ සිටීම සහෝදර සහෝදරියන්, ධෛර්යය, කෙටි ගමන්, අත්කම්, ලිවීම සහ තමන්ම ආරම්භ කරන වැඩ ගැන විග්‍රහයට යොදාගනී. "
        "3 වන භාවය ශක්තිමත් නම් අලුත් කුසලතාවක් නැවත නැවත පුහුණු කරගෙන වැඩි දියුණු වීමේ හැකියාවක් පෙන්වයි. උදාහරණයක් ලෙස, රැකියාවක් සමඟ අමතර ව්‍යාපෘතියක්, අන්තර්ජාල සේවාවක් හෝ නිර්මාණාත්මක වැඩක් ආරම්භ කිරීමට උනන්දුව පෙන්විය හැක."
    )
    education=(
        f"අධ්‍යාපනය සඳහා 4, 5 සහ 9 වන භාවයන් එකට බලයි. 5 වන භාවයේ අධිපති {lord_si(fifth_lord)} {fifth_lord_house} වන භාවයේත්, 9 වන භාවයේ අධිපති {lord_si(ninth_lord)} {ninth_lord_house} වන භාවයේත් සිටී. "
        f"බුධ {merc_house} වන භාවයේ සිටීම භාෂා, ගණිතය, ලේඛන, තාක්ෂණික දැනුම සහ ව්‍යාපාරික බුද්ධිය පිළිබඳ ඉඟියක් දෙයි. "
        "උදාහරණයක් ලෙස, එක දිගටම පොතකින් ඉගෙනීමට වඩා වැඩ කරමින්, ව්‍යාපෘති කරමින්, පුහුණු පාඨමාලා හෝ සහතික ලබාගනිමින් ඉගෙනීම වඩා හොඳ ප්‍රතිඵල දෙන රටාවක් පෙන්විය හැක."
    )
    career=(
        f"10 වන භාවයේ අධිපති {lord_si(tenth_lord)} {tenth_lord_house} වන භාවයේ සිටින අතර 10 වන භාවයේ {house_planets(10)}. "
        f"ශනි {sat_house} වන භාවයේ සහ බුධ {merc_house} වන භාවයේ සිටීම වෘත්තීය ස්ථාවරත්වය, වගකීම්, තාක්ෂණික වැඩ, කළමනාකරණය සහ සැලසුම් කිරීම සමඟ සම්බන්ධ කර බලයි. "
        "උදාහරණයක් ලෙස, ශනි බලවත් වෘත්තීය කාලයකදී ප්‍රගතිය අඩු වේගයෙන් පෙනුනත් වසර කිහිපයකින් නිල තනතුරක්, වැඩි වගකීමක් හෝ විශ්වාසය ලැබීම වැනි ස්ථාවර ප්‍රතිඵල ලබාගත හැක. රැකියා මාරුවක් ගැන සිතන විට දශා මාරුව සහ 10 වන භාවයට ගෝචර බලය එකට සසඳා බැලීම සුදුසුය."
    )
    business=(
        f"ව්‍යාපාර සඳහා 3, 7, 10 සහ 11 වන භාවයන් සලකයි. 7 වන භාවයේ අධිපති {lord_si(seventh_lord)} {seventh_lord_house} වන භාවයේත් 11 වන භාවයේ අධිපති {lord_si(eleventh_lord)} {eleventh_lord_house} වන භාවයේත් සිටී. "
        "මෙය හවුල් ව්‍යාපාර, පාරිභෝගික සම්බන්ධතා, අලෙවිය, සේවා සැපයීම සහ සම්බන්ධතා මගින් ලැබෙන ආදායම ගැන විග්‍රහයට වැදගත්ය. "
        "උදාහරණයක් ලෙස, 7 සහ 11 භාව සම්බන්ධතාවය හොඳ නම් තනිව වැඩ කරනවාට වඩා විශ්වාසදායක හවුල්කරුවෙකු, නිත්‍ය පාරිභෝගික පිරිසක් හෝ නියෝජිත ජාලයක් හරහා ව්‍යාපාරය වර්ධනය විය හැක."
    )
    finance=(
        f"2 වන භාවයේ අධිපති {lord_si(second_lord)} {second_lord_house} වන භාවයේත් 11 වන භාවයේ අධිපති {lord_si(eleventh_lord)} {eleventh_lord_house} වන භාවයේත් සිටීම ආදායම, ඉතිරි කිරීම සහ ලාභ සම්බන්ධ ප්‍රධාන සූචක වේ. "
        f"ගුරු {jup_house} වන භාවයේ සිටීම දිගුකාලීන වර්ධනය සහ දැනුම හරහා ලැබෙන ලාභ සමඟ සම්බන්ධ කරයි. "
        "උදාහරණයක් ලෙස, කෙටි කාලයක ඉක්මන් ලාභයකට වඩා මාසික ඉතිරි කිරීම, කුසලතා වැඩි කිරීම සහ ස්ථාවර ආදායම් මාර්ග දෙකක් ගොඩනැගීම වඩා හොඳ රටාවක් විය හැක. ජ්‍යෝතිෂ්‍ය විග්‍රහයක් පමණක් මත ණය, ආයෝජන හෝ විශාල මුදල් තීරණ නොගත යුතුය."
    )
    marriage=(
        f"විවාහය සඳහා 7 වන භාවය, එහි අධිපති {lord_si(seventh_lord)} සහ ශුක්‍රයා වැදගත්ය. 7 වන අධිපති {seventh_lord_house} වන භාවයේත් ශුක්‍ර {ven_house} වන භාවයේත් සිටී. "
        + (f"කුජ {mars_house} වන භාවයේ සිටීම නිසා කුජ/භෞම දෝෂ සමානතාව වෙනම සසඳා බැලීම සුදුසුය. " if mars_house in {1,2,4,7,8,12} else "") +
        "උදාහරණයක් ලෙස, 7 වන භාවයට ශනි බලයක් ඇත්නම් විවාහය ප්‍රමාද වීම හෝ වගකීම් වැඩි සම්බන්ධතාවයක් ඇති විය හැකි අතර, ගුරු හෝ ශුක්‍ර යහපත් බලයක් ඇත්නම් සමගිය හා අවබෝධය වැඩි කිරීමට උදව් වන බව සාම්ප්‍රදායිකව සලකයි. අවසාන තීරණයට දෙපාර්ශවයේ චරිත, ආර්ථික තත්ත්වය සහ ප්‍රායෝගික ගැලපීමත් අනිවාර්යයෙන් බලන්න."
    )
    children=(
        f"5 වන භාවය දරුවන්, නිර්මාණශීලීත්වය සහ ඉගෙනීමේ ප්‍රතිඵල සම්බන්ධ කර බලයි. එහි අධිපති {lord_si(fifth_lord)} {fifth_lord_house} වන භාවයේ සිටින අතර ගුරු {jup_house} වන භාවයේ සිටී. "
        "උදාහරණයක් ලෙස, 5 වන භාවයට යහපත් බලපෑම් වැඩි නම් ඉගැන්වීම, නිර්මාණය, දරුවන් සමඟ කටයුතු කිරීම හෝ නව අදහස් ව්‍යාපෘතියක් බවට පත් කිරීමේ හැකියාවක් පෙන්විය හැක. දරු ලැබීම වැනි සෞඛ්‍ය කරුණු සම්බන්ධයෙන් කේන්දරයක් පමණක් මත තීරණ නොගෙන වෛද්‍ය උපදෙස් ලබාගත යුතුය."
    )
    foreign=(
        f"විදේශ ගමන්, දිගු ගමන් සහ පදිංචි වෙනස්කම් සඳහා 9 සහ 12 භාවයන් බලයි. 12 වන භාවයේ අධිපති {lord_si(twelfth_lord)} {twelfth_lord_house} වන භාවයේත් රාහු {rahu_house} වන භාවයේත් සිටී. "
        "රාහු, 9 වන භාවය හෝ 12 වන භාවය වෘත්තීය භාව සමඟ සම්බන්ධ වුණොත් විදේශ රැකියා, වෙනත් භාෂා/සංස්කෘතික පරිසර හෝ දුරස්ථ සම්බන්ධතා මගින් අවස්ථා ලැබීමේ ඉඟියක් ලෙස බලයි. "
        "උදාහරණයක් ලෙස, දශාවක් 9/12 භාව අධිපතිවරුන් සක්‍රීය කරන කාලයක රැකියා වීසා, අධ්‍යාපන වීසා හෝ දිගුකාලීන පදිංචි මාරුවක් ගැන වැඩි ක්‍රියාකාරීත්වයක් ඇති විය හැක."
    )
    property_text=(
        f"4 වන භාවයේ අධිපති {lord_si(fourth_lord)} {fourth_lord_house} වන භාවයේ සිටීම නිවස, ඉඩම්, වාහන සහ ස්ථාවර දේපළ විග්‍රහයට වැදගත්ය. කුජ {mars_house} සහ ශුක්‍ර {ven_house} වන භාවයන් ද මේ කරුණට අමතර බලයක් දෙයි. "
        "උදාහරණයක් ලෙස, 4 වන භාවය දශාවක සක්‍රීය වුණොත් නිවසක් මාරු කිරීම, වාහනයක් ගැනීම හෝ ඉඩමක් ගැන සිතීම වැනි කරුණු ඉස්මතු විය හැක. එවැනි තීරණවලදී මුදල් හැකියාව, නීතිමය ලේඛන සහ තාක්ෂණික පරීක්ෂණ වෙනම කළ යුතුය."
    )
    status=(
        f"9, 10 සහ 11 වන භාවයන් සමාජ ගෞරවය, වෘත්තීය නම, සහයෝගී සම්බන්ධතා සහ දිගුකාලීන ලාභ සඳහා බලයි. 9 වන අධිපති {lord_si(ninth_lord)} {ninth_lord_house} වන භාවයේත් 10 වන අධිපති {lord_si(tenth_lord)} {tenth_lord_house} වන භාවයේත් 11 වන අධිපති {lord_si(eleventh_lord)} {eleventh_lord_house} වන භාවයේත් සිටී. "
        "උදාහරණයක් ලෙස, 10 සහ 11 භාව සම්බන්ධතාවයක් හොඳ නම් වැඩ කරන තැන හඳුනාගැනීම, උසස් නිලධාරීන්ගේ විශ්වාසය, වෘත්තීය සම්බන්ධතා හරහා අලුත් අවස්ථා ලැබීම වැනි ප්‍රතිඵල ඇති විය හැක."
    )
    wellbeing=(
        f"1, 6 සහ 8 වන භාවයන් ශක්තිය, දෛනික වැඩ පීඩනය සහ නැවත ශක්තිමත් වීමේ රටාව සංකේතාත්මකව විග්‍රහ කිරීමට භාවිතා කරයි. 6 වන භාවයේ අධිපති {lord_si(sixth_lord)} {sixth_lord_house} වන භාවයේත් 8 වන අධිපති {lord_si(eighth_lord)} {eighth_lord_house} වන භාවයේත් සිටී. "
        f"ශනි {sat_house}, කුජ {mars_house}, රාහු {rahu_house} සහ කේතු {ketu_house} යන පිහිටීම් අනුව වැඩ බර, නින්ද සහ දෛනික රටාව පාලනය කිරීම ප්‍රයෝජනවත්. "
        "උදාහරණයක් ලෙස, වැඩ අධික කාලයක නින්ද කපා දැමීම, ආහාර වේලාව අක්‍රමවත් කිරීම සහ දිගටම ආතතියෙන් සිටීම වැළැක්වීම ප්‍රායෝගික උපදෙසකි. සෞඛ්‍ය ගැටලුවකට කේන්දරය භාවිතා නොකර වෛද්‍ය උපදෙස් ලබාගන්න."
    )
    dasha_text="විම්ශෝත්තරී දශා ක්‍රමය අනුව කාලයක් තුළ සක්‍රීය වන ග්‍රහයා එම කාලයේ ප්‍රධාන තේමාව පෙන්වන බව සාම්ප්‍රදායිකව සලකයි."
    if current:
        p_house=current_planet.get('house') if current_planet else None
        p_sign=current_planet.get('rashi',{}).get('name','') if current_planet else ''
        dasha_text += f" දැනට {current['name']} මහා දශාව ක්‍රියාත්මක වන අතර එම ග්‍රහයා ජන්ම කේන්දරයේ {p_house or '—'} වන භාවයේ {p_sign or '—'} රාශියේ සිටී. එම භාවයට අදාළ කරුණු මේ කාලයේ වැඩිපුර ඉස්මතු විය හැක."
        if dasha.get('antardasha'):
            dasha_text += f" දැනට සටහන් වන අතුරු දශාව {dasha['antardasha']} වේ. මහා දශා ග්‍රහයා සහ අතුරු දශා ග්‍රහයා දෙදෙනාගේ භාව/රාශි සම්බන්ධතාවය කෙටි කාලීන සිදුවීම්වල ස්වභාවය වෙනස් කළ හැක."
    if next_period:
        dasha_text += f" ඊළඟ මහා දශාව {next_period['name']} වෙත මාරුවෙන විට ජීවිතයේ ප්‍රමුඛතා සහ අවස්ථා රටාව වෙනස් විය හැක. උදාහරණයක් ලෙස, රැකියා භාවයක් සක්‍රීය කරන දශාවක රැකියා මාරුවක් හෝ උසස්වීමක් ගැන වැඩි ක්‍රියාකාරීත්වයක් පෙනිය හැක."

    timing=(
        "නිශ්චිත මාසයක් හෝ දිනයක් ගැන බලන විට ජන්ම දශාව, අතුරු දශාව, ප්‍රත්‍යන්තර දශාව සහ ඒ දිනයේ ගෝචර ග්‍රහ පිහිටීම් එකට සලකා බලන්න ඕන. "
        "උදාහරණයක් ලෙස, 10 වන භාවය සක්‍රීය කරන දශාවක් යන අතර ගුරු 10 හෝ 11 වන භාවයට යහපත් ගෝචරයක් දෙන කාලයක් රැකියා අවස්ථාවක්, වගකීමක් හෝ ප්‍රසිද්ධියක් වැඩි විය හැකි කාලයක් ලෙස සලකන්න පුළුවන්. "
        "එහෙත් එක් ග්‍රහ පිහිටීමක් පමණක් මත නිශ්චිත සිදුවීමක් තහවුරු නොකළ යුතුය."
    )
    if current and current.get('end'):
        timing += f" වත්මන් මහා දශාව {current['end']} දක්වා පවතින බැවින්, එම දිනයට පෙර අවසන් මාස කිහිපය සහ පසුව ආරම්භ වන දශාව වෙන වෙනම විග්‍රහ කිරීම වඩා හොඳය."

    saturn_text=(
        f"ජන්ම ශනි {sat_house} වන භාවයේ සිටී. ශනි සාම්ප්‍රදායිකව ප්‍රමාදය, වගකීම, දීර්ඝකාලීන මහන්සිය, නීතිය සහ අත්දැකීම් හරහා පරිණත වීම සමඟ සම්බන්ධ කරයි. "
        + ("මෙම පිහිටීම නිසා සමහර වැඩ ඉක්මනින් නොසාර්ථක වුවත් නැවත නැවත උත්සාහ කළ විට ස්ථාවර ප්‍රතිඵල ලැබීමේ රටාවක් පෙන්විය හැක. " if sat_house in {1,4,7,8,10,12} else "උපචය ස්ථානයක ශනි බලය කාලයත් සමඟ වැඩි ප්‍රතිඵල දෙන බව සාම්ප්‍රදායිකව සලකයි. ")+
        "උදාහරණයක් ලෙස, රැකියා ප්‍රගතිය මාස කිහිපයකින් නොව වසර කිහිපයකින් ගොඩනැගෙන්න පුළුවන්; ඒ නිසා කෙටි මාර්ග වෙනුවට සහතික, පළපුරුද්ද සහ විනය ගොඩනැගීම ප්‍රයෝජනවත්."
    )
    nodes_text=(
        f"රාහු {rahu_house} වන භාවයේත් කේතු {ketu_house} වන භාවයේත් සිටීම නිසා මෙම භාව දෙකේ අක්ෂය ජීවිතයේ අසාමාන්‍ය වෙනස්කම්, දැඩි ආකර්ෂණය සහ පසුව වෙන්වීම් හැඟීමක් ඇති කරන ප්‍රදේශයක් ලෙස සලකයි. "
        "රාහු ඉක්මන් ආකර්ෂණය, අලුත් තාක්ෂණය, විදේශ සම්බන්ධතා සහ අසාමාන්‍ය අවස්ථා පෙන්වන්න පුළුවන්; කේතු අභ්‍යන්තර පරීක්ෂාව, සරල කිරීම සහ සමහර දේවල් වලින් වෙන්වීමේ රටාවක් පෙන්වයි. "
        "උදාහරණයක් ලෙස, රාහු 10/11 භාව සම්බන්ධ නම් අන්තර්ජාලය, විදේශ සමාගම් හෝ නව ක්ෂේත්‍රයක් හරහා රැකියා අවස්ථාවක් ලැබිය හැකි නමුත් ගිවිසුම් සහ පොරොන්දු දෙවරක් පරීක්ෂා කිරීම වැදගත්ය."
    )
    mars_text=(
        f"කුජ {mars_house} වන භාවයේ සිටීම ක්‍රියාශීලීත්වය, තරඟකාරීත්වය, ඉක්මන් තීරණ සහ ආවේගය සමඟ සම්බන්ධ කර බලයි. "
        + ("විවාහ ගැලපීමේදී ලග්නය, චන්ද්‍රය සහ ශුක්‍රය යන තුනෙන්ම කුජ දෝෂ සමානතාව සසඳා බැලීම සුදුසුය. " if mars_house in {1,2,4,7,8,12} else "මෙම පිහිටීම ප්‍රධාන කුජ දෝෂ භාවයක නොපෙනුණත් දෘෂ්ටි සහ අධිපති සම්බන්ධතාද බලන්න ඕන. ")+
        "උදාහරණයක් ලෙස, කුජ බලවත් කාලයක රැකියා/ව්‍යාපාර තීරණ වේගයෙන් ගන්න හිතෙන්න පුළුවන්; එවැනි වෙලාවක ලියවිලි කියවලා පැය 24ක් හෝ දවසක් තබා තීරණය කිරීම ප්‍රායෝගික පිළියමක්."
    )

    challenges=[]
    if mars_house in {1,2,4,7,8,12}: challenges.append("කුජ බලය නිසා ආවේගය, වාද විවාද, ඉක්මන් වාහන/දේපළ තීරණ හෝ සම්බන්ධතා ආතතිය ඇතිවිය හැකි කාලවල තීරණ ප්‍රමාද කර නැවත සලකා බැලීම හොඳයි.")
    if sat_house in {1,4,7,8,10,12}: challenges.append("ශනි බලය නිසා ප්‍රමාද, වගකීම් සහ දිගුකාලීන මහන්සිය අවශ්‍ය විය හැක. ප්‍රතිඵල පෙනෙන්නේ නැති නිසා මැදින් අත්හැරීම වෙනුවට කුඩා පියවරවලින් ඉදිරියට යාම සුදුසුය.")
    if rahu_house in {1,5,7,8,10,12}: challenges.append("රාහු බලය ඇති අංශවල අධික බලාපොරොත්තු, අවුල්කාරී තත්ත්ව, හදිසි වෙනස්කම් හෝ සාමාන්‍යයෙන් නොකරන තේරීම් ඇතිවිය හැක. ලේඛන, ණය, රැකියා කොන්ත්‍රාත් සහ විදේශ ගිවිසුම් දෙවරක් පරීක්ෂා කරන්න.")
    if ketu_house in {1,4,7,8,12}: challenges.append("කේතු බලය ඇති අංශවල අකමැත්ත, වෙන්වීම් හැඟීම හෝ හදිසි රුචි වෙනස්කම් පෙන්විය හැකි නිසා දිගුකාලීන තීරණ හදිසියේ නොගැනීම හොඳයි.")
    if not challenges: challenges.append("මෙම මූලික පරීක්ෂාවෙන් දැඩි අපලයක් ලෙස නම් කළ යුතු තත්ත්වයක් නොපෙනේ. එහෙත් දශා සහ ගෝචර මාරුව අනුව කාලික අභියෝග වෙනස් විය හැක.")

    opportunities=[]
    if jup_house in {1,2,5,9,10,11}: opportunities.append("ගුරුගේ පිහිටීම අධ්‍යාපනය, උපදේශනය, වෘත්තීය වර්ධනය හෝ ආදායම් වර්ධනයට සහාය දෙන ලකුණක් ලෙස සලකන්න පුළුවන්.")
    if ven_house in {1,4,5,7,9,10,11}: opportunities.append("ශුක්‍රගේ පිහිටීම සබඳතා, නිර්මාණශීලීත්වය, අලංකරණය, සේවා ක්ෂේත්‍ර හෝ සමාජ සම්බන්ධතා හරහා අවස්ථා ලැබීමේ ඉඟියක් ලබා දිය හැක.")
    if merc_house in {1,2,3,5,6,10,11}: opportunities.append("බුධගේ පිහිටීම ඉගෙනීම, භාෂා, තාක්ෂණය, අලෙවිය, ගණනය සහ ලේඛන කටයුතු හරහා දියුණුවීමට හොඳ හැකියාවක් පෙන්විය හැක.")
    if not opportunities: opportunities.append("අවස්ථා විග්‍රහයේදී දශා අධිපති, 9/10/11 භාව අධිපති සහ ගුරු ගෝචරය එකට බලන එක වඩා නිවැරදියි.")

    remedies_common=[
        "පිළියම්වල මූලික අරමුණ බිය ඇති කිරීම නොව, අසමතුලිත රටාවක් පාලනය කිරීමට හොඳ හැසිරීම්, පින්කම් සහ සංයමය ගොඩනැගීමයි.",
        "තම ආගමට හා විශ්වාසයට ගැලපෙන පින්කම්, දාන, ප්‍රාර්ථනා, භාවනා, වැඩිහිටියන්ට සහ අවශ්‍යතා ඇති අයට උදව් කිරීම වගේ අඩු වියදම් යහපත් ක්‍රියා තෝරාගන්න.",
        "අධික මුදල් ඉල්ලන යන්ත්‍ර, රත්න, විශේෂ පූජා හෝ තහවුරු කළ නොහැකි පොරොන්දු අනිවාර්ය පිළියම් ලෙස පිළිගන්න එපා. රත්න හෝ සෞඛ්‍ය සම්බන්ධ දෙයක් ආරම්භ කිරීමට පෙර අදාළ වෘත්තීය උපදෙස් ගන්න.",
    ]
    planet_remedies=[]
    if current:
        lord=current.get('lord')
        if lord=='Saturn':
            planet_remedies += [
                "ශනි කාලයට: සෙනසුරාදා හෝ සතියේ සුදුසු දිනක වැඩිහිටියෙකුට, දුෂ්කරතාවයක සිටින පවුලකට හෝ සේවකයෙකුට ආහාර/අවශ්‍ය දේ ලබාදීම වැනි සේවාවක් කරන්න.",
                "ප්‍රායෝගික උදාහරණය: රැකියා ප්‍රමාදයක් තිබේ නම් සතියකට අයදුම්පත් 5ක්, මාසයකට එක් කුසලතා පාඩමක්, ණය/බිල් නියමිත දිනයට ගෙවීම වැනි විනයානුකූල ක්‍රමයක් තබාගන්න."
            ]
        elif lord=='Rahu':
            planet_remedies += [
                "රාහු කාලයට: අසත්‍ය පොරොන්දු, සැක සහිත ණය, නොපැහැදිලි ගිවිසුම් සහ හදිසි අන්තර්ජාල ගනුදෙනු වලින් වැළකී සිටීම වැදගත් පිළියමක් ලෙස සලකන්න.",
                "ප්‍රායෝගික උදාහරණය: විදේශ රැකියා හෝ ව්‍යාපාර ගිවිසුමක් නම් නම, ලිපිනය, මුදල් කොන්දේසි සහ අවලංගු කිරීමේ නීති ලිඛිතව තහවුරු කර පසුව අත්සන් කරන්න."
            ]
        elif lord=='Ketu':
            planet_remedies += [
                "කේතු කාලයට: භාවනා, නිශ්ශබ්ද කාලයක්, අනවශ්‍ය වැඩ අඩු කිරීම සහ එකවර ඉලක්ක කිහිපයක් වෙනුවට ප්‍රධාන ඉලක්ක දෙක තුනක් තෝරාගැනීම සුදුසුය.",
                "ප්‍රායෝගික උදාහරණය: සම්බන්ධතාවයක් හෝ රැකියාවක් හදිසියේ අත්හැරීමට හිතෙනවා නම් තීරණය දින කිහිපයක් තබා හේතු ලියා බලන්න."
            ]
        elif lord=='Mars':
            planet_remedies += [
                "කුජ කාලයට: ශාරීරික ක්‍රියාකාරකම්, විනය, වාදයට පෙර නිහඬවීම සහ වාහන/යන්ත්‍ර භාවිතයේ සැලකිල්ල වැඩි කිරීම ප්‍රායෝගික පිළියම් වේ.",
                "ප්‍රායෝගික උදාහරණය: කෝපයෙන් පණිවිඩයක් යැවීමට පෙර විනාඩි 30ක් තබා නැවත කියවා යවන්න."
            ]
        elif lord=='Mercury':
            planet_remedies += [
                "බුධ කාලයට: ඉගෙනීම, ලිවීම, ගණනය නිවැරදි කිරීම සහ කුඩා දරුවන්ගේ/ශිෂ්‍යයන්ගේ අධ්‍යාපනයට උදව් කිරීම යහපත් ක්‍රියා ලෙස සලකයි.",
                "ප්‍රායෝගික උදාහරණය: ලේඛනයක්, අයදුම්පතක් හෝ ගිවිසුමක් යැවීමට පෙර අංක, දිනය සහ නම දෙවරක් පරීක්ෂා කරන්න."
            ]
        elif lord=='Jupiter':
            planet_remedies += [
                "ගුරු කාලයට: ගුරුවරුන්ට, මව්පියන්ට හෝ දැනුම ලබාදෙන අයට ගෞරවය දක්වමින් අධ්‍යාපනික දාන/උදව් කිරීම යහපත් ලෙස සලකයි.",
                "ප්‍රායෝගික උදාහරණය: වෘත්තීය දියුණුවක් අවශ්‍ය නම් එක් පිළිගත් පාඨමාලාවක් හෝ සහතිකයක් තෝරා අවසන් කරන්න."
            ]
        elif lord=='Venus':
            planet_remedies += [
                "ශුක්‍ර කාලයට: සබඳතා තුළ ගරුක කථනය, පිරිසිදුකම, කලාව/සංගීතය වැනි සන්සුන් ක්‍රියා සහ පවුලේ සමගිය රැකීම වැදගත්ය.",
                "ප්‍රායෝගික උදාහරණය: සබඳතාවයක ගැටලුවක් නම් තෙවන පුද්ගලයෙකු ඉදිරියේ වාද කරනවාට වඩා දෙදෙනාටම සුදුසු වේලාවක් තෝරා සන්සුන්ව සාකච්ඡා කරන්න."
            ]
        elif lord=='Moon':
            planet_remedies += [
                "චන්ද්‍ර කාලයට: නිදාගැනීමේ වේලාව, පවුල් සමගිය, ජලය පානය කිරීම, මනස සන්සුන් කරන ආගමික/භාවනා ක්‍රියා සහ මව්පාර්ශවයට ගෞරවය දක්වීම යහපත් ලෙස සලකයි.",
                "ප්‍රායෝගික උදාහරණය: හැඟීම් වැඩි දවසක විශාල මුදල් හෝ සම්බන්ධතා තීරණයක් එදිනම නොගෙන පසුදා නැවත බලන්න."
            ]
        elif lord=='Sun':
            planet_remedies += [
                "රවි කාලයට: මව්පියන්/වැඩිහිටියන්ට ගෞරවය, උදෑසන ක්‍රමවත් ආරම්භයක්, වගකීමෙන් නායකත්වය දීම සහ අහංකාර වාද අඩු කිරීම යහපත්ය.",
                "ප්‍රායෝගික උදාහරණය: නිලධාරී ගැටලුවක් තිබේ නම් වාචික වාදයට වඩා ලිඛිත සාක්ෂි සහ සන්සුන් පැහැදිලි කිරීම භාවිතා කරන්න."
            ]
    if not planet_remedies:
        planet_remedies.append("වත්මන් දශාව සටහන් වී නොමැති නම් සාමාන්‍ය පිළියම් ලෙස පින්කම්, සංයමය, සදාචාරාත්මක ක්‍රියා සහ ප්‍රායෝගික සැලසුම්කරණය තෝරාගන්න.")

    sections=[
        {"title":"1. සමස්ත ජීවිත ස්වභාවය","text":personality},
        {"title":"2. මනස, හැඟීම් සහ තීරණ ගැනීම","text":mind},
        {"title":"3. පවුල, වචනය සහ ගෘහ ජීවිතය","text":family},
        {"title":"4. ධෛර්යය, සහෝදරයන් සහ තමන්ගේ උත්සාහ","text":siblings},
        {"title":"5. අධ්‍යාපනය, දැනුම සහ කුසලතා","text":education},
        {"title":"6. රැකියාව සහ වෘත්තීය දිශාව","text":career},
        {"title":"7. ව්‍යාපාර, හවුල්කාරීත්වය සහ පාරිභෝගික සම්බන්ධතා","text":business},
        {"title":"8. මුදල්, ඉතිරි කිරීම සහ ලාභ","text":finance},
        {"title":"9. විවාහය සහ දිගුකාලීන සබඳතා","text":marriage},
        {"title":"10. දරුවන්, නිර්මාණශීලීත්වය සහ බුද්ධි බලය","text":children},
        {"title":"11. විදේශ ගමන් සහ පදිංචි වෙනස්කම්","text":foreign},
        {"title":"12. නිවස, ඉඩම් සහ වාහන","text":property_text},
        {"title":"13. සමාජ ගෞරවය, නම සහ සම්බන්ධතා","text":status},
        {"title":"14. ශාරීරික හා මානසික සුවතාව පිළිබඳ සාම්ප්‍රදායික සටහන","text":wellbeing},
        {"title":"15. මහා දශා සහ අතුරු දශා විග්‍රහය","text":dasha_text},
        {"title":"16. ඉදිරි කාල සීමා විග්‍රහ කරන ආකාරය","text":timing},
        {"title":"17. ශනි බලපෑම සහ ඒරාෂ්ටක සලකා බැලීම","text":saturn_text},
        {"title":"18. රාහු සහ කේතු අක්ෂයේ බලපෑම","text":nodes_text},
        {"title":"19. කුජ බලපෑම සහ කුජ දෝෂ සලකා බැලීම","text":mars_text},
        {"title":"20. ඉදිරි අවස්ථා සහ වර්ධනය විය හැකි අංශ","text":" ".join(opportunities)},
        {"title":"21. අවධානය යොමු කළ යුතු අභියෝග","text":" ".join(challenges)},
        {"title":"22. සාම්ප්‍රදායික පිළියම්, ප්‍රායෝගික ක්‍රියා සහ උදාහරණ","text":" ".join(remedies_common + planet_remedies)},
    ]
    return {"summary":summary,"sections":sections}


# --- Advanced Jyotishya calculations (v1.8) ---
YOGA_NAMES = ["විෂ්කම්භ","ප්‍රීති","ආයුෂ්මාන්","සෞභාග්‍ය","ශෝභන","අතිගණ්ඩ","සුකර්ම","ධෘති","ශූල","ගණ්ඩ","වෘද්ධි","ධෘව","ව්‍යාඝාත","හර්ෂණ","වජ්‍ර","සිද්ධි","ව්‍යතිපාත","වරීයන","පරිඝ","ශිව","සිද්ධ","සාධ්‍ය","ශුභ","ශුක්ල","බ්‍රහ්ම","ඉන්ද්‍ර","වෛධෘති"]
KARANA_MOVABLE = ["බව","බාලව","කෞලව","තෛතිල","ගරජ","වණිජ","විෂ්ටි"]
EXALT_SIGN = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}
DEBIL_SIGN = {k:(v+6)%12 for k,v in EXALT_SIGN.items()}
OWN_SIGNS = {"Sun":{4},"Moon":{3},"Mars":{0,7},"Mercury":{2,5},"Jupiter":{8,11},"Venus":{1,6},"Saturn":{9,10}}


def panchanga_details(planets, jd):
    sun = planets["Sun"]["longitude"]
    moon = planets["Moon"]["longitude"]
    elong = norm(moon - sun)
    tithi_num = int(elong // 12) + 1
    paksha = "ශුක්ල පක්ෂය" if tithi_num <= 15 else "කෘෂ්ණ පක්ෂය"
    paksha_tithi = tithi_num if tithi_num <= 15 else tithi_num - 15
    if paksha_tithi == 15:
        tithi_label = "පුර පසළොස්වක" if tithi_num == 15 else "අමාවක"
    else:
        tithi_label = f"{paksha_tithi} වන තිථිය"
    yoga_index = int(norm(sun + moon) // (360/27))
    half_index = int(elong // 6) + 1
    if half_index == 1:
        karana = "කිංස්තුඝ්න"
    elif 2 <= half_index <= 57:
        karana = KARANA_MOVABLE[(half_index-2) % 7]
    elif half_index == 58:
        karana = "ශකුණි"
    elif half_index == 59:
        karana = "චතුෂ්පාද"
    else:
        karana = "නාග"
    weekday = int((jd + 1.5) % 7)
    weekday_names = ["ඉරිදා","සඳුදා","අඟහරුවාදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා","සෙනසුරාදා"]
    ayan = swe.get_ayanamsa_ut(jd)
    return {
        "vara": weekday_names[weekday],
        "tithi_number": tithi_num,
        "paksha": paksha,
        "tithi": tithi_label,
        "nakshatra": planets["Moon"]["nakshatra"]["name"],
        "pada": planets["Moon"]["nakshatra"]["pada"],
        "yoga": YOGA_NAMES[yoga_index],
        "karana": karana,
        "ayanamsa": round(ayan,6),
        "julian_day": round(jd,6),
    }


def varga_sign(lon, division):
    lon = norm(lon)
    sign = int(lon // 30)
    deg = lon % 30
    if division == 2:  # Hora
        first = deg < 15
        if sign % 2 == 0: return 4 if first else 3
        return 3 if first else 4
    if division == 3:  # Drekkana: 1st/5th/9th
        part = min(2, int(deg // 10))
        return (sign + part*4) % 12
    if division == 7:  # Saptamsa
        part = min(6, int(deg // (30/7)))
        start = sign if sign % 2 == 0 else (sign + 6) % 12
        return (start + part) % 12
    if division == 9:
        return navamsa_info(lon)["index"]
    if division == 10:  # Dasamsa
        part = min(9, int(deg // 3))
        start = sign if sign % 2 == 0 else (sign + 8) % 12
        return (start + part) % 12
    if division == 12:  # Dwadasamsa
        part = min(11, int(deg // 2.5))
        return (sign + part) % 12
    return sign


def divisional_charts(planets, lagna):
    out = {}
    for division, code, title in [(2,"D2","හෝරා"),(3,"D3","ද්‍රෙක්කාණ"),(7,"D7","සප්තාංශ"),(9,"D9","නවාංශ"),(10,"D10","දශාංශ"),(12,"D12","ද්වාදශාංශ")]:
        cells = [{"sign_index":i,"sign":RASHI[i],"planets":[]} for i in range(12)]
        for key,p in planets.items():
            si = varga_sign(p["longitude"], division)
            cells[si]["planets"].append(p["name"])
        lag_lon = lagna.get("longitude", lagna.get("rashi",{}).get("index",0)*30.0)
        li = varga_sign(lag_lon, division)
        cells[li]["planets"].insert(0,"ලග්න")
        out[code] = {"code":code,"title":title,"lagna_sign":RASHI[li],"cells":cells}
    return out


def graha_drishti(planets):
    result=[]
    aspect_offsets = {
        "Sun":[7],"Moon":[7],"Mercury":[7],"Venus":[7],
        "Mars":[4,7,8],"Jupiter":[5,7,9],"Saturn":[3,7,10]
    }
    for key, offsets in aspect_offsets.items():
        p=planets[key]
        src=p["rashi"]["index"]
        targets=[]
        for off in offsets:
            sign=(src + off - 1)%12
            targets.append({"aspect":off,"sign":RASHI[sign],"sign_index":sign})
        result.append({"planet":p["name"],"key":key,"from_sign":p["rashi"]["name"],"targets":targets})
    return result


def dignity_summary(planets):
    rows=[]
    for key in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        p=planets[key]; si=p["rashi"]["index"]
        if EXALT_SIGN.get(key)==si: state="උච්ච"
        elif DEBIL_SIGN.get(key)==si: state="නීච"
        elif si in OWN_SIGNS.get(key,set()): state="ස්වක්ෂේත්‍ර"
        else: state="සාමාන්‍ය"
        house=p.get("house")
        if house in {1,4,7,10}: house_strength="කේන්ද්‍ර"
        elif house in {1,5,9}: house_strength="ත්‍රිකෝණ"
        elif house in {3,6,10,11}: house_strength="උපචය"
        elif house in {6,8,12}: house_strength="දුෂ්ථාන"
        else: house_strength="සාමාන්‍ය"
        rows.append({"planet":p["name"],"state":state,"house":house,"house_class":house_strength,"retrograde":p.get("retrograde",False)})
    return rows


def yoga_dosha_checks(planets, lagna):
    yogas=[]; doshas=[]
    def same(a,b): return planets[a]["rashi"]["index"]==planets[b]["rashi"]["index"]
    def dist(a,b): return ((planets[b]["rashi"]["index"]-planets[a]["rashi"]["index"])%12)+1
    if same("Sun","Mercury"):
        yogas.append({"name":"බුධ-ආදිත්‍ය යෝගය","note":"රවි සහ බුධ එකම රාශියේ."})
    jfrommoon=dist("Moon","Jupiter")
    if jfrommoon in {1,4,7,10}:
        yogas.append({"name":"ගජකේශරී යෝගය","note":f"ගුරු චන්ද්‍රයාගෙන් {jfrommoon} වන ස්ථානයේ."})
    if same("Moon","Mars") or dist("Moon","Mars")==7:
        yogas.append({"name":"චන්ද්‍ර-මංගල යෝගය","note":"චන්ද්‍ර සහ කුජ සම්බන්ධතාවයක් පෙනේ."})
    if same("Jupiter","Mars") or dist("Jupiter","Mars")==7:
        yogas.append({"name":"ගුරු-මංගල සම්බන්ධය","note":"ගුරු සහ කුජ අතර ප්‍රබල සම්බන්ධතාවයක්."})
    mars_h=planets["Mars"].get("house")
    if mars_h in {1,2,4,7,8,12}:
        doshas.append({"name":"කුජ / භෞම දෝෂ පරීක්ෂාව","note":f"කුජ {mars_h} වන භාවයේ. සම්පූර්ණ විවාහ ගැලපීමේදී වෙනම සසඳන්න."})
    # Simple Kala Sarpa screening: all seven classical planets lie within one nodal semicircle
    rahu=planets["Rahu"]["longitude"]; ketu=planets["Ketu"]["longitude"]
    classical=[planets[k]["longitude"] for k in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]]
    def arc_contains(x,start,end):
        if start<=end: return start<=x<=end
        return x>=start or x<=end
    side1=all(arc_contains(x,rahu,ketu) for x in classical)
    side2=all(arc_contains(x,ketu,rahu) for x in classical)
    if side1 or side2:
        doshas.append({"name":"කාල සර්ප යෝග පරීක්ෂාව","note":"ප්‍රධාන ග්‍රහ සියල්ල රාහු–කේතු අක්ෂයේ එක පැත්තක පිහිටන රටාවක් පෙනේ. මෙය පාරම්පරික ක්‍රම අනුව වෙනස් ලෙස විග්‍රහ කරයි."})
    if not yogas: yogas.append({"name":"ප්‍රධාන සරල යෝග","note":"මෙම මූලික පරීක්ෂාවේ ප්‍රධාන සරල යෝගයක් හඳුනාගෙන නොමැත. භාව අධිපති සම්බන්ධතා, දෘෂ්ටි සහ වර්ග බලයද එකට සලකා බලන්න."})
    if not doshas: doshas.append({"name":"ප්‍රධාන දෝෂ පරීක්ෂාව","note":"මෙම මූලික පරීක්ෂාව අනුව ප්‍රධාන දෝෂ තත්ත්වයක් හඳුනාගෙන නොමැත."})
    return {"yogas":yogas,"doshas":doshas}


def antardasha_for_current(dasha):
    cur=dasha.get("current")
    if not cur or not cur.get("lord") or not cur.get("start") or not cur.get("end"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur["start"]); end=datetime.fromisoformat(cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds()
    seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]
        dur=total*(DASHA_YEARS[lord]/120.0)
        e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat()})
        cursor=e
    today=datetime.now()
    current=next((p for p in periods if datetime.fromisoformat(p["start"]) <= today < datetime.fromisoformat(p["end"])),None)
    return {"current":current,"periods":periods}


def current_gochara(natal_moon_sign, natal_lagna_sign):
    now=datetime.utcnow(); jd=jd_from_dt(now)
    trans=planet_positions(jd)
    rows=[]
    for key in ["Jupiter","Saturn","Rahu","Ketu","Mars","Venus","Mercury"]:
        p=trans[key]; si=p["rashi"]["index"]
        from_moon=((si-natal_moon_sign)%12)+1
        from_lagna=((si-natal_lagna_sign)%12)+1
        rows.append({"planet":p["name"],"key":key,"sign":p["rashi"]["name"],"from_moon":from_moon,"from_lagna":from_lagna,"retrograde":p.get("retrograde",False)})
    sat=next(x for x in rows if x["key"]=="Saturn")
    notes=[]
    if sat["from_moon"] in {12,1,2}:
        notes.append("චන්ද්‍ර රාශිය අනුව ඒරාෂ්ටක කාල පරාසයට අයත් ශනි ගෝචරයක් පවතී.")
    if sat["from_moon"]==8:
        notes.append("චන්ද්‍ර රාශියෙන් අටවන ස්ථානයේ ශනි ගෝචරය පවතින බැවින් අෂ්ටම ශනි බලපෑම සලකා බලයි.")
    if sat["from_lagna"]==8:
        notes.append("ලග්නයෙන් අටවන ස්ථානයේ ශනි ගෝචරය පවතී; වගකීම්, ප්‍රමාද සහ නැවත සැලසුම් කිරීම සම්බන්ධ කරුණු වැඩි විය හැක.")
    if not notes:
        notes.append("මෙම ගණනය අනුව ප්‍රධාන ශනි අපල තත්ත්වයක් හඳුනාගෙන නොමැත.")
        notes.append("ශනිගේ රාශි පිහිටීම, භාවය, දෘෂ්ටි, දශා සහ වත්මන් ගෝචරය එකට සලකා මෙම සාරාංශය ලබාදී ඇත.")
    return {"as_of":now.date().isoformat(),"rows":rows,"flags":notes}




def hela_traditional_factors(planets, lagna):
    """Transparent classical house-lord relationships used as a reference layer.
    This intentionally avoids claiming full Shadbala/Ashtakavarga calculations.
    """
    lag_i = lagna["rashi"]["index"]
    house_lords=[]
    lord_positions={}
    for h in range(1,13):
        sign_i=(lag_i+h-1)%12
        lord_key=RASHI_LORD[sign_i]
        lord_house=planets.get(lord_key,{}).get("house")
        lord_sign=planets.get(lord_key,{}).get("rashi",{}).get("name")
        klass=[]
        if h in {1,4,7,10}: klass.append("කේන්ද්‍ර")
        if h in {1,5,9}: klass.append("ත්‍රිකෝණ")
        if h in {3,6,10,11}: klass.append("උපචය")
        if h in {6,8,12}: klass.append("දුස්ථාන")
        house_lords.append({
            "house":h,"sign":RASHI[sign_i],"lord":PLANET_SI.get(lord_key,lord_key),
            "lord_house":lord_house,"lord_sign":lord_sign or "—","class":" / ".join(klass) or "සාමාන්‍ය"
        })
        lord_positions[h]=(lord_key,lord_house)

    # 
    yoga_notes=[]
    kendra={1,4,7,10}; trikona={1,5,9}
    seen=set()
    for kh in kendra:
        for th in trikona:
            kkey,_=lord_positions[kh]; tkey,_=lord_positions[th]
            if kkey==tkey:
                key=("same",kkey)
                if key not in seen:
                    yoga_notes.append(f"{PLANET_SI.get(kkey,kkey)} ග්‍රහයා කේන්ද්‍ර සහ ත්‍රිකෝණ අධිපතිත්වයක් එකට දරන සම්බන්ධතාවයක් පෙන්වයි.")
                    seen.add(key)
            elif planets[kkey]["rashi"]["index"]==planets[tkey]["rashi"]["index"]:
                key=tuple(sorted((kkey,tkey)))
                if key not in seen:
                    yoga_notes.append(f"{PLANET_SI.get(kkey,kkey)} සහ {PLANET_SI.get(tkey,tkey)} කේන්ද්‍ර-ත්‍රිකෝණ අධිපති සම්බන්ධතාවයක් එකම රාශියේ පෙන්වයි.")
                    seen.add(key)
    if not yoga_notes:
        yoga_notes.append("මෙම මූලික පරීක්ෂාවේ පැහැදිලි කේන්ද්‍ර-ත්‍රිකෝණ අධිපති සංයෝගයක් නොපෙනේ; දෘෂ්ටි සහ වර්ග බලය වෙනම බලන්න.")

    dhana=[]
    wealth_houses={2,11}; fortune_houses={5,9}
    for wh in wealth_houses:
        for fh in fortune_houses:
            wkey,_=lord_positions[wh]; fkey,_=lord_positions[fh]
            if wkey==fkey or planets[wkey]["rashi"]["index"]==planets[fkey]["rashi"]["index"]:
                dhana.append(f"{wh} සහ {fh} භාව අධිපති අතර සම්බන්ධතාවයක් පෙන්වයි ({PLANET_SI.get(wkey,wkey)} / {PLANET_SI.get(fkey,fkey)}).")
    if not dhana:
        dhana.append("2/11 සහ 5/9 භාව අධිපති අතර සරල සංයෝගයක් මෙම පරීක්ෂාවේ නොපෙනේ.")

    lagna_lord_key=RASHI_LORD[lag_i]
    moon_nak=planets["Moon"]["nakshatra"]
    return {
        "lagna_lord": {"planet":PLANET_SI.get(lagna_lord_key,lagna_lord_key),"house":planets[lagna_lord_key]["house"],"sign":planets[lagna_lord_key]["rashi"]["name"]},
        "nakshatra_lord": {"nakshatra":moon_nak["name"],"planet":DASHA_SI.get(moon_nak["lord"],moon_nak["lord"]),"pada":moon_nak["pada"]},
        "house_lords":house_lords,
        "raja_yoga_reference":yoga_notes,
        "dhana_yoga_reference":dhana,
        "note":"මෙය භාව අධිපති සම්බන්ධතා මත පදනම් වූ මූලික හෙළ/වේදික ජ්‍යෝතිෂ්‍ය පරීක්ෂාවකි. අෂ්ටකවර්ගය වෙනම සම්පූර්ණ වගුවකින් පෙන්වයි; ග්‍රහ බල දර්ශකය පූර්ණ ෂඩ්බලයක් නොවේ."
    }



def pratyantardasha_for_current(dasha):
    ad = antardasha_for_current(dasha)
    cur = ad.get("current")
    if not cur or not cur.get("lord") or not cur.get("start") or not cur.get("end"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur["start"]); end=datetime.fromisoformat(cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds(); seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]
        dur=total*(DASHA_YEARS[lord]/120.0)
        e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat()})
        cursor=e
    today=datetime.now()
    current=next((x for x in periods if datetime.fromisoformat(x["start"]) <= today < datetime.fromisoformat(x["end"])),None)
    return {"current":current,"periods":periods}


def planetary_strength_reference(planets):
    rows=[]
    for key in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        p=planets[key]; si=p["rashi"]["index"]; h=p.get("house") or 0
        score=50; reasons=[]
        if EXALT_SIGN.get(key)==si: score+=30; reasons.append("උච්ච")
        elif DEBIL_SIGN.get(key)==si: score-=25; reasons.append("නීච")
        elif si in OWN_SIGNS.get(key,set()): score+=20; reasons.append("ස්වක්ෂේත්‍ර")
        if h in {1,4,7,10}: score+=12; reasons.append("කේන්ද්‍ර")
        if h in {1,5,9}: score+=12; reasons.append("ත්‍රිකෝණ")
        if h in {3,6,10,11}: score+=6; reasons.append("උපචය")
        if h in {6,8,12}: score-=7; reasons.append("දුෂ්ථාන")
        if p.get("retrograde") and key in {"Mars","Mercury","Jupiter","Venus","Saturn"}: score+=5; reasons.append("වක්‍ර")
        score=max(0,min(100,score))
        level="ප්‍රබල" if score>=75 else ("මධ්‍යම" if score>=45 else "දුර්වල")
        rows.append({"planet":p["name"],"score":score,"level":level,"reasons":reasons or ["සාමාන්‍ය පිහිටීම"]})
    return {"rows":rows,"note":"මෙය උච්ච/නීච, ස්වක්ෂේත්‍ර, භාව වර්ග සහ වක්‍රත්වය මත ගත් සාර ග්‍රහ බල දර්ශකයකි. පූර්ණ ෂඩ්බල ගණනයක් නොවේ."}


def malefic_analysis(planets, lagna, dasha, gochara):
    out=[]
    current=dasha.get("current",{}) if dasha else {}
    ad=antardasha_for_current(dasha).get("current") if dasha else None
    for key,title in [("Saturn","ශනි"),("Rahu","රාහු"),("Ketu","කේතු"),("Mars","කුජ")]:
        p=planets[key]; h=p.get("house") or 0; sign=p["rashi"]["name"]
        points=[]; level="සාමාන්‍ය"
        if key=="Saturn":
            if h in {6,8,12}: points.append(f"ජන්ම කේන්දරයේ ශනි {h} වන භාවයේ සිටීම නිසා වගකීම්, ප්‍රමාද සහ ඉවසීම සම්බන්ධ පාඩම් වැඩි විය හැක.")
            elif h in {3,6,10,11}: points.append(f"ශනි {h} වන උපචය භාවයේ සිටීම නිසා මහන්සියෙන් හා කාලයත් සමඟ ප්‍රගතිය ගොඩනැඟීමේ හැකියාව පෙන්වයි.")
        if key in {"Rahu","Ketu"}:
            if h in {1,4,7,8,10,12}: points.append(f"{title} {h} වන භාවයේ පිහිටීම නිසා එම භාවයට අදාළ කරුණු සම්බන්ධයෙන් අසාමාන්‍ය වෙනස්කම් හෝ දැඩි අවධානයක් ඇති විය හැක.")
        if key=="Mars":
            if h in {1,2,4,7,8,12}: points.append(f"කුජ {h} වන භාවයේ සිටීම නිසා භෞම/කුජ දෝෂය විවාහ ගැලපීමේදී වෙනම සලකා බැලීම සුදුසුය.")
            else: points.append(f"කුජ {h} වන භාවයේ සිටීම ශක්තිය, ක්‍රියාකාරීත්වය සහ තීරණ ගැනීමේ වේගය සමඟ සම්බන්ධ කර විග්‍රහ කරයි.")
        if current and current.get("lord")==key: points.append(f"දැනට {title} මහා දශාව ක්‍රියාත්මක බැවින් ජන්ම {title} පිහිටීමේ ප්‍රතිඵල වැඩි ප්‍රමුඛතාවයකින් පෙනිය හැක.")
        if ad and ad.get("lord")==key: points.append(f"දැනට {title} අතුරු දශාව ක්‍රියාත්මක වන බැවින් කෙටි කාලීන තීරණ සහ සිදුවීම් වලදී මෙම ග්‍රහයාගේ බලය වැඩි වේ.")
        g=next((x for x in gochara.get("rows",[]) if x.get("key")==key),None)
        if g: points.append(f"වත්මන් ගෝචරයේ {title} චන්ද්‍රයෙන් {g['from_moon']} වන ස්ථානයේත් ලග්නයෙන් {g['from_lagna']} වන ස්ථානයේත් ගමන් කරයි.")
        if len(points)>=3: level="වැඩි අවධානය"
        elif len(points)>=2: level="මධ්‍යම අවධානය"
        if not points: points.append("මෙම ග්‍රහයා සම්බන්ධයෙන් ප්‍රධාන විශේෂ අවදානම් ලකුණක් මෙම මූලික පරීක්ෂාවෙන් හඳුනාගෙන නොමැත.")
        out.append({"planet":title,"level":level,"points":points})
    return out



# පරාශර අෂ්ටකවර්ගයේ මූලික බින්න අෂ්ටකවර්ග සහ සර්වාෂ්ටකවර්ග වගු.
# රාහු/කේතු අෂ්ටකවර්ග contributor ලෙස භාවිතා නොකෙරේ.
ASHTA_CONTRIB = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Lagna"]
ASHTA_TARGETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
ASHTA_BENEFIC = {
    "Sun": {
        "Sun":[1,2,4,7,8,9,10,11], "Moon":[3,6,10,11], "Mars":[1,2,4,7,8,9,10,11],
        "Mercury":[3,5,6,9,10,11,12], "Jupiter":[5,6,9,11], "Venus":[6,7,12],
        "Saturn":[1,2,4,7,8,9,10,11], "Lagna":[3,4,6,10,11,12]},
    "Moon": {
        "Sun":[3,6,7,8,10,11], "Moon":[1,3,6,7,10,11], "Mars":[2,3,5,6,9,10,11],
        "Mercury":[1,3,4,5,7,8,10,11], "Jupiter":[1,4,7,8,10,11,12], "Venus":[3,4,5,7,9,10,11],
        "Saturn":[3,5,6,11], "Lagna":[3,6,10,11]},
    "Mars": {
        "Sun":[3,5,6,10,11], "Moon":[3,6,11], "Mars":[1,2,4,7,8,10,11], "Mercury":[3,5,6,11],
        "Jupiter":[6,10,11,12], "Venus":[6,8,11,12], "Saturn":[1,4,7,8,9,10,11], "Lagna":[1,3,6,10,11]},
    "Mercury": {
        "Sun":[5,6,9,11,12], "Moon":[2,4,6,8,10,11], "Mars":[1,2,4,7,8,9,10,11],
        "Mercury":[1,3,5,6,9,10,11,12], "Jupiter":[6,8,11,12], "Venus":[1,2,3,4,5,8,9,11],
        "Saturn":[1,2,4,7,8,9,10,11], "Lagna":[1,2,4,6,8,10,11]},
    "Jupiter": {
        "Sun":[1,2,3,4,7,8,9,10,11], "Moon":[2,5,7,9,11], "Mars":[1,2,4,7,8,10,11],
        "Mercury":[1,2,4,5,6,9,10,11], "Jupiter":[1,2,3,4,7,8,10,11], "Venus":[2,5,6,9,10,11],
        "Saturn":[3,5,6,12], "Lagna":[1,2,4,5,6,7,9,10,11]},
    "Venus": {
        "Sun":[8,11,12], "Moon":[1,2,3,4,5,8,9,11,12], "Mars":[3,5,6,9,11,12],
        "Mercury":[3,5,6,9,11], "Jupiter":[5,8,9,10,11], "Venus":[1,2,3,4,5,8,9,10,11],
        "Saturn":[3,4,5,8,9,10,11], "Lagna":[1,2,3,4,5,8,9,11]},
    "Saturn": {
        "Sun":[1,2,4,7,8,10,11], "Moon":[3,6,11], "Mars":[3,5,6,10,11,12],
        "Mercury":[6,8,9,10,11,12], "Jupiter":[5,6,11,12], "Venus":[6,11,12],
        "Saturn":[3,5,6,11], "Lagna":[1,3,4,6,10,11]},
}
ASHTA_EXPECTED = {"Sun":48,"Moon":49,"Mars":39,"Mercury":54,"Jupiter":56,"Venus":52,"Saturn":39}

def ashtakavarga(planets, lagna):
    positions = {k: planets[k]["rashi"]["index"] for k in ASHTA_TARGETS}
    lag_i = lagna["rashi"]["index"]
    bav = {}
    checks = {}
    sav = [0]*12
    for target in ASHTA_TARGETS:
        vals = [0]*12
        for contributor in ASHTA_CONTRIB:
            csign = lag_i if contributor == "Lagna" else positions[contributor]
            for house in ASHTA_BENEFIC[target][contributor]:
                vals[(csign + house - 1) % 12] += 1
        bav[target] = vals
        total = sum(vals)
        checks[target] = {"total":total,"expected":ASHTA_EXPECTED[target],"ok":total==ASHTA_EXPECTED[target]}
        for i,v in enumerate(vals): sav[i] += v
    signs=[]
    for i,v in enumerate(sav):
        level = "ප්‍රබල" if v >= 30 else ("මධ්‍යම" if v >= 25 else "අඩු")
        signs.append({"sign_index":i,"sign":RASHI[i],"points":v,"level":level})
    return {
        "bav":bav,
        "sav":sav,
        "signs":signs,
        "total":sum(sav),
        "checks":checks,
        "note":"මෙය පරාශර සම්ප්‍රදායේ මූලික බින්න අෂ්ටකවර්ග සහ සර්වාෂ්ටකවර්ග ගණනයයි. ශෝධන පියවර වෙනම පරීක්ෂණයකි."
    }

def advanced_jyotishya(planets, lagna, dasha, jd):
    go=current_gochara(planets["Moon"]["rashi"]["index"], lagna["rashi"]["index"])
    return {
        "panchanga":panchanga_details(planets,jd),
        "vargas":divisional_charts(planets,lagna),
        "drishti":graha_drishti(planets),
        "dignity":dignity_summary(planets),
        "planet_strength":planetary_strength_reference(planets),
        "ashtakavarga":ashtakavarga(planets,lagna),
        "yoga_dosha":yoga_dosha_checks(planets,lagna),
        "antardasha":antardasha_for_current(dasha),
        "pratyantardasha":pratyantardasha_for_current(dasha),
        "gochara":go,
        "malefic_analysis":malefic_analysis(planets,lagna,dasha,go),
        "hela_factors":hela_traditional_factors(planets,lagna),
        "methods":["ලහිරි අයනංශය","බින්න අෂ්ටකවර්ග / සර්වාෂ්ටකවර්ග","නිරයන ග්‍රහ ස්ඵුට","පංචාංග ගණිතය","විම්ශෝත්තරී මහා දශා / අතුරු දශා / ප්‍රත්‍යන්තර දශා","සාම්ප්‍රදායික ග්‍රහ දෘෂ්ටි","හෝරා / ද්‍රෙක්කාණ / සප්තාංශ / නවාංශ / දශාංශ / ද්වාදශාංශ වර්ග","ග්‍රහ බල සාර දර්ශකය","යෝග සහ දෝෂ පරීක්ෂාව","චන්ද්‍ර සහ ලග්නයෙන් වත්මන් ගෝචරය","ශනි / රාහු / කේතු / කුජ ගැඹුරු සාර විග්‍රහය","භාව අධිපති / කේන්ද්‍ර / ත්‍රිකෝණ / උපචය / දුස්ථාන පරීක්ෂාව","රාජ යෝග සහ ධන යෝග මූලික අධිපති සම්බන්ධතා"]
    }



# --- පුද්ගලික කේන්දර විග්‍රහ එන්ජිම v2.9 ---
# සෑම කොටසක්ම අදාළ භාවය, භාව අධිපති, ග්‍රහ පිහිටීම්, දෘෂ්ටි,
# ග්‍රහ තත්ත්වය සහ වත්මන් දශාව එකට සලකා සකස් කරයි.
NAK_TRAITS = [
    "වේගවත් ආරම්භ, ස්වාධීනත්වය සහ ක්‍රියාශීලීත්වය", "ඉවසීම, වගකීම සහ භෞතික ස්ථාවරත්වය",
    "කැපවීම, පිරිසිදු කිරීම සහ තීරණාත්මක බව", "සැලසුම්කරණය, සෞන්දර්යය සහ ස්ථාවර වර්ධනය",
    "සෙවීම, ඉගෙනීම සහ නව මාර්ග සොයාගැනීම", "ගැඹුරු සිතීම, වෙනස්කම් සහ අභ්‍යන්තර පීඩනය",
    "නැවත ගොඩනැගීම, පවුල් ආරක්ෂාව සහ උපදේශන ගුණය", "පෝෂණය, වගකීම සහ ආරක්ෂාව",
    "සංවේදීත්වය, ගැඹුරු අවබෝධය සහ රහස්කාරී ස්වභාවය", "ගෞරවය, නායකත්වය සහ පවුල් සම්ප්‍රදාය",
    "නිර්මාණශීලීත්වය, සතුට සහ සමාජ ආකර්ෂණය", "ගිවිසුම්, වගකීම් සහ ක්‍රමානුකූල වර්ධනය",
    "කාර්යදක්ෂතාව, අත්කම් සහ ප්‍රායෝගික බුද්ධිය", "නිර්මාණය, පෙනුම සහ තරඟකාරීත්වය",
    "ස්වාධීනත්වය, වෙළඳාම සහ ගමන්", "අරමුණු, හවුල්කාරීත්වය සහ තීරණාත්මක අවස්ථා",
    "විශ්වාසය, මිත්‍රත්වය සහ දිගුකාලීන කැපවීම", "තීක්ෂණභාවය, රහස් විමර්ශනය සහ පාලන ගුණය",
    "මූල හේතු සෙවීම, වෙන්වීම සහ නැවත ආරම්භය", "ජයග්‍රහණය, සම්බන්ධතා සහ අගය හඳුනාගැනීම",
    "දිගුකාලීන ජයග්‍රහණ, නීතිය සහ වගකීම", "ඉගෙනීම, කීර්තිය සහ ශ්‍රවණශීලීත්වය",
    "සම්පත්, සංගීතය සහ සංවිධානය", "ස්වාධීන අදහස්, පර්යේෂණය සහ අසාමාන්‍ය මාර්ග",
    "ආධ්‍යාත්මිකත්වය, ගැඹුරු අදහස් සහ වෙනස්කම්", "ස්ථාවරත්වය, උපදේශනය සහ පරිණත බව",
    "සංවේදීත්වය, අවසන් කිරීම සහ කරුණාව"
]

HOUSE_MEANINGS = {
    1:"ශරීරය, පුද්ගලත්වය, ස්වභාවය සහ ජීවිත දිශාව", 2:"පවුල, වචනය, මුදල් සහ ඉතිරි කිරීම",
    3:"ධෛර්යය, සහෝදරයන්, සන්නිවේදනය සහ තමන්ගේ උත්සාහ", 4:"නිවස, මව්පාර්ශවය, අධ්‍යාපන පදනම, දේපළ සහ සැනසීම",
    5:"බුද්ධිය, අධ්‍යාපනය, නිර්මාණශීලීත්වය සහ දරුවන්", 6:"සේවය, තරඟ, ණය, බාධා සහ දෛනික වැඩ",
    7:"විවාහය, හවුල්කාරීත්වය සහ මහජන සම්බන්ධතා", 8:"හදිසි වෙනස්කම්, රහස්, පරිවර්තනය සහ අභියෝග",
    9:"භාග්‍යය, උසස් අධ්‍යාපනය, දුර ගමන් සහ ධර්මය", 10:"රැකියාව, තනතුර, කීර්තිය සහ වගකීම",
    11:"ලාභ, ජාලය, මිතුරන් සහ අරමුණු ඉටු කිරීම", 12:"විදේශ, වියදම්, නිශ්ශබ්දතාව සහ වෙන්වීම්"
}

PLANET_KEY_SI = {"Sun":"රවි","Moon":"චන්ද්‍ර","Mars":"කුජ","Mercury":"බුධ","Jupiter":"ගුරු","Venus":"ශුක්‍ර","Saturn":"ශනි","Rahu":"රාහු","Ketu":"කේතු"}


def _aspect_map(planets, lagna_idx):
    offsets={"Sun":[7],"Moon":[7],"Mercury":[7],"Venus":[7],"Mars":[4,7,8],"Jupiter":[5,7,9],"Saturn":[3,7,10]}
    out={h:[] for h in range(1,13)}
    for key, offs in offsets.items():
        src=planets[key]["rashi"]["index"]
        for off in offs:
            target_sign=(src+off-1)%12
            house=((target_sign-lagna_idx)%12)+1
            out[house].append(PLANET_KEY_SI[key])
    return out


def _dignity_map(planets):
    return {row["planet"]:row for row in dignity_summary(planets)}


def _planet_state_text(pname, dmap):
    row=dmap.get(pname,{})
    state=row.get("state","සාමාන්‍ය")
    cls=row.get("house_class","සාමාන්‍ය")
    extras=[]
    if state!="සාමාන්‍ය": extras.append(state)
    if cls!="සාමාන්‍ය": extras.append(cls)
    if row.get("retrograde"): extras.append("වක්‍ර")
    return " / ".join(extras) if extras else "සාමාන්‍ය බලය"


def _house_evidence(h, lagna_idx, planets, aspects, dmap):
    sign_i=(lagna_idx+h-1)%12
    lord_key=RASHI_LORD[sign_i]
    lord=planets[lord_key]
    occupants=[p["name"] for p in planets.values() if p.get("house")==h]
    asp=aspects.get(h,[])
    parts=[
        f"{h} වන භාවය {RASHI[sign_i]} රාශියට අයත්ය",
        f"එහි අධිපති {PLANET_KEY_SI[lord_key]} {lord.get('house')} වන භාවයේ {lord['rashi']['name']} රාශියේ සිටී",
        f"{PLANET_KEY_SI[lord_key]}ගේ තත්ත්වය {_planet_state_text(PLANET_KEY_SI[lord_key], dmap)} ලෙස පෙනේ"
    ]
    if occupants: parts.append("එම භාවයේ " + ", ".join(occupants) + " පිහිටා ඇත")
    else: parts.append("එම භාවයේ ප්‍රධාන ග්‍රහයක් නොමැත")
    if asp: parts.append("එම භාවයට " + ", ".join(asp) + " දෘෂ්ටි වැටේ")
    return ". ".join(parts) + "."


def _conjunctions(planets):
    by_sign={i:[] for i in range(12)}
    for k,p in planets.items(): by_sign[p['rashi']['index']].append(p['name'])
    return [vals for vals in by_sign.values() if len(vals)>=2]


def _section_judgement(houses, lagna_idx, planets, aspects, dmap, current_lord=None):
    positives=[]; cautions=[]
    for h in houses:
        sign_i=(lagna_idx+h-1)%12
        lord_key=RASHI_LORD[sign_i]
        lord_name=PLANET_KEY_SI[lord_key]
        lord=planets[lord_key]
        state=dmap.get(lord_name,{}).get('state','සාමාන්‍ය')
        if state in {'උච්ච','ස්වක්ෂේත්‍ර'} or lord.get('house') in {1,4,5,7,9,10,11}:
            positives.append(f"{h} වන භාවයේ අධිපති {lord_name} සාපේක්ෂව සහායක තත්ත්වයක සිටී")
        if state=='නීච' or lord.get('house') in {6,8,12}:
            cautions.append(f"{h} වන භාවයේ අධිපති {lord_name} සඳහා වැඩි සැලකිල්ලක් අවශ්‍ය පිහිටීමක් පෙනේ")
        occ=[p for p in planets.values() if p.get('house')==h]
        for p in occ:
            if p['key'] in {'Jupiter','Venus','Mercury'}:
                positives.append(f"{h} වන භාවයේ {p['name']} සිටීම එම අංශයට සහාය දිය හැක")
            if p['key'] in {'Saturn','Mars','Rahu','Ketu'}:
                cautions.append(f"{h} වන භාවයේ {p['name']} සිටීම එම අංශයේ ප්‍රමාද, තදබල වෙනස්කම් හෝ වැඩි වගකීම් පෙන්විය හැක")
        if 'ගුරු' in aspects.get(h,[]): positives.append(f"{h} වන භාවයට ගුරු දෘෂ්ටියක් ඇත")
        if 'ශනි' in aspects.get(h,[]): cautions.append(f"{h} වන භාවයට ශනි දෘෂ්ටියක් ඇත")
        if 'කුජ' in aspects.get(h,[]): cautions.append(f"{h} වන භාවයට කුජ දෘෂ්ටියක් ඇත")
    if current_lord:
        cp=planets.get(current_lord)
        if cp and cp.get('house') in houses:
            positives.append(f"වත්මන් දශා අධිපති {cp['name']} මෙම විෂයට අදාළ භාවයක සිටින නිසා මේ අංශය දැනට සක්‍රීය වේ")
    # de-duplicate, preserve order
    positives=list(dict.fromkeys(positives))[:4]
    cautions=list(dict.fromkeys(cautions))[:4]
    return positives,cautions


def _compose_section(title, houses, lagna_idx, planets, aspects, dmap, current_lord, practical):
    evidence=" ".join(_house_evidence(h,lagna_idx,planets,aspects,dmap) for h in houses)
    pos,cau=_section_judgement(houses,lagna_idx,planets,aspects,dmap,current_lord)
    verdict=[]
    if pos: verdict.append("යහපත් පැත්ත: " + "; ".join(pos) + ".")
    if cau: verdict.append("අවධානය: " + "; ".join(cau) + ".")
    if not verdict: verdict.append("මෙම අංශයට මිශ්‍ර බලපෑමක් පෙනෙන බැවින් දශා සහ ගෝචර සමඟ කාලය තීරණය කිරීම වඩා සුදුසුය.")
    return {"title":title,"text": evidence + " " + " ".join(verdict) + " " + practical}


def expanded_reading(lagna, planets, dasha, reference=False):
    lag_i=lagna['rashi']['index']
    moon=planets['Moon']
    nak=moon['nakshatra']
    aspects=_aspect_map(planets,lag_i)
    dmap=_dignity_map(planets)
    current=dasha.get('current') or {}
    current_lord=current.get('lord')
    conjunctions=_conjunctions(planets)

    lag_lord_key=RASHI_LORD[lag_i]
    lag_lord=planets[lag_lord_key]
    summary=[
        f"ලග්නය {lagna['rashi']['name']} ({lagna['rashi'].get('degree',0):.2f}°) වන අතර ලග්නාධිපති {lag_lord['name']} {lag_lord.get('house')} වන භාවයේ {lag_lord['rashi']['name']} රාශියේ සිටී.",
        f"චන්ද්‍රයා {moon['rashi']['name']} රාශියේ {nak['name']} නැකතේ {nak.get('pada')} වන පාදයේ සිටී. මෙම නැකතට සම්බන්ධ මූලික රටාව: {NAK_TRAITS[nak['index']] }.",
        f"චන්ද්‍රයා {moon.get('house')} වන භාවයේ සිටීම නිසා {HOUSE_MEANINGS.get(moon.get('house'),'එම භාවයේ කරුණු')} මනසට සහ තීරණවලට වැඩි බලපෑමක් දක්වයි.",
    ]
    if current_lord and current_lord in planets:
        cp=planets[current_lord]
        summary.append(f"වත්මන් මහා දශාව {current.get('name')} වේ. එහි අධිපති {cp['name']} {cp.get('house')} වන භාවයේ {cp['rashi']['name']} රාශියේ සිටින බැවින් {HOUSE_MEANINGS.get(cp.get('house'),'එම භාවයේ කරුණු')} දැනට වැඩිපුර සක්‍රීය විය හැක.")
    if conjunctions:
        summary.append("ප්‍රධාන යුති: " + "; ".join(" + ".join(x) for x in conjunctions[:3]) + ".")

    sections=[]
    sections.append(_compose_section("1. පුද්ගලත්වය, ශරීර බලය සහ ජීවිත දිශාව",[1],lag_i,planets,aspects,dmap,current_lord,
        f"උදාහරණයක් ලෙස, ලග්නාධිපති {lag_lord['name']} {lag_lord.get('house')} වන භාවයේ සිටීම නිසා {HOUSE_MEANINGS.get(lag_lord.get('house'),'එම භාවයේ කරුණු')} ඔබේ ජීවිත තීරණවල නිතර ඉස්මතු විය හැක."))
    sections.append(_compose_section("2. මනස, හැඟීම් සහ තීරණ ගැනීම",[1,4],lag_i,planets,aspects,dmap,current_lord,
        f"චන්ද්‍රයාගේ නැකත් රටාව {NAK_TRAITS[nak['index']]} බැවින්, පීඩනයකදී ඉක්මන් තීරණයකට වඩා සිතුවිලි ලියා පසුව තීරණය කිරීම ප්‍රයෝජනවත් වේ."))
    sections.append(_compose_section("3. පවුල, වචනය සහ ඉතිරි කිරීම",[2,4],lag_i,planets,aspects,dmap,current_lord,
        "උදාහරණයක් ලෙස, පවුල් වගකීම් සහ මුදල් තීරණ එකට ගැටෙන කාලයක මාසික වියදම් සටහනක් තබා ප්‍රමුඛතා වෙන් කිරීම හොඳය."))
    sections.append(_compose_section("4. ධෛර්යය, සන්නිවේදනය සහ තමන්ගේ උත්සාහ",[3],lag_i,planets,aspects,dmap,current_lord,
        "උදාහරණයක් ලෙස, අලුත් කුසලතාවක් හෝ අමතර වැඩක් ආරම්භ කළොත් කෙටි කාලීන උද්යෝගයට වඩා නිතර පුහුණුව ප්‍රතිඵලදායක වේ."))
    sections.append(_compose_section("5. අධ්‍යාපනය, බුද්ධිය සහ කුසලතා",[4,5,9],lag_i,planets,aspects,dmap,current_lord,
        f"බුධගේ පිහිටීම {planets['Mercury'].get('house')} වන භාවයේ සහ {_planet_state_text('බුධ',dmap)} තත්ත්වයේ බැවින් ඉගෙනීමේ ක්‍රමය, ලේඛන සහ තාක්ෂණික දැනුම ඒ අනුව වෙනස් වේ."))
    sections.append(_compose_section("6. රැකියාව, තනතුර සහ වෘත්තීය දිශාව",[6,10,11],lag_i,planets,aspects,dmap,current_lord,
        "උදාහරණයක් ලෙස, 10 වන භාවයට ශනි සම්බන්ධතාවයක් තිබේ නම් ප්‍රගතිය මන්දගාමී වුවත් දිගුකාලීනව වගකීම සහ තනතුර ගොඩනැගීම වැදගත් වේ; ගුරු/බුධ බලය තිබේ නම් දැනුම, පරිපාලනය හෝ තාක්ෂණය හරහා ඉදිරියට යා හැක."))
    sections.append(_compose_section("7. ව්‍යාපාර සහ හවුල්කාරීත්වය",[3,7,10,11],lag_i,planets,aspects,dmap,current_lord,
        "හවුල්කාරීත්වයක් ආරම්භ කරන විට වාචික එකඟතාවකට වඩා වගකීම්, ලාභ බෙදීම සහ පිටවීමේ කොන්දේසි ලිඛිතව තබාගැනීම හොඳය."))
    sections.append(_compose_section("8. මුදල්, ආදායම් සහ ලාභ",[2,5,9,11],lag_i,planets,aspects,dmap,current_lord,
        f"ගුරු {_planet_state_text('ගුරු',dmap)} තත්ත්වයේ {planets['Jupiter'].get('house')} වන භාවයේ සිටින නිසා දිගුකාලීන වර්ධනය ගැන එය ප්‍රධාන ඉඟියකි. කෙටි ලාභයකට වඩා ඉතිරි කිරීම සහ ස්ථාවර ආදායම් මාර්ග ප්‍රමුඛ කරගන්න."))
    sections.append(_compose_section("9. විවාහය සහ දිගුකාලීන සබඳතා",[2,7,8,11],lag_i,planets,aspects,dmap,current_lord,
        f"ශුක්‍ර {planets['Venus'].get('house')} වන භාවයේ {_planet_state_text('ශුක්‍ර',dmap)} තත්ත්වයේ සිටී. කුජ {planets['Mars'].get('house')} වන භාවයේ බැවින් විවාහ ගැලපීමේදී දෙපාර්ශවයේ කුජ බලය, 7 වන අධිපති සහ ශුක්‍රය වෙනම සසඳන්න."))
    sections.append(_compose_section("10. දරුවන් සහ නිර්මාණශීලීත්වය",[5,9],lag_i,planets,aspects,dmap,current_lord,
        "මෙය දරුවන් ගැන නිශ්චිත සෞඛ්‍ය අනාවැකියක් නොවෙයි; දරු ලැබීම සම්බන්ධ වෛද්‍ය කරුණු සඳහා වෛද්‍ය උපදෙස් අවශ්‍යය."))
    sections.append(_compose_section("11. විදේශ ගමන්, දුර ගමන් සහ පදිංචි වෙනස්කම්",[9,12],lag_i,planets,aspects,dmap,current_lord,
        f"රාහු {planets['Rahu'].get('house')} වන භාවයේ සිටින නිසා විදේශ, අසාමාන්‍ය මාර්ග සහ නව පරිසර ගැන එම භාවය හරහා වැඩි උත්තේජනයක් ලැබිය හැක. වීසා/ගිවිසුම් සම්බන්ධ ලේඛන දෙවරක් පරීක්ෂා කරන්න."))
    sections.append(_compose_section("12. නිවස, ඉඩම් සහ වාහන",[4,8,11],lag_i,planets,aspects,dmap,current_lord,
        "දේපළ හෝ වාහන තීරණයකදී කේන්දරයට අමතරව නීතිමය ලේඛන, ණය හැකියාව සහ තාක්ෂණික පරීක්ෂාව අනිවාර්යය."))
    sections.append(_compose_section("13. භාග්‍යය, ගෞරවය සහ සමාජ ජාලය",[9,10,11],lag_i,planets,aspects,dmap,current_lord,
        "ගුරු, 9 වන අධිපති සහ 11 වන අධිපති අතර සහායක සම්බන්ධතා තිබේ නම් ගුරුවරුන්, උසස් අධ්‍යාපනය සහ වෘත්තීය ජාලය හරහා අවස්ථා වැඩි විය හැක."))
    sections.append(_compose_section("14. අභියෝග, තරඟ සහ නැවත ගොඩනැගීම",[6,8,12],lag_i,planets,aspects,dmap,current_lord,
        "මෙම භාවයන් තදබල නම් අභියෝගය මගහැරීමට වඩා සැලසුම්, ණය පාලනය, සෞඛ්‍ය පුරුදු සහ නීතිමය පැහැදිලිභාවය ගොඩනැගීම ප්‍රායෝගික පිළියමකි."))

    # Dasha-specific section
    if current_lord and current_lord in planets:
        cp=planets[current_lord]
        dasha_text=(f"දැනට {current.get('name')} මහා දශාව ක්‍රියාත්මක වේ. දශා අධිපති {cp['name']} {cp.get('house')} වන භාවයේ, {cp['rashi']['name']} රාශියේ, {_planet_state_text(cp['name'],dmap)} තත්ත්වයේ සිටී. "
                    f"ඒ නිසා {HOUSE_MEANINGS.get(cp.get('house'),'එම භාවයේ කරුණු')} දැනට ප්‍රධාන තේමාවක් විය හැක. ")
        if current.get('end'): dasha_text += f"මෙම මහා දශාව {current.get('end')} දක්වා පවතී. "
        if cp.get('house') in {6,8,12}: dasha_text += "මෙය බාධා, වියදම් හෝ නැවත සැලසුම් කිරීම වැඩි කළ හැකි බැවින් ඉක්මන් තීරණවලට වඩා පාලනය සහ සූදානම වැදගත්ය."
        elif cp.get('house') in {1,5,9,10,11}: dasha_text += "මෙය අධ්‍යාපනය, වෘත්තිය, ගෞරවය හෝ අරමුණු ඉටු කිරීම සඳහා වැඩි ක්‍රියාකාරීත්වයක් ලබාදිය හැකි කාලයක් ලෙස සලකන්න පුළුවන්."
        else: dasha_text += "ප්‍රතිඵල තීරණය කිරීමට අතුරු දශාව සහ ගෝචරයද එකට බලන්න."
    else:
        dasha_text="වත්මන් දශා අධිපති හඳුනාගත නොහැකි බැවින් කාල විග්‍රහය සම්පූර්ණ කිරීමට දශා දත්ත අවශ්‍යය."
    sections.append({"title":"15. වත්මන් මහා දශාව සහ එහි ප්‍රධාන තේමාව","text":dasha_text})

    # Specific Saturn / nodes / Mars
    sat=planets['Saturn']; rahu=planets['Rahu']; ketu=planets['Ketu']; mars=planets['Mars']
    sections.append({"title":"16. ශනි බලපෑම", "text":f"ශනි {sat.get('house')} වන භාවයේ {sat['rashi']['name']} රාශියේ {_planet_state_text('ශනි',dmap)} තත්ත්වයේ සිටී. එම භාවය {HOUSE_MEANINGS.get(sat.get('house'))} සම්බන්ධ බැවින් එහි ප්‍රතිඵල සාමාන්‍යයෙන් කාලය, වගකීම, පරීක්ෂණ සහ පසුව ලැබෙන ස්ථාවරත්වය සමඟ පෙනෙන්න පුළුවන්. උදාහරණයක් ලෙස, එම අංශයේ ප්‍රගතිය ප්‍රමාද වුණත් ක්‍රමවත් වැඩ, ලේඛන සහ දිගුකාලීන සැලසුම වැඩි ප්‍රතිඵල දිය හැක."})
    sections.append({"title":"17. රාහු–කේතු අක්ෂය", "text":f"රාහු {rahu.get('house')} වන භාවයේ සහ කේතු {ketu.get('house')} වන භාවයේ සිටී. එබැවින් {rahu.get('house')}/{ketu.get('house')} භාව අක්ෂය ජීවිතයේ විශේෂ අවධානයක් ගන්නා අංශයකි. රාහු පිහිටි භාවයේ අලුත්, විදේශීය හෝ සාමාන්‍ය නොවන මාර්ග වෙත ආකර්ෂණය වැඩි විය හැකි අතර කේතු පිහිටි භාවයේ අභ්‍යන්තර වෙන්වීම හෝ සරල කිරීමේ අවශ්‍යතාව පෙනෙන්න පුළුවන්. උදාහරණයක් ලෙස, රාහු සම්බන්ධ අංශයේ ලේඛන සහ පොරොන්දු දෙවරක් පරීක්ෂා කිරීම ප්‍රායෝගික ආරක්ෂාවකි."})
    sections.append({"title":"18. කුජ බලය සහ ක්‍රියාශීලීත්වය", "text":f"කුජ {mars.get('house')} වන භාවයේ {mars['rashi']['name']} රාශියේ {_planet_state_text('කුජ',dmap)} තත්ත්වයේ සිටී. එය {HOUSE_MEANINGS.get(mars.get('house'))} අංශයට වේගය, තරඟකාරීත්වය සහ ආවේගය එක් කරයි. උදාහරණයක් ලෙස, එම අංශයේ තීරණයක් ගන්න කලින් පැය කිහිපයක් හෝ දවසක් තබා නැවත පරීක්ෂා කිරීම වාද/අලාභ අඩු කිරීමට උපකාරී වේ."})

    # Personalized remedies from exact weak/pressured houses and dasha
    remedies=[]
    weak=[]
    for h in range(1,13):
        pos,cau=_section_judgement([h],lag_i,planets,aspects,dmap,current_lord)
        if cau: weak.append((h,cau))
    if current_lord=='Saturn': remedies.append("වත්මන් ශනි දශාව සඳහා: නියමිත වේලාවට වැඩ කිරීම, ණය/බිල් ප්‍රමාද නොකිරීම, වැඩිහිටියන්ට හෝ අවශ්‍යතා ඇති අයට සේවාවක් කිරීම සහ සෙනසුරාදා සරල පින්කමක් කිරීම සාම්ප්‍රදායිකව යෝග්‍ය ලෙස සලකයි.")
    elif current_lord=='Rahu': remedies.append("වත්මන් රාහු දශාව සඳහා: සැක සහිත ගිවිසුම්, ඉක්මන් ණය සහ නොපැහැදිලි විදේශ අවස්ථා වලින් වැළකී ලේඛන දෙවරක් පරීක්ෂා කිරීම ප්‍රධාන ප්‍රායෝගික පිළියමකි.")
    elif current_lord=='Mars': remedies.append("වත්මන් කුජ දශාව සඳහා: වාදයට පෙර විරාමයක් ගැනීම, ක්‍රමවත් ශාරීරික ව්‍යායාම, වාහන/යන්ත්‍ර භාවිතයේ සැලකිල්ල සහ හදිසි මුදල් තීරණ ප්‍රමාද කිරීම හොඳය.")
    elif current_lord=='Mercury': remedies.append("වත්මන් බුධ දශාව සඳහා: ලේඛන, අංක, ගිවිසුම් සහ අයදුම්පත් දෙවරක් පරීක්ෂා කිරීම, නව කුසලතාවක් ඉගෙනීම සහ අධ්‍යාපනික උදව්/දානය යහපත් ලෙස සලකයි.")
    elif current_lord=='Jupiter': remedies.append("වත්මන් ගුරු දශාව සඳහා: ගුරුවරුන්ට/මව්පියන්ට ගෞරවය, අධ්‍යාපනයට උදව් කිරීම, දැනුම වැඩි කිරීම සහ අධික විශ්වාසයෙන් විශාල මුදල් තීරණ නොගැනීම සුදුසුය.")
    elif current_lord=='Venus': remedies.append("වත්මන් ශුක්‍ර දශාව සඳහා: සබඳතා තුළ ගරුක කථනය, පිරිසිදුකම, කලාව/සංගීතය වැනි සන්සුන් ක්‍රියා සහ අනවශ්‍ය සුඛෝපභෝගී වියදම් පාලනය කිරීම යහපත්ය.")
    elif current_lord=='Moon': remedies.append("වත්මන් චන්ද්‍ර දශාව සඳහා: නිදාගැනීමේ රටාව, පවුල් සම්බන්ධතා, මනස සන්සුන් කරන ආගමික/භාවනා ක්‍රියා සහ හැඟීම් වැඩි දවසක විශාල තීරණ පසුවට තැබීම ප්‍රයෝජනවත්ය.")
    elif current_lord=='Sun': remedies.append("වත්මන් රවි දශාව සඳහා: වැඩිහිටියන්ට ගෞරවය, නිල ලේඛන නිවැරදිව තබාගැනීම, අහංකාර වාද අඩු කිරීම සහ වගකීමෙන් නායකත්වය දීම යහපත්ය.")
    elif current_lord=='Ketu': remedies.append("වත්මන් කේතු දශාව සඳහා: භාවනා, අනවශ්‍ය වැඩ අඩු කිරීම, හදිසි වෙන්වීම් තීරණ ප්‍රමාද කිරීම සහ සරල පින්කම්/දාන කිරීම සුදුසුය.")
    for h,cau in weak[:3]:
        remedies.append(f"{h} වන භාවය සඳහා: {HOUSE_MEANINGS[h]} සම්බන්ධ අංශයේ ලේඛන, සැලසුම් සහ වගකීම් වැඩි පැහැදිලිව තබාගන්න. උදාහරණයක්: මෙම අංශයට අදාළ තීරණයක් ගැනීමට පෙර වියදම්/කාලසටහන/ගිවිසුම් ලිඛිතව පරීක්ෂා කරන්න.")
    remedies.append("සාම්ප්‍රදායික පිළියම් බිය ඇති කිරීමට නොව, සංයමය, පින්කම් සහ හොඳ හැසිරීම් ගොඩනැගීමට භාවිතා කළ යුතුය. අධික මුදල් ඉල්ලන යන්ත්‍ර, රත්න හෝ පූජා අනිවාර්ය ප්‍රතිකාර ලෙස නොසලකන්න.")
    sections.append({"title":"19. මෙම කේන්දරයට අදාළ සාම්ප්‍රදායික සහ ප්‍රායෝගික පිළියම්","text":" ".join(remedies)})

    # final unique synthesis
    strongest=[]; pressured=[]
    for h in range(1,13):
        pos,cau=_section_judgement([h],lag_i,planets,aspects,dmap,current_lord)
        if len(pos)>len(cau): strongest.append(h)
        if len(cau)>len(pos): pressured.append(h)
    final=("මෙම කේන්දරයේ සාපේක්ෂව සහායක භාවයන්: " + (", ".join(map(str,strongest[:5])) if strongest else "මිශ්‍ර") + ". "
           "වැඩි සැලකිල්ලක් අවශ්‍ය භාවයන්: " + (", ".join(map(str,pressured[:5])) if pressured else "විශේෂ එකක් නොපෙනේ") + ". "
           "ඒ නිසා මෙම වාර්තාවේ ප්‍රතිඵල සාමාන්‍ය වාක්‍ය නොව, ඔබගේ ලග්නය, ග්‍රහ භාව, අධිපති පිහිටීම්, දෘෂ්ටි, ග්‍රහ තත්ත්වය සහ දශාව මත වෙන වෙනම සකස් කර ඇත.")
    sections.append({"title":"20. කේන්දරයේ සමස්ත නිගමනය","text":final})
    return {"summary":summary,"sections":sections}


def detailed_reading(lagna, planets, dasha):
    return expanded_reading(lagna, planets, dasha, reference=False)

def calculate_birth(data):
    tz_used, tz_source = effective_timezone_offset(data)
    data = dict(data)
    data["timezone_offset"] = tz_used
    data["timezone_source"] = tz_source
    utc = local_to_utc(data["birth_date"], data["birth_time"], tz_used)
    jd = jd_from_dt(utc)
    planets = planet_positions(jd)
    lag = ascendant(jd, data.get("latitude", 6.9271), data.get("longitude", 79.8612))
    lag_i = lag["rashi"]["index"]
    for p in planets.values():
        p["house"] = whole_sign_house(p["rashi"]["index"], lag_i)
    local_birth = datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
    dasha = dasha_timeline(local_birth, planets["Moon"]["longitude"])
    reading = detailed_reading(lag, planets, dasha)
    advanced = advanced_jyotishya(planets, lag, dasha, jd)
    return {
        "mode":"calculated",
        "person": data,
        "lagna": lag,
        "moon_sign": planets["Moon"]["rashi"],
        "birth_nakshatra": planets["Moon"]["nakshatra"],
        "planets": planets,
        "rashi_chart": fixed_sign_chart(planets, lag, "rashi"),
        "navamsa_chart": fixed_sign_chart(planets, lag, "navamsa"),
        "houses": house_summary(planets, lag_i),
        "dasha": dasha,
        "reading": reading,
        "advanced": advanced,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "disclaimer": "මෙය සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය ගණනය/විග්‍රහයකි. විද්‍යාත්මකව අනාගතය තහවුරු කරන ක්‍රමයක් නොවේ."
    }


def sign_from_index(i):
    i = int(i) % 12
    return {"index": i, "number": i+1, "name": RASHI[i], "english": RASHI_EN[i], "degree": 0}


def build_reference_planets(items, lagna_idx):
    out = {}
    for item in items:
        key = item.get("key")
        if key not in PLANET_ORDER:
            continue
        sign_index = int(item.get("sign_index", 0)) % 12
        house = int(item.get("house", 0) or 0)
        if house < 1 or house > 12:
            house = whole_sign_house(sign_index, lagna_idx)
        degree = float(item.get("degree", 0) or 0)
        lon = sign_index * 30 + (degree % 30)
        out[key] = {
            "key": key,
            "name": PLANET_SI[key],
            "longitude": round(lon, 4),
            "rashi": {"index": sign_index, "number": sign_index+1, "name": RASHI[sign_index], "english": RASHI_EN[sign_index], "degree": round(degree % 30, 4)},
            "navamsa": navamsa_info(lon),
            "nakshatra": nak_info(lon),
            "retrograde": bool(item.get("retrograde", False)),
            "house": house,
        }
    for key in PLANET_ORDER:
        if key not in out:
            sign_index = lagna_idx
            house = whole_sign_house(sign_index, lagna_idx)
            out[key] = {
                "key": key,
                "name": PLANET_SI[key],
                "longitude": sign_index * 30,
                "rashi": {"index": sign_index, "number": sign_index+1, "name": RASHI[sign_index], "english": RASHI_EN[sign_index], "degree": 0},
                "navamsa": navamsa_info(sign_index*30),
                "nakshatra": nak_info(sign_index*30),
                "retrograde": False,
                "house": house,
            }
    return out


def dasha_from_reference(ref):
    maha = ref.get("current_mahadasha") or ref.get("current_dasha") or ""
    antar = ref.get("current_antardasha") or ""
    current = None
    if maha:
        current = {"lord": maha, "name": DASHA_SI.get(maha, maha), "years": DASHA_YEARS.get(maha, 0), "start": ref.get("current_dasha_start", ""), "end": ref.get("current_dasha_end", "")}
    periods = []
    for item in ref.get("dasha_periods", []):
        lord = item.get("lord") or item.get("name") or ""
        periods.append({
            "lord": lord,
            "name": DASHA_SI.get(lord, lord),
            "years": item.get("years", DASHA_YEARS.get(lord, "")),
            "start": item.get("start", ""),
            "end": item.get("end", "")
        })
    return {"current": current, "periods": periods, "birth_nakshatra_lord": maha, "antardasha": DASHA_SI.get(antar, antar) if antar else ""}


def reference_reading(ref, lagna, planets, dasha):
    reading = expanded_reading(lagna, planets, dasha, reference=True)
    prefix = [
        "මෙය පවතින හෝ අත්ලිපි කේන්දරයක මුල් අගයන් ඇසුරින් සකස් කළ විග්‍රහයකි.",
        f"ලග්නය {lagna['rashi']['name']}, චන්ද්‍ර රාශිය {ref['moon_sign_name']}, ජන්ම නැකත {ref['birth_nakshatra_name']} ලෙස මුල් කේන්දර අගයන්හි සලකා ඇත.",
    ]
    if ref.get("source_notes"):
        prefix.append("මුල් ජ්‍යෝතිෂ්‍ය සටහන් report එකේ වෙනම කොටසක් ලෙස තබා ඇත.")
    reading["summary"] = prefix + reading["summary"]
    return reading


def auto_reference_from_birth(data, anchors=None):
    """Calculate all technical chart fields from the minimum birth inputs.
    Optional anchors let the user keep a few values copied from an existing handwritten chart.
    """
    anchors = anchors or {}
    calculated = calculate_birth(validate_birth(dict(data)))
    ref = {
        "name": calculated["person"].get("name", ""),
        "birth_date": calculated["person"].get("birth_date", ""),
        "birth_time": calculated["person"].get("birth_time", ""),
        "birth_place": calculated["person"].get("birth_place", ""),
        "timezone_offset": calculated["person"].get("timezone_offset", ""),
        "lagna_sign_index": calculated["lagna"]["rashi"]["index"],
        "moon_sign_index": calculated["moon_sign"]["index"],
        "nakshatra_index": calculated["birth_nakshatra"]["index"],
        "nakshatra_pada": calculated["birth_nakshatra"]["pada"],
        "current_mahadasha": calculated["dasha"]["current"]["lord"] if calculated["dasha"].get("current") else "",
        "current_dasha_start": calculated["dasha"]["current"]["start"] if calculated["dasha"].get("current") else "",
        "current_dasha_end": calculated["dasha"]["current"]["end"] if calculated["dasha"].get("current") else "",
        "planets": [],
        "source_notes": anchors.get("source_notes", "")
    }
    for key in PLANET_ORDER:
        p = calculated["planets"][key]
        ref["planets"].append({
            "key": key,
            "sign_index": p["rashi"]["index"],
            "house": p["house"],
            "degree": p["rashi"]["degree"],
            "retrograde": p.get("retrograde", False),
        })

    # A few original-chart anchor values can override the calculated defaults.
    if anchors.get("lagna_sign_index") not in (None, ""):
        ref["lagna_sign_index"] = int(anchors["lagna_sign_index"])
    if anchors.get("moon_sign_index") not in (None, ""):
        ref["moon_sign_index"] = int(anchors["moon_sign_index"])
    if anchors.get("nakshatra_index") not in (None, ""):
        ref["nakshatra_index"] = int(anchors["nakshatra_index"])
    if anchors.get("nakshatra_pada") not in (None, ""):
        ref["nakshatra_pada"] = int(anchors["nakshatra_pada"])
    if anchors.get("current_mahadasha"):
        ref["current_mahadasha"] = anchors["current_mahadasha"]
    if anchors.get("current_antardasha"):
        ref["current_antardasha"] = anchors["current_antardasha"]
    if anchors.get("current_dasha_start"):
        ref["current_dasha_start"] = anchors["current_dasha_start"]
    if anchors.get("current_dasha_end"):
        ref["current_dasha_end"] = anchors["current_dasha_end"]
    return ref

def analyze_reference(ref):
    lagna_idx = int(ref.get('lagna_sign_index', 0)) % 12
    moon_idx = int(ref.get('moon_sign_index', lagna_idx)) % 12
    nak_idx = int(ref.get('nakshatra_index', 0)) % 27
    pada = int(ref.get('nakshatra_pada', 1) or 1)
    lagna = {"rashi": sign_from_index(lagna_idx), "navamsa": sign_from_index(lagna_idx)}
    planets = build_reference_planets(ref.get('planets', []), lagna_idx)
    moon = planets.get('Moon')
    moon['rashi'] = sign_from_index(moon_idx)
    moon['house'] = int(ref.get('moon_house', whole_sign_house(moon_idx, lagna_idx)) or whole_sign_house(moon_idx, lagna_idx))
    birth_nak = {"index": nak_idx, "number": nak_idx+1, "name": NAK[nak_idx], "english": NAK_EN[nak_idx], "pada": pada, "lord": NAK_LORD[nak_idx]}
    person = {
        "name": ref.get('name',''),
        "birth_date": ref.get('birth_date',''),
        "birth_time": ref.get('birth_time',''),
        "birth_place": ref.get('birth_place',''),
        "timezone_source": "මුල් අගයන් / අතින් ඇතුළත් කළ",
        "timezone_offset": ref.get('timezone_offset',''),
        "source_notes": ref.get('source_notes','')
    }
    houses = house_summary(planets, lagna_idx)
    dasha = dasha_from_reference(ref)
    normalized = {
        "moon_sign_name": RASHI[moon_idx],
        "birth_nakshatra_name": NAK[nak_idx],
        "source_notes": ref.get('source_notes','')
    }
    reading = reference_reading(normalized, lagna, planets, dasha)
    try:
        tz=float(person.get("timezone_offset") or 5.5)
        bdt=local_to_utc(person.get("birth_date"), person.get("birth_time"), tz)
        ref_jd=jd_from_dt(bdt)
    except Exception:
        ref_jd=jd_from_dt(datetime.utcnow())
    advanced = advanced_jyotishya(planets, lagna, dasha, ref_jd)
    return {
        "mode":"reference",
        "person":person,
        "lagna":lagna,
        "moon_sign":sign_from_index(moon_idx),
        "birth_nakshatra":birth_nak,
        "planets":planets,
        "rashi_chart":fixed_sign_chart(planets, lagna, 'rashi'),
        "navamsa_chart":fixed_sign_chart(planets, lagna, 'navamsa'),
        "houses":houses,
        "dasha":dasha,
        "reading":reading,
        "advanced":advanced,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "disclaimer":"මෙය ඔබ ඇතුළත් කළ කේන්දරයේ මුල් අගයන් මත පදනම් වූ විග්‍රහයකි."
    }


def relation_score(a,b):
    if a == b:
        return ("හොඳයි",1.0)
    if b in FRIENDS.get(a,set()) or a in FRIENDS.get(b,set()):
        return ("හොඳයි",1.0)
    return ("මධ්‍යම",0.5)



def porondam_factor(name, score, note, weight=5, category="සාමාන්‍ය", critical=False):
    score = max(0.0, min(1.0, float(score)))
    if score >= 0.75:
        grade = "ඉතා හොඳයි" if score >= 0.95 else "ගැලපේ"
    elif score >= 0.4:
        grade = "මධ්‍යම"
    else:
        grade = "අවධානය"
    return {"name":name,"grade":grade,"score":round(score,2),"weight":weight,"weighted":round(score*weight,2),"note":note,"category":category,"critical":bool(critical and score < 0.4)}

# නැකත් යෝනි වර්ග. සම්ප්‍රදාය අනුව කුඩා වෙනස්කම් තිබිය හැක.
YONI = ["අශ්ව","ගජ","එළු","සර්ප","සර්ප","සුනඛ","බළලා","එළු","බළලා","මීයා","මීයා","ගව","මහීෂ","ව්‍යාඝ්‍ර","මහීෂ","ව්‍යාඝ්‍ර","මුව","මුව","සුනඛ","වඳුරු","මුගටි","වඳුරු","සිංහ","අශ්ව","සිංහ","ගව","ගජ"]
YONI_ENEMY = {frozenset(x) for x in [("අශ්ව","මහීෂ"),("ගජ","සිංහ"),("එළු","වඳුරු"),("සර්ප","මුගටි"),("සුනඛ","මුව"),("බළලා","මීයා"),("ගව","ව්‍යාඝ්‍ර")]}
NADI = ["ආදි","මධ්‍ය","අන්ත්‍ය"] * 9
VARNA = ["ක්ෂත්‍රිය","වෛශ්‍ය","ශූද්‍ර","බ්‍රාහ්මණ","ක්ෂත්‍රිය","වෛශ්‍ය","ශූද්‍ර","බ්‍රාහ්මණ","ක්ෂත්‍රිය","වෛශ්‍ය","ශූද්‍ර","බ්‍රාහ්මණ"]
VARNA_RANK = {"ශූද්‍ර":1,"වෛශ්‍ය":2,"ක්ෂත්‍රිය":3,"බ්‍රාහ්මණ":4}

def kuja_dosha_level(chart):
    lag_i=chart["lagna"]["rashi"]["index"]
    moon_i=chart["moon_sign"]["index"]
    venus_i=chart["planets"]["Venus"]["rashi"]["index"]
    mars_i=chart["planets"]["Mars"]["rashi"]["index"]
    bad={1,2,4,7,8,12}
    refs=[]
    for label,base in [("ලග්නය",lag_i),("චන්ද්‍රය",moon_i),("ශුක්‍රය",venus_i)]:
        h=((mars_i-base)%12)+1
        refs.append((label,h,h in bad))
    level=sum(1 for _,_,x in refs if x)
    return level, refs

def porondam(groom, bride):
    gn = groom["birth_nakshatra"]["index"]
    bn = bride["birth_nakshatra"]["index"]
    gr = groom["moon_sign"]["index"]
    br = bride["moon_sign"]["index"]
    glag = groom["lagna"]["rashi"]["index"]
    blag = bride["lagna"]["rashi"]["index"]
    count = ((gn - bn) % 27) + 1
    rev_count = ((bn - gn) % 27) + 1
    factors=[]

    factors.append(porondam_factor("දින / තාරා පොරොන්දම", 1 if count in {2,4,6,8,9,11,13,15,18,20,24,26} else 0, f"ස්ත්‍රී නැකතෙන් පුරුෂ නැකතට ගණන {count}", 7,"නැකත්"))
    gg,bg=GANA[gn],GANA[bn]
    gs=1 if gg==bg else (0.6 if {gg,bg}=={"Deva","Manushya"} else 0.15)
    factors.append(porondam_factor("ගණ පොරොන්දම",gs,f"{GANA_SI[bg]} / {GANA_SI[gg]}",6,"නැකත්"))
    factors.append(porondam_factor("මහේන්ද්‍ර පොරොන්දම",1 if count in {4,7,10,13,16,19,22,25} else 0.25,f"නැකත් ගණන {count}",4,"නැකත්"))
    factors.append(porondam_factor("ස්ත්‍රී දීර්ඝ පොරොන්දම",1 if count>=13 else (0.5 if count>=9 else 0.15),f"ගණන {count}",4,"නැකත්"))
    by,gy=YONI[bn],YONI[gn]
    yp=frozenset((by,gy))
    ys=1 if by==gy else (0.1 if yp in YONI_ENEMY else 0.65)
    factors.append(porondam_factor("යෝනි පොරොන්දම",ys,f"{by} / {gy}",6,"නැකත්"))

    pair={((gr-br)%12)+1,((br-gr)%12)+1}
    rashi_bad=(2 in pair and 12 in pair) or (6 in pair and 8 in pair)
    factors.append(porondam_factor("රාශි පොරොන්දම",0.15 if rashi_bad else 1,f"චන්ද්‍ර රාශි: {RASHI[br]} / {RASHI[gr]}",7,"රාශි"))
    gl,bl=RASHI_LORD[gr],RASHI_LORD[br]
    _,rel=relation_score(gl,bl)
    factors.append(porondam_factor("රාශි අධිපති මෛත්‍රී",rel,f"{DASHA_SI.get(bl,bl)} / {DASHA_SI.get(gl,gl)}",5,"රාශි"))
    vasya=1 if gr==br or ((gr-br)%12 in {2,3,4,6,8,9,10}) else 0.35
    factors.append(porondam_factor("වශ්‍ය පොරොන්දම",vasya,"රාශි අතර ආකර්ෂණ හා සහයෝගී සම්බන්ධතාවය",4,"රාශි"))
    same_rajju=RAJJU[gn]==RAJJU[bn]
    factors.append(porondam_factor("රජ්ජු පොරොන්දම",0 if same_rajju else 1,f"{RAJJU_SI[RAJJU[bn]]} / {RAJJU_SI[RAJJU[gn]]}"+(" — එකම රජ්ජු කාණ්ඩය" if same_rajju else ""),10,"අත්‍යවශ්‍ය",True))
    vedha_bad=tuple(sorted((gn+1,bn+1))) in VEDHA_PAIRS
    factors.append(porondam_factor("වේධ පොරොන්දම",0 if vedha_bad else 1,"වේධ නැකත් යුගලයක්" if vedha_bad else "ප්‍රධාන වේධ යුගලයක් නොපෙනේ",8,"අත්‍යවශ්‍ය",True))

    same_nadi=NADI[gn]==NADI[bn]
    factors.append(porondam_factor("නාඩි පොරොන්දම",0 if same_nadi else 1,f"{NADI[bn]} / {NADI[gn]}",8,"අත්‍යවශ්‍ය",True))
    bv,gv=VARNA[br],VARNA[gr]
    vs=1 if VARNA_RANK[gv]>=VARNA_RANK[bv] else 0.45
    factors.append(porondam_factor("වර්ණ පොරොන්දම",vs,f"{bv} / {gv}",3,"රාශි"))
    bnl=NAK_LORD[bn]; gnl=NAK_LORD[gn]
    _,nrel=relation_score(bnl,gnl)
    factors.append(porondam_factor("නැකත් අධිපති මෛත්‍රී",nrel,f"{DASHA_SI.get(bnl,bnl)} / {DASHA_SI.get(gnl,gnl)}",4,"නැකත්"))
    md=min(count,rev_count)
    factors.append(porondam_factor("චන්ද්‍ර දුර ගැලපීම",1 if md not in {2,6,8,12} else 0.35,f"රාශි/නැකත් චක්‍රයේ සම්බන්ධ දුර {md}",3,"රාශි"))

    lagdist=((glag-blag)%12)+1
    lagpair={lagdist,((blag-glag)%12)+1}
    ls=0.3 if (6 in lagpair and 8 in lagpair) or (2 in lagpair and 12 in lagpair) else 1
    factors.append(porondam_factor("ලග්න ගැලපීම",ls,f"{RASHI[blag]} / {RASHI[glag]}",6,"සම්පූර්ණ කේන්දර"))
    b7=(blag+6)%12; g7=(glag+6)%12
    _,s7=relation_score(RASHI_LORD[b7],RASHI_LORD[g7])
    factors.append(porondam_factor("සත්වන භාව අධිපති ගැලපීම",s7,f"ස්ත්‍රී: {DASHA_SI.get(RASHI_LORD[b7],RASHI_LORD[b7])} / පුරුෂ: {DASHA_SI.get(RASHI_LORD[g7],RASHI_LORD[g7])}",6,"සම්පූර්ණ කේන්දර"))
    bven=bride["planets"]["Venus"]["rashi"]["index"]; gven=groom["planets"]["Venus"]["rashi"]["index"]
    vdist=((gven-bven)%12)+1
    factors.append(porondam_factor("ශුක්‍ර ගැලපීම",1 if vdist in {1,3,4,5,7,9,10,11} else 0.45,f"ශුක්‍ර රාශි: {RASHI[bven]} / {RASHI[gven]}",4,"සම්පූර්ණ කේන්දර"))
    bj=bride["planets"]["Jupiter"]["rashi"]["index"]; gj=groom["planets"]["Jupiter"]["rashi"]["index"]
    jdist=((gj-bj)%12)+1
    factors.append(porondam_factor("ගුරු ගැලපීම",1 if jdist in {1,3,5,7,9,11} else 0.5,f"ගුරු රාශි: {RASHI[bj]} / {RASHI[gj]}",3,"සම්පූර්ණ කේන්දර"))

    bk,brefs=kuja_dosha_level(bride); gk,grefs=kuja_dosha_level(groom)
    diff=abs(bk-gk); ks=1 if diff==0 else (0.65 if diff==1 else 0.15)
    factors.append(porondam_factor("කුජ දෝෂ සමානතාව",ks,f"ස්ත්‍රී දර්ශකය {bk}/3 • පුරුෂ දර්ශකය {gk}/3",8,"අත්‍යවශ්‍ය",diff>=2))
    bcur=bride.get("dasha",{}).get("current"); gcur=groom.get("dasha",{}).get("current")
    if bcur and gcur:
        _,ds=relation_score(bcur.get("lord"),gcur.get("lord"))
        dnote=f"වත්මන් මහා දශා: {bcur.get('name','—')} / {gcur.get('name','—')}"
    else:
        ds=0.5; dnote="වත්මන් දශා දෙකම සම්පූර්ණව ලබාගත නොහැකි විය"
    factors.append(porondam_factor("දශා කාල ගැලපීම",ds,dnote,4,"කාල ගැලපීම"))
    total_weight=sum(f["weight"] for f in factors)
    weighted=sum(f["weighted"] for f in factors)
    pct=round((weighted/total_weight)*100,1) if total_weight else 0
    critical=[f["name"] for f in factors if f.get("critical")]
    if critical:
        verdict="විශේෂ අවධානය අවශ්‍යයි"
    elif pct>=80:
        verdict="ඉතා හොඳ ගැලපීමක්"
    elif pct>=65:
        verdict="හොඳ ගැලපීමක්"
    elif pct>=50:
        verdict="මධ්‍යම ගැලපීමක්"
    else:
        verdict="ගැඹුරු විග්‍රහයක් අවශ්‍යයි"
    categories={}
    for f in factors:
        c=f["category"]; categories.setdefault(c,{"earned":0,"total":0}); categories[c]["earned"]+=f["weighted"]; categories[c]["total"]+=f["weight"]
    cat_rows=[]
    for c,v in categories.items():
        cat_rows.append({"name":c,"percent":round(v["earned"]/v["total"]*100,1) if v["total"] else 0})
    return {
        "groom_summary":{"name":groom["person"]["name"],"nakshatra":groom["birth_nakshatra"],"moon_sign":groom["moon_sign"],"lagna":groom["lagna"]["rashi"]},
        "bride_summary":{"name":bride["person"]["name"],"nakshatra":bride["birth_nakshatra"],"moon_sign":bride["moon_sign"],"lagna":bride["lagna"]["rashi"]},
        "factors":factors,"score":pct,"out_of":100,"verdict":verdict,"categories":cat_rows,"critical_flags":critical,
        "kuja":{"bride":bk,"groom":gk,"bride_refs":brefs,"groom_refs":grefs},
        "note":"මෙය නැකත් පොරොන්දම් සමඟ ලග්න, සත්වන භාව, ශුක්‍ර, ගුරු, කුජ දෝෂ සහ දශා පසුබිමද එකට ගත් විස්තීර්ණ ගැලපුම් වාර්තාවකි. සම්ප්‍රදායන් අනුව නීති වෙනස් විය හැකි බැවින් අවසන් තීරණයට පෙර සම්පූර්ණ කේන්දර දෙකම ප්‍රවීණව විග්‍රහ කිරීම යෝග්‍යය."
    }

def validate_birth(d):
    if not isinstance(d, dict):
        raise ValueError("Invalid birth data")
    for k in ("birth_date", "birth_time"):
        if not d.get(k):
            raise ValueError(f"Missing {k}")
    datetime.strptime(d["birth_date"], "%Y-%m-%d")
    datetime.strptime(d["birth_time"], "%H:%M")
    d.setdefault("name", "")
    d.setdefault("birth_place", "Colombo")
    d["latitude"] = float(d.get("latitude", 6.9271))
    d["longitude"] = float(d.get("longitude", 79.8612))
    d["timezone_offset"] = float(d.get("timezone_offset", 5.5))
    if not -90 <= d["latitude"] <= 90:
        raise ValueError("Latitude must be between -90 and 90")
    if not -180 <= d["longitude"] <= 180:
        raise ValueError("Longitude must be between -180 and 180")
    if not -14 <= d["timezone_offset"] <= 14:
        raise ValueError("Timezone must be between -14 and +14")
    return d


def jbytes(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def self_test():
    sample = {
        "name": "Self Test",
        "birth_date": "1997-03-18",
        "birth_time": "10:20",
        "birth_place": "Hambantota",
        "latitude": 6.1241,
        "longitude": 81.1185,
        "timezone_offset": 5.5,
    }
    result = calculate_birth(validate_birth(dict(sample)))
    assert result["lagna"]["rashi"]["name"]
    assert len(result["planets"]) == 9
    assert result["birth_nakshatra"]["name"]
    assert len(result["rashi_chart"]) == 12
    assert len(result["navamsa_chart"]) == 12
    ref = analyze_reference({
        "name":"Manual", "birth_date":"1997-03-18", "birth_time":"10:20", "birth_place":"Hambantota",
        "lagna_sign_index":3, "moon_sign_index":3, "nakshatra_index":9, "nakshatra_pada":1,
        "current_mahadasha":"Saturn",
        "planets":[{"key":"Sun","sign_index":11,"house":9},{"key":"Moon","sign_index":3,"house":1},{"key":"Mars","sign_index":4,"house":2}]
    })
    assert ref["mode"] == "reference"
    auto = auto_reference_from_birth(sample, {"lagna_sign_index":3})
    assert auto["lagna_sign_index"] == 3
    assert len(ref["planets"]) == 9
    match = porondam(result, result)
    assert len(match["factors"]) == 20
    assert match["out_of"] == 100
    av = result["advanced"]["ashtakavarga"]
    assert av["total"] == 337
    assert all(x["ok"] for x in av["checks"].values())
    return True




# --- විස්තීර්ණ මුහුර්ත ගණනය (v2.6) ---
MUHURTA_PURPOSES = {
    "විවාහය": {
        "weekdays":{"සඳුදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"රෙහෙණ","මුවසිරස","මා","උත්‍රපල්","හත","සා","අනුර","මුල","උත්‍රසල","රේවතී"},
        "tithi":{2,3,5,7,10,11,13}, "hora":{"Venus","Jupiter","Moon"}
    },
    "ව්‍යාපාර ආරම්භය": {
        "weekdays":{"බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"අස්විද","රෙහෙණ","මුවසිරස","පුෂ","හත","සා","අනුර","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11,13}, "hora":{"Mercury","Jupiter","Venus"}
    },
    "ගෙදර වැඩ ආරම්භය": {
        "weekdays":{"සඳුදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"රෙහෙණ","මුවසිරස","පුෂ","උත්‍රපල්","හත","අනුර","උත්‍රසල","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11,13}, "hora":{"Jupiter","Venus","Moon"}
    },
    "ගමන් ආරම්භය": {
        "weekdays":{"සඳුදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"අස්විද","මුවසිරස","පුනාවස","පුෂ","හත","සා","අනුර","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11}, "hora":{"Moon","Mercury","Jupiter"}
    },
    "ගිවිසුමක්": {
        "weekdays":{"බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"රෙහෙණ","මුවසිරස","පුෂ","හත","සා","අනුර","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11,13}, "hora":{"Mercury","Venus","Jupiter"}
    },
    "නව රැකියාව": {
        "weekdays":{"ඉරිදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"අස්විද","රෙහෙණ","මුවසිරස","පුෂ","හත","සා","අනුර","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11}, "hora":{"Sun","Jupiter","Mercury"}
    },
    "වාහනයක් මිලදී ගැනීම": {
        "weekdays":{"සඳුදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"අස්විද","රෙහෙණ","මුවසිරස","පුෂ","හත","සා","අනුර","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11,13}, "hora":{"Venus","Moon","Mercury"}
    },
    "අධ්‍යාපන ආරම්භය": {
        "weekdays":{"බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා"},
        "nak":{"අස්විද","රෙහෙණ","මුවසිරස","පුනාවස","පුෂ","හත","සා","සුවණ","රේවතී"},
        "tithi":{2,3,5,7,10,11}, "hora":{"Mercury","Jupiter","Venus"}
    }
}
GOOD_YOGA = {"ප්‍රීති","ආයුෂ්මාන්","සෞභාග්‍ය","ශෝභන","සුකර්ම","ධෘති","වෘද්ධි","ධෘව","හර්ෂණ","සිද්ධි","ශිව","සිද්ධ","සාධ්‍ය","ශුභ","ශුක්ල","බ්‍රහ්ම","ඉන්ද්‍ර"}
BAD_YOGA = {"අතිගණ්ඩ","ශූල","ගණ්ඩ","ව්‍යාඝාත","වජ්‍ර","ව්‍යතිපාත","පරිඝ","වෛධෘති"}
BAD_KARANA = {"විෂ්ටි","ශකුණි","චතුෂ්පාද","නාග"}
HORA_SEQ = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]
WEEKDAY_LORD = {"ඉරිදා":"Sun","සඳුදා":"Moon","අඟහරුවාදා":"Mars","බදාදා":"Mercury","බ්‍රහස්පතින්දා":"Jupiter","සිකුරාදා":"Venus","සෙනසුරාදා":"Saturn"}
RAHU_SEG = {"ඉරිදා":8,"සඳුදා":2,"අඟහරුවාදා":7,"බදාදා":5,"බ්‍රහස්පතින්දා":6,"සිකුරාදා":4,"සෙනසුරාදා":3}
YAMA_SEG = {"ඉරිදා":5,"සඳුදා":4,"අඟහරුවාදා":3,"බදාදා":2,"බ්‍රහස්පතින්දා":1,"සිකුරාදා":7,"සෙනසුරාදා":6}
GULIKA_SEG = {"ඉරිදා":7,"සඳුදා":6,"අඟහරුවාදා":5,"බදාදා":4,"බ්‍රහස්පතින්දා":3,"සිකුරාදා":2,"සෙනසුරාදා":1}


def _jd_to_datetime(jd):
    y,m,d,h = swe.revjul(jd, swe.GREG_CAL)
    hh=int(h); mm=int((h-hh)*60); ss=int(round((((h-hh)*60)-mm)*60))
    if ss>=60: ss=0; mm+=1
    if mm>=60: mm=0; hh+=1
    return datetime(y,m,d,0,0)+timedelta(hours=hh,minutes=mm,seconds=ss)


def _sunrise_sunset(local_date, lat, lon, tz):
    local_mid=datetime.strptime(local_date, "%Y-%m-%d")
    utc_mid=local_mid-timedelta(hours=tz)
    jd0=jd_from_dt(utc_mid)
    geopos=(float(lon),float(lat),0.0)
    try:
        _,rt=swe.rise_trans(jd0,swe.SUN,swe.CALC_RISE,geopos,0.0,15.0,swe.FLG_SWIEPH)
        _,st=swe.rise_trans(jd0,swe.SUN,swe.CALC_SET,geopos,0.0,15.0,swe.FLG_SWIEPH)
        rise=_jd_to_datetime(rt[0])+timedelta(hours=tz)
        sett=_jd_to_datetime(st[0])+timedelta(hours=tz)
        if rise.date()!=local_mid.date():
            _,rt=swe.rise_trans(jd0+1,swe.SUN,swe.CALC_RISE,geopos,0.0,15.0,swe.FLG_SWIEPH); rise=_jd_to_datetime(rt[0])+timedelta(hours=tz)
        if sett.date()!=local_mid.date():
            _,st=swe.rise_trans(jd0+1,swe.SUN,swe.CALC_SET,geopos,0.0,15.0,swe.FLG_SWIEPH); sett=_jd_to_datetime(st[0])+timedelta(hours=tz)
        return rise,sett
    except Exception:
        return local_mid.replace(hour=6), local_mid.replace(hour=18)


def _segment_window(rise, sett, seg_num):
    span=(sett-rise)/8
    start=rise+span*(seg_num-1)
    return start,start+span


def _fmt_time(dt): return dt.strftime("%H:%M")

def _in_window(dt, win): return win[0] <= dt < win[1]

def _angular_sep(a,b):
    d=abs(norm(a-b)); return min(d,360-d)


def _hora_lord(local_dt, rise, sett, vara):
    if local_dt < rise or local_dt >= sett: return ""
    hour_len=(sett-rise)/12
    idx=int((local_dt-rise)/hour_len)
    first=WEEKDAY_LORD.get(vara,"Sun")
    start=HORA_SEQ.index(first)
    return HORA_SEQ[(start+idx)%7]


def _tara_bala(natal_nak, current_nak):
    if natal_nak is None: return None
    count=((int(current_nak)-int(natal_nak))%27)+1
    tara=((count-1)%9)+1
    names={1:"ජන්ම",2:"සම්පත්",3:"විපත්",4:"ක්ෂේම",5:"ප්‍රත්‍යරි",6:"සාධන",7:"නයිධන",8:"මිත්‍ර",9:"පරම මිත්‍ර"}
    return {"count":count,"tara":tara,"name":names[tara],"good":tara in {2,4,6,8,9},"bad":tara in {3,5,7}}


def _chandra_bala(natal_moon, current_moon):
    if natal_moon is None: return None
    dist=((int(current_moon)-int(natal_moon))%12)+1
    return {"distance":dist,"good":dist in {1,3,6,7,10,11},"ashtama":dist==8}


def _simple_muhurta_chart(ds, tm, lat, lon, tz):
    utc=local_to_utc(ds,tm,tz); jd=jd_from_dt(utc); planets=planet_positions(jd); lag=ascendant(jd,float(lat),float(lon)); li=lag["rashi"]["index"]
    for p in planets.values(): p["house"]=whole_sign_house(p["rashi"]["index"],li)
    return jd,planets,lag,panchanga_details(planets,jd)


def _muhurta_slot_score(purpose, local_dt, rise, sett, planets, lag, pan, natal_nak=None, natal_moon=None, partner_nak=None, partner_moon=None):
    cfg=MUHURTA_PURPOSES.get(purpose,MUHURTA_PURPOSES["ව්‍යාපාර ආරම්භය"])
    score=50; good=[]; caution=[]; avoid=[]
    vara=pan["vara"]; tnum=((pan["tithi_number"]-1)%15)+1
    if vara in cfg["weekdays"]: score+=7; good.append(f"{vara} මෙම කාර්යයට සාම්ප්‍රදායිකව යෝග්‍ය දිනයකි")
    else: caution.append(f"{vara} මෙම කාර්යයට ප්‍රධාන වාරයක් නොවේ")
    if tnum in cfg["tithi"]: score+=8; good.append(f"{pan['tithi']} යෝග්‍ය තිථියකි")
    elif tnum in {4,6,8,9,12,14,15}: score-=8; caution.append(f"{pan['tithi']} සඳහා වැඩි සැලකිල්ලක් යොමු කරයි")
    if pan["nakshatra"] in cfg["nak"]: score+=12; good.append(f"{pan['nakshatra']} නැකත මෙම කාර්යයට හොඳ ලෙස සැලකේ")
    else: caution.append(f"{pan['nakshatra']} නැකත විශේෂ සුභ ලැයිස්තුවට අයත් නොවේ")
    if pan["yoga"] in GOOD_YOGA: score+=6; good.append(f"{pan['yoga']} යෝගය සුභ බලයක් ලබාදේ")
    elif pan["yoga"] in BAD_YOGA: score-=7; caution.append(f"{pan['yoga']} යෝගය නිසා අවධානය අවශ්‍යය")
    if pan["karana"] in BAD_KARANA: score-=6; caution.append(f"{pan['karana']} කරණය ප්‍රධාන සුභ කාර්යයකට දුර්වල ලෙස සැලකේ")
    else: score+=3; good.append(f"{pan['karana']} කරණය පිළිගත හැක")

    tara=_tara_bala(natal_nak,planets["Moon"]["nakshatra"]["index"])
    if tara:
        if tara["good"]: score+=8; good.append(f"තාරා බලය: {tara['name']} — උපන් නැකතට හොඳ ගැලපීමක්")
        elif tara["bad"]: score-=9; caution.append(f"තාරා බලය: {tara['name']} — පුද්ගලික නැකත අනුව අවධානය අවශ්‍යය")
    cb=_chandra_bala(natal_moon,planets["Moon"]["rashi"]["index"])
    if cb:
        if cb["good"]: score+=8; good.append(f"චන්ද්‍ර බලය හොඳයි — උපන් චන්ද්‍රයෙන් {cb['distance']} වන රාශිය")
        if cb["ashtama"]: score-=14; avoid.append("චන්ද්‍රාෂ්ටම තත්ත්වයක් පෙනේ")

    if partner_nak is not None:
        pt=_tara_bala(partner_nak,planets["Moon"]["nakshatra"]["index"])
        if pt and pt["good"]: score+=4; good.append(f"දෙවන පාර්ශවයට තාරා බලය {pt['name']} ලෙස හොඳයි")
        elif pt and pt["bad"]: score-=5; caution.append(f"දෙවන පාර්ශවයට තාරා බලය {pt['name']} ලෙස දුර්වලයි")
    if partner_moon is not None:
        pc=_chandra_bala(partner_moon,planets["Moon"]["rashi"]["index"])
        if pc and pc["good"]: score+=4
        if pc and pc["ashtama"]: score-=7; caution.append("දෙවන පාර්ශවයට චන්ද්‍රාෂ්ටම තත්ත්වයක් පෙනේ")

    rw=_segment_window(rise,sett,RAHU_SEG[vara]); yw=_segment_window(rise,sett,YAMA_SEG[vara]); gw=_segment_window(rise,sett,GULIKA_SEG[vara])
    if _in_window(local_dt,rw): score-=20; avoid.append("රාහු කාලයට වැටේ")
    if _in_window(local_dt,yw): score-=14; avoid.append("යමගණ්ඩ කාලයට වැටේ")
    if _in_window(local_dt,gw): score-=10; caution.append("ගුලික කාලයට වැටේ")

    noon=rise+(sett-rise)/2; abh=(noon-timedelta(minutes=24),noon+timedelta(minutes=24))
    if _in_window(local_dt,abh): score+=6; good.append("අභිජිත් මුහුර්තයට ආසන්න කාලයකි")
    hora=_hora_lord(local_dt,rise,sett,vara)
    if hora in cfg["hora"]: score+=6; good.append(f"{DASHA_SI.get(hora,hora)} හෝරාව මෙම කාර්යයට යෝග්‍යයි")

    # මුහුර්ත ලග්නයේ සාම්ප්‍රදායික සාර පරීක්ෂාව
    benef={"Jupiter","Venus","Mercury"}; malef={"Mars","Saturn","Rahu","Ketu"}
    for k in benef:
        h=planets[k]["house"]
        if h in {1,4,5,7,9,10}: score+=2
    for k in malef:
        h=planets[k]["house"]
        if h in {8,12}: score-=4; caution.append(f"{planets[k]['name']} {h} වන භාවයේ")
    if any(planets[k]["house"]==8 for k in malef): avoid.append("මුහුර්ත ලග්නයේ 8 වන භාවයට පාප ග්‍රහ බලයක් ඇත")

    # ගුරු/ශුක්‍ර අස්ත ආසන්නතාව
    sun=planets["Sun"]["longitude"]
    if _angular_sep(planets["Jupiter"]["longitude"],sun) < 11: score-=7; caution.append("ගුරු සූර්යයාට අතිශයින් ආසන්න බැවින් අස්ත බලපෑම සලකන්න")
    if _angular_sep(planets["Venus"]["longitude"],sun) < 10: score-=7; caution.append("ශුක්‍ර සූර්යයාට අතිශයින් ආසන්න බැවින් අස්ත බලපෑම සලකන්න")

    # ශනි/රාහු/කේතු ගෝචරය උපන් චන්ද්‍රයෙන්
    if natal_moon is not None:
        for key in ("Saturn","Rahu","Ketu"):
            dist=((planets[key]["rashi"]["index"]-int(natal_moon))%12)+1
            if (key=="Saturn" and dist in {1,2,8,12}) or (key in {"Rahu","Ketu"} and dist in {1,5,7,8,12}):
                score-=3; caution.append(f"{planets[key]['name']} ගෝචරය උපන් චන්ද්‍රයෙන් {dist} වන ස්ථානයේ")

    score=max(0,min(100,score))
    label="ඉතා යෝග්‍ය" if score>=82 else ("යෝග්‍ය" if score>=70 else ("මධ්‍යම" if score>=58 else ("අවධානයෙන්" if score>=45 else "වළක්වා ගැනීම හොඳයි")))
    return {"score":score,"label":label,"good":good[:7],"caution":caution[:7],"avoid":avoid[:5],"hora":DASHA_SI.get(hora,hora),"rahu":(_fmt_time(rw[0]),_fmt_time(rw[1])),"yama":(_fmt_time(yw[0]),_fmt_time(yw[1])),"gulika":(_fmt_time(gw[0]),_fmt_time(gw[1])),"abhijit":(_fmt_time(abh[0]),_fmt_time(abh[1]))}


def muhurta_search(data):
    purpose=data.get("purpose") or "විවාහය"; start=data.get("from_date"); end=data.get("to_date")
    lat=float(data.get("latitude",6.9271)); lon=float(data.get("longitude",79.8612)); tz=float(data.get("timezone_offset",5.5))
    a=datetime.strptime(start,"%Y-%m-%d").date(); b=datetime.strptime(end,"%Y-%m-%d").date()
    if b<a: raise ValueError("අවසන් දිනය ආරම්භක දිනයට පෙර විය නොහැක")
    if (b-a).days>45: raise ValueError("එක් වරකට දින 46ක් දක්වා පරීක්ෂා කරන්න")
    nn=data.get("natal_nakshatra_index"); nm=data.get("natal_moon_sign_index"); pn=data.get("partner_nakshatra_index"); pm=data.get("partner_moon_sign_index")
    nn=None if nn in (None,"") else int(nn); nm=None if nm in (None,"") else int(nm); pn=None if pn in (None,"") else int(pn); pm=None if pm in (None,"") else int(pm)
    results=[]
    cur=a
    while cur<=b:
        ds=cur.isoformat(); rise,sett=_sunrise_sunset(ds,lat,lon,tz)
        # දිනකට මිනිත්තු 30 පියවරෙන් හොඳම වේලාව සොයයි
        slot=rise+timedelta(minutes=30); best=None
        while slot <= sett-timedelta(minutes=30):
            tm=slot.strftime("%H:%M")
            try:
                jd,pl,lg,pan=_simple_muhurta_chart(ds,tm,lat,lon,tz)
                sc=_muhurta_slot_score(purpose,slot,rise,sett,pl,lg,pan,nn,nm,pn,pm)
                item={"date":ds,"time":tm,"start":(slot-timedelta(minutes=15)).strftime("%H:%M"),"end":(slot+timedelta(minutes=15)).strftime("%H:%M"),"sunrise":_fmt_time(rise),"sunset":_fmt_time(sett),"vara":pan["vara"],"nakshatra":pan["nakshatra"],"tithi":pan["paksha"]+" • "+pan["tithi"],"yoga":pan["yoga"],"karana":pan["karana"],"moon_sign":pl["Moon"]["rashi"]["name"],"lagna":lg["rashi"]["name"],**sc}
                if best is None or item["score"]>best["score"]: best=item
            except Exception:
                pass
            slot+=timedelta(minutes=30)
        if best: results.append(best)
        cur+=timedelta(days=1)
    results.sort(key=lambda x:(x["score"],x["date"]),reverse=True)
    return {"purpose":purpose,"count":len(results),"results":results[:12],"note":"මෙය පංචාංග, තාරා බල, චන්ද්‍ර බල, රාහු කාල, යමගණ්ඩ, ගුලික, අභිජිත්, හෝරා, මුහුර්ත ලග්නය සහ ප්‍රධාන ගෝචර සලකා සකස් කළ සාම්ප්‍රදායික පෙරහන් කිරීමකි."}



# --- v2.7 calculation audit and correction layer ---
CALC_LOCK = threading.RLock()
_ACTIVE_NODE_MODE = "mean"
AYANAMSA_MODES = {
    "lahiri": (swe.SIDM_LAHIRI, "ලහිරි / චිත්‍ර පක්ෂ"),
    "raman": (swe.SIDM_RAMAN, "බී. වී. රාමන්"),
    "krishnamurti": (swe.SIDM_KRISHNAMURTI, "ක්‍රිෂ්ණමූර්ති"),
}


def _configure_profile(data):
    global _ACTIVE_NODE_MODE
    key = str(data.get("ayanamsa", "lahiri") or "lahiri").lower()
    if key not in AYANAMSA_MODES:
        key = "lahiri"
    swe.set_sid_mode(AYANAMSA_MODES[key][0])
    node = str(data.get("node_mode", "mean") or "mean").lower()
    if node not in {"mean", "true"}:
        node = "mean"
    _ACTIVE_NODE_MODE = node
    return key, node


def planet_positions(jd, node_mode=None):
    node_mode = (node_mode or _ACTIVE_NODE_MODE or "mean").lower()
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    out = {}
    local_planets = {
        "Sun": ("රවි", swe.SUN), "Moon": ("චන්ද්‍ර", swe.MOON), "Mars": ("කුජ", swe.MARS),
        "Mercury": ("බුධ", swe.MERCURY), "Jupiter": ("ගුරු", swe.JUPITER), "Venus": ("ශුක්‍ර", swe.VENUS),
        "Saturn": ("ශනි", swe.SATURN), "Rahu": ("රාහු", swe.TRUE_NODE if node_mode == "true" else swe.MEAN_NODE),
    }
    for key, (si, pid) in local_planets.items():
        data, retflag, serr = calc_ut_compat(jd, pid, flags)
        lon = norm(data[0])
        out[key] = {
            "key": key, "name": si, "longitude": round(lon, 6), "rashi": rashi_info(lon),
            "nakshatra": nak_info(lon), "navamsa": navamsa_info(lon), "retrograde": bool(data[3] < 0),
            "ephemeris_flag": int(retflag), "ephemeris_note": str(serr or "")
        }
    klon = norm(out["Rahu"]["longitude"] + 180)
    out["Ketu"] = {
        "key": "Ketu", "name": "කේතු", "longitude": round(klon, 6), "rashi": rashi_info(klon),
        "nakshatra": nak_info(klon), "navamsa": navamsa_info(klon), "retrograde": True,
        "ephemeris_flag": out["Rahu"].get("ephemeris_flag", 0), "ephemeris_note": out["Rahu"].get("ephemeris_note", "")
    }
    return out


def _angle_diff(a,b):
    return abs(((float(a)-float(b)+180.0)%360.0)-180.0)


def ascendant_with_audit(jd, lat, lon):
    trop_cusps, trop_ascmc = swe.houses_ex(jd, float(lat), float(lon), b'P', 0)
    sid_cusps, sid_ascmc = swe.houses_ex(jd, float(lat), float(lon), b'P', swe.FLG_SIDEREAL)
    tropical = norm(trop_ascmc[0])
    sidereal = norm(sid_ascmc[0])
    ayan = float(swe.get_ayanamsa_ut(jd))
    cross = norm(tropical - ayan)
    delta = _angle_diff(sidereal, cross)
    if delta > 0.05:
        raise RuntimeError(f"ලග්න සත්‍යාපන ගණනය නොගැලපේ ({delta:.4f}°)")
    return {
        "longitude": round(sidereal, 6), "rashi": rashi_info(sidereal), "nakshatra": nak_info(sidereal),
        "navamsa": navamsa_info(sidereal),
    }, {
        "tropical_ascendant": round(tropical, 6), "ayanamsa": round(ayan, 6),
        "sidereal_crosscheck": round(cross, 6), "crosscheck_difference": round(delta, 6)
    }


def dasha_timeline(birth_dt_local, moon_lon):
    n = nak_info(moon_lon)
    lord = n["lord"]
    span = 360/27
    fraction_elapsed = n["inside_degree"] / span
    elapsed_days = DASHA_YEARS[lord] * fraction_elapsed * 365.2425
    current_start = birth_dt_local - timedelta(days=elapsed_days)
    start_lord_index = DASHA_LORDS.index(lord)
    periods=[]; cursor=current_start
    for k in range(12):
        l=DASHA_LORDS[(start_lord_index+k)%9]
        end=cursor+timedelta(days=DASHA_YEARS[l]*365.2425)
        periods.append({
            "lord":l,"name":DASHA_SI[l],"years":DASHA_YEARS[l],
            "start":cursor.date().isoformat(),"end":end.date().isoformat(),
            "start_dt":cursor.isoformat(timespec="minutes"),"end_dt":end.isoformat(timespec="minutes")
        })
        cursor=end
    now=datetime.now()
    current=next((p for p in periods if datetime.fromisoformat(p["start_dt"]) <= now < datetime.fromisoformat(p["end_dt"])),None)
    return {"birth_nakshatra_lord":lord,"periods":periods,"current":current,"moon_fraction_elapsed":round(fraction_elapsed,9)}


def antardasha_for_current(dasha):
    cur=dasha.get("current") if dasha else None
    if not cur or not cur.get("lord"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur.get("start_dt") or cur["start"])
        end=datetime.fromisoformat(cur.get("end_dt") or cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds(); seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]; dur=total*(DASHA_YEARS[lord]/120.0); e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat(),"start_dt":cursor.isoformat(timespec="minutes"),"end_dt":e.isoformat(timespec="minutes")})
        cursor=e
    now=datetime.now()
    current=next((p for p in periods if datetime.fromisoformat(p["start_dt"]) <= now < datetime.fromisoformat(p["end_dt"])),None)
    return {"current":current,"periods":periods}


def pratyantardasha_for_current(dasha):
    ad=antardasha_for_current(dasha); cur=ad.get("current")
    if not cur or not cur.get("lord"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur.get("start_dt") or cur["start"]); end=datetime.fromisoformat(cur.get("end_dt") or cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds(); seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]; dur=total*(DASHA_YEARS[lord]/120.0); e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat(),"start_dt":cursor.isoformat(timespec="minutes"),"end_dt":e.isoformat(timespec="minutes")})
        cursor=e
    now=datetime.now()
    current=next((x for x in periods if datetime.fromisoformat(x["start_dt"]) <= now < datetime.fromisoformat(x["end_dt"])),None)
    return {"current":current,"periods":periods}


def panchanga_details(planets, jd, local_dt=None):
    sun=planets["Sun"]["longitude"]; moon=planets["Moon"]["longitude"]; elong=norm(moon-sun)
    tithi_num=int(elong//12)+1; paksha="ශුක්ල පක්ෂය" if tithi_num<=15 else "කෘෂ්ණ පක්ෂය"; paksha_tithi=tithi_num if tithi_num<=15 else tithi_num-15
    tithi_label=("පුර පසළොස්වක" if tithi_num==15 else "අමාවක") if paksha_tithi==15 else f"{paksha_tithi} වන තිථිය"
    yoga_index=int(norm(sun+moon)//(360/27)); half_index=int(elong//6)+1
    if half_index==1: karana="කිංස්තුඝ්න"
    elif 2<=half_index<=57: karana=KARANA_MOVABLE[(half_index-2)%7]
    elif half_index==58: karana="ශකුණි"
    elif half_index==59: karana="චතුෂ්පාද"
    else: karana="නාග"
    weekday_names=["සඳුදා","අඟහරුවාදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා","සෙනසුරාදා","ඉරිදා"]
    if local_dt is not None:
        vara=weekday_names[local_dt.weekday()]
    else:
        # fallback from UT Julian day only
        vara=["ඉරිදා","සඳුදා","අඟහරුවාදා","බදාදා","බ්‍රහස්පතින්දා","සිකුරාදා","සෙනසුරාදා"][int((jd+1.5)%7)]
    return {"vara":vara,"tithi_number":tithi_num,"paksha":paksha,"tithi":tithi_label,"nakshatra":planets["Moon"]["nakshatra"]["name"],"pada":planets["Moon"]["nakshatra"]["pada"],"yoga":YOGA_NAMES[yoga_index],"karana":karana,"ayanamsa":round(float(swe.get_ayanamsa_ut(jd)),6),"julian_day":round(jd,6)}


def _standard_time_equivalent(data, tz_used):
    try:
        local_dt=datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
    except Exception:
        return None
    if is_sri_lanka_coords(data.get("latitude",0),data.get("longitude",0)) and abs(float(tz_used)-5.5)>1e-9:
        eq=local_dt-timedelta(hours=(float(tz_used)-5.5))
        return eq.strftime("%Y-%m-%d %H:%M")
    return None


def advanced_jyotishya(planets, lagna, dasha, jd, local_dt=None):
    go=current_gochara(planets["Moon"]["rashi"]["index"], lagna["rashi"]["index"])
    return {
        "panchanga":panchanga_details(planets,jd,local_dt), "vargas":divisional_charts(planets,lagna), "drishti":graha_drishti(planets),
        "dignity":dignity_summary(planets), "planet_strength":planetary_strength_reference(planets), "ashtakavarga":ashtakavarga(planets,lagna),
        "yoga_dosha":yoga_dosha_checks(planets,lagna), "antardasha":antardasha_for_current(dasha), "pratyantardasha":pratyantardasha_for_current(dasha),
        "gochara":go, "malefic_analysis":malefic_analysis(planets,lagna,dasha,go), "hela_factors":hela_traditional_factors(planets,lagna),
        "methods":["ලහිරි/තෝරාගත් නිරයන අයනංශය","නිරයන ග්‍රහ ස්ඵුට","පංචාංග ගණිතය","විම්ශෝත්තරී දශා නිවැරදි කාල සීමා","සාම්ප්‍රදායික ග්‍රහ දෘෂ්ටි","වර්ග කේන්දර","බින්න අෂ්ටකවර්ග / සර්වාෂ්ටකවර්ග","ගෝචර පරීක්ෂාව"]
    }


def calculate_birth(data):
    with CALC_LOCK:
        ay_key,node_mode=_configure_profile(data)
        tz_used,tz_source=effective_timezone_offset(data)
        data=dict(data); data["timezone_offset"]=tz_used; data["timezone_source"]=tz_source; data["ayanamsa"]=ay_key; data["node_mode"]=node_mode
        utc=local_to_utc(data["birth_date"],data["birth_time"],tz_used); jd=jd_from_dt(utc)
        planets=planet_positions(jd,node_mode=node_mode)
        lag,audit=ascendant_with_audit(jd,data.get("latitude",6.9271),data.get("longitude",79.8612))
        lag_i=lag["rashi"]["index"]
        for p in planets.values(): p["house"]=whole_sign_house(p["rashi"]["index"],lag_i)
        local_birth=datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
        dasha=dasha_timeline(local_birth,planets["Moon"]["longitude"])
        reading=detailed_reading(lag,planets,dasha)
        advanced=advanced_jyotishya(planets,lag,dasha,jd,local_birth)
        known=data.get("known_lagna")
        verification=None
        if known not in (None,""):
            try:
                known_i=int(known)%12; verification={"known":RASHI[known_i],"calculated":lag["rashi"]["name"],"match":known_i==lag_i}
            except Exception: pass
        diag={**audit,
            "utc_datetime":utc.isoformat(timespec="minutes"),"julian_day":round(jd,8),"timezone_used":tz_used,"timezone_source":tz_source,
            "standard_time_0530_equivalent":_standard_time_equivalent(data,tz_used),"ayanamsa_key":ay_key,"ayanamsa_name":AYANAMSA_MODES[ay_key][1],
            "node_mode":"සත්‍ය රාහු/කේතු" if node_mode=="true" else "මධ්‍ය රාහු/කේතු","house_method":"සම්පූර්ණ රාශි භාව","verification":verification,
            "warning":"ලග්නය මිනිත්තු කිහිපයකින් වෙනස් විය හැකි බැවින් නිවැරදි උපන් වෙලාව සහ නිවැරදි උපන් ස්ථානය අත්‍යවශ්‍යය."
        }
        return {"mode":"calculated","person":data,"lagna":lag,"moon_sign":planets["Moon"]["rashi"],"birth_nakshatra":planets["Moon"]["nakshatra"],"planets":planets,
            "rashi_chart":fixed_sign_chart(planets,lag,"rashi"),"navamsa_chart":fixed_sign_chart(planets,lag,"navamsa"),"houses":house_summary(planets,lag_i),"dasha":dasha,
            "reading":reading,"advanced":advanced,"calculation_audit":diag,"generated_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "disclaimer":"මෙය සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය ගණනය/විග්‍රහයකි. විද්‍යාත්මකව අනාගතය තහවුරු කරන ක්‍රමයක් නොවේ."}



# --- v2.8 deterministic Sri Lanka standard calculation layer ---
CALC_PROFILE_ID = "SL-LAHIRI-MEAN-WHOLE-1"
CALC_PROFILE_NAME = "ශ්‍රී ලංකා ස්ථාවර නිරයන ගණිත ක්‍රමය"


def _configure_profile(data):
    """Lock all natal calculations to one versioned profile.

    This prevents the same birth data from changing because a user or another
    request switched ayanamsa/node settings. Alternative methods belong only
    in diagnostics, never in the canonical chart.
    """
    global _ACTIVE_NODE_MODE
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    _ACTIVE_NODE_MODE = "mean"
    return "lahiri", "mean"


def _analysis_datetime(data):
    raw = str(data.get("analysis_date") or "").strip()
    try:
        if raw:
            return datetime.strptime(raw, "%Y-%m-%d").replace(hour=12, minute=0)
    except Exception:
        pass
    return datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)


def dasha_timeline(birth_dt_local, moon_lon, as_of=None):
    n = nak_info(moon_lon)
    lord = n["lord"]
    span = 360/27
    fraction_elapsed = n["inside_degree"] / span
    elapsed_days = DASHA_YEARS[lord] * fraction_elapsed * 365.2425
    current_start = birth_dt_local - timedelta(days=elapsed_days)
    start_lord_index = DASHA_LORDS.index(lord)
    periods=[]; cursor=current_start
    for k in range(12):
        l=DASHA_LORDS[(start_lord_index+k)%9]
        end=cursor+timedelta(days=DASHA_YEARS[l]*365.2425)
        periods.append({
            "lord":l,"name":DASHA_SI[l],"years":DASHA_YEARS[l],
            "start":cursor.date().isoformat(),"end":end.date().isoformat(),
            "start_dt":cursor.isoformat(timespec="minutes"),"end_dt":end.isoformat(timespec="minutes")
        })
        cursor=end
    check = as_of or datetime.now()
    current=next((p for p in periods if datetime.fromisoformat(p["start_dt"]) <= check < datetime.fromisoformat(p["end_dt"])),None)
    return {"birth_nakshatra_lord":lord,"periods":periods,"current":current,"moon_fraction_elapsed":round(fraction_elapsed,9),"as_of_dt":check.isoformat(timespec="minutes")}


def _dasha_reference_time(dasha):
    raw=(dasha or {}).get("as_of_dt")
    try:
        return datetime.fromisoformat(raw) if raw else datetime.now()
    except Exception:
        return datetime.now()


def antardasha_for_current(dasha):
    cur=dasha.get("current") if dasha else None
    if not cur or not cur.get("lord"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur.get("start_dt") or cur["start"]); end=datetime.fromisoformat(cur.get("end_dt") or cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds(); seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]; dur=total*(DASHA_YEARS[lord]/120.0); e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat(),"start_dt":cursor.isoformat(timespec="minutes"),"end_dt":e.isoformat(timespec="minutes")})
        cursor=e
    check=_dasha_reference_time(dasha)
    current=next((p for p in periods if datetime.fromisoformat(p["start_dt"]) <= check < datetime.fromisoformat(p["end_dt"])),None)
    return {"current":current,"periods":periods}


def pratyantardasha_for_current(dasha):
    ad=antardasha_for_current(dasha); cur=ad.get("current")
    if not cur or not cur.get("lord"):
        return {"current":None,"periods":[]}
    try:
        start=datetime.fromisoformat(cur.get("start_dt") or cur["start"]); end=datetime.fromisoformat(cur.get("end_dt") or cur["end"])
    except Exception:
        return {"current":None,"periods":[]}
    total=(end-start).total_seconds(); seq_start=DASHA_LORDS.index(cur["lord"])
    periods=[]; cursor=start
    for i in range(9):
        lord=DASHA_LORDS[(seq_start+i)%9]; dur=total*(DASHA_YEARS[lord]/120.0); e=cursor+timedelta(seconds=dur)
        periods.append({"lord":lord,"name":DASHA_SI[lord],"start":cursor.date().isoformat(),"end":e.date().isoformat(),"start_dt":cursor.isoformat(timespec="minutes"),"end_dt":e.isoformat(timespec="minutes")})
        cursor=e
    check=_dasha_reference_time(dasha)
    current=next((x for x in periods if datetime.fromisoformat(x["start_dt"]) <= check < datetime.fromisoformat(x["end_dt"])),None)
    return {"current":current,"periods":periods}


def current_gochara(natal_moon_sign, natal_lagna_sign, as_of=None):
    local_noon = as_of or datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
    # Sri Lanka current civil offset is UTC+5:30. Use a visible, fixed daily reference time.
    utc = local_noon - timedelta(hours=5.5)
    jd=jd_from_dt(utc)
    trans=planet_positions(jd, node_mode="mean")
    rows=[]
    for key in ["Jupiter","Saturn","Rahu","Ketu","Mars","Venus","Mercury"]:
        p=trans[key]; si=p["rashi"]["index"]
        from_moon=((si-natal_moon_sign)%12)+1
        from_lagna=((si-natal_lagna_sign)%12)+1
        rows.append({"planet":p["name"],"key":key,"sign":p["rashi"]["name"],"from_moon":from_moon,"from_lagna":from_lagna,"retrograde":p.get("retrograde",False)})
    sat=next(x for x in rows if x["key"]=="Saturn")
    notes=[]
    if sat["from_moon"] in {12,1,2}: notes.append("චන්ද්‍ර රාශිය අනුව ඒරාෂ්ටක කාල පරාසයට අයත් ශනි ගෝචරයක් පවතී.")
    if sat["from_moon"]==8: notes.append("චන්ද්‍ර රාශියෙන් අටවන ස්ථානයේ ශනි ගෝචරය පවතින බැවින් අෂ්ටම ශනි බලපෑම සලකා බලයි.")
    if sat["from_lagna"]==8: notes.append("ලග්නයෙන් අටවන ස්ථානයේ ශනි ගෝචරය පවතී; වගකීම්, ප්‍රමාද සහ නැවත සැලසුම් කිරීම සම්බන්ධ කරුණු වැඩි විය හැක.")
    if not notes:
        notes.append("මෙම ගණනය අනුව ප්‍රධාන ශනි අපල තත්ත්වයක් හඳුනාගෙන නොමැත.")
        notes.append("ශනිගේ රාශි පිහිටීම, භාවය, දෘෂ්ටි, දශා සහ තෝරාගත් ගෝචර දිනය එකට සලකා මෙම සාරාංශය ලබාදී ඇත.")
    return {"as_of":local_noon.date().isoformat(),"rows":rows,"flags":notes}


def advanced_jyotishya(planets, lagna, dasha, jd, local_dt=None, analysis_dt=None):
    go=current_gochara(planets["Moon"]["rashi"]["index"], lagna["rashi"]["index"], analysis_dt)
    return {
        "panchanga":panchanga_details(planets,jd,local_dt), "vargas":divisional_charts(planets,lagna), "drishti":graha_drishti(planets),
        "dignity":dignity_summary(planets), "planet_strength":planetary_strength_reference(planets), "ashtakavarga":ashtakavarga(planets,lagna),
        "yoga_dosha":yoga_dosha_checks(planets,lagna), "antardasha":antardasha_for_current(dasha), "pratyantardasha":pratyantardasha_for_current(dasha),
        "gochara":go, "malefic_analysis":malefic_analysis(planets,lagna,dasha,go), "hela_factors":hela_traditional_factors(planets,lagna),
        "methods":["ලහිරි නිරයන අයනංශය","මධ්‍ය රාහු / කේතු","සම්පූර්ණ රාශි භාව","නිරයන ග්‍රහ ස්ඵුට","පංචාංග ගණිතය","විම්ශෝත්තරී දශා","සාම්ප්‍රදායික ග්‍රහ දෘෂ්ටි","වර්ග කේන්දර","බින්න අෂ්ටකවර්ග / සර්වාෂ්ටකවර්ග","තෝරාගත් දිනයේ ගෝචරය"]
    }


def _natal_signature(data, lag, planets, jd, tz_used):
    body={
        "profile":CALC_PROFILE_ID,"birth_date":data.get("birth_date"),"birth_time":data.get("birth_time"),
        "lat":round(float(data.get("latitude",0)),6),"lon":round(float(data.get("longitude",0)),6),"tz":float(tz_used),"jd":round(float(jd),8),
        "asc":round(float(lag["longitude"]),6),"planets":{k:round(float(planets[k]["longitude"]),6) for k in sorted(planets)}
    }
    raw=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16].upper()


def _lagna_window_diagnostic(data, known_i, tz_used):
    try:
        base=datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
    except Exception:
        return None
    hits=[]
    for minutes in range(-180,181,5):
        local=base+timedelta(minutes=minutes); utc=local-timedelta(hours=float(tz_used)); jd=jd_from_dt(utc)
        lag,_=ascendant_with_audit(jd,float(data.get("latitude",0)),float(data.get("longitude",0)))
        if lag["rashi"]["index"]==known_i: hits.append((minutes,local.strftime("%H:%M")))
    if not hits: return {"match_window":None,"note":"උපන් වෙලාවට පැය 3ක ඉදිරිය/පසු පරාසය තුළ දන්නා ලග්නය නොලැබුණි."}
    return {"match_window":f"{hits[0][1]} – {hits[-1][1]}","offset_minutes_from_entered":[hits[0][0],hits[-1][0]],"note":"මෙය දෝෂ නිර්ණය සඳහා පමණි; උපන් වෙලාව ස්වයංක්‍රීයව වෙනස් නොකරයි."}


def calculate_birth(data):
    with CALC_LOCK:
        # Canonical profile is deliberately locked for repeatability.
        ay_key,node_mode=_configure_profile(data)
        tz_used,tz_source=effective_timezone_offset(data)
        data=dict(data)
        data["timezone_offset"]=tz_used; data["timezone_source"]=tz_source
        data["ayanamsa"]="lahiri"; data["node_mode"]="mean"; data["calculation_profile"]=CALC_PROFILE_ID
        analysis_dt=_analysis_datetime(data); data["analysis_date"]=analysis_dt.date().isoformat()
        utc=local_to_utc(data["birth_date"],data["birth_time"],tz_used); jd=jd_from_dt(utc)
        planets=planet_positions(jd,node_mode="mean")
        lag,audit=ascendant_with_audit(jd,data.get("latitude",6.9271),data.get("longitude",79.8612))
        lag_i=lag["rashi"]["index"]
        for p in planets.values(): p["house"]=whole_sign_house(p["rashi"]["index"],lag_i)
        local_birth=datetime.strptime(f"{data['birth_date']} {data['birth_time']}", "%Y-%m-%d %H:%M")
        dasha=dasha_timeline(local_birth,planets["Moon"]["longitude"],analysis_dt)
        reading=detailed_reading(lag,planets,dasha)
        advanced=advanced_jyotishya(planets,lag,dasha,jd,local_birth,analysis_dt)
        known=data.get("known_lagna"); verification=None; lagna_diag=None
        if known not in (None,""):
            try:
                known_i=int(known)%12
                verification={"known":RASHI[known_i],"calculated":lag["rashi"]["name"],"match":known_i==lag_i}
                if known_i!=lag_i: lagna_diag=_lagna_window_diagnostic(data,known_i,tz_used)
            except Exception: pass
        signature=_natal_signature(data,lag,planets,jd,tz_used)
        diag={**audit,
            "utc_datetime":utc.isoformat(timespec="minutes"),"julian_day":round(jd,8),"timezone_used":tz_used,"timezone_source":tz_source,
            "standard_time_0530_equivalent":_standard_time_equivalent(data,tz_used),"ayanamsa_key":"lahiri","ayanamsa_name":"ලහිරි / චිත්‍ර පක්ෂ",
            "node_mode":"මධ්‍ය රාහු / කේතු","house_method":"සම්පූර්ණ රාශි භාව","verification":verification,"lagna_time_diagnostic":lagna_diag,
            "calculation_profile":CALC_PROFILE_ID,"calculation_profile_name":CALC_PROFILE_NAME,"natal_signature":signature,
            "analysis_date":analysis_dt.date().isoformat(),
            "warning":"ජන්ම ගණනය ස්ථාවර ගණිත පැතිකඩකට අගුළු දමා ඇත. එකම උපන් දත්ත දුන්නොත් ජන්ම ලග්නය සහ ග්‍රහ ස්ඵුට එකම අගයන් ලැබිය යුතුය. ගෝචර/වත්මන් දශා පමණක් තෝරාගත් විග්‍රහ දිනය අනුව වෙනස් වේ."
        }
        return {"mode":"calculated","person":data,"lagna":lag,"moon_sign":planets["Moon"]["rashi"],"birth_nakshatra":planets["Moon"]["nakshatra"],"planets":planets,
            "rashi_chart":fixed_sign_chart(planets,lag,"rashi"),"navamsa_chart":fixed_sign_chart(planets,lag,"navamsa"),"houses":house_summary(planets,lag_i),"dasha":dasha,
            "reading":reading,"advanced":advanced,"calculation_audit":diag,"generated_at":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "disclaimer":"මෙය සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය ගණනය/විග්‍රහයකි. විද්‍යාත්මකව අනාගතය තහවුරු කරන ක්‍රමයක් නොවේ."}

def self_test():
    sample={"name":"Self Test","birth_date":"1997-03-18","birth_time":"10:20","birth_place":"Hambantota","latitude":6.1241,"longitude":81.1185,"timezone_offset":5.5,"analysis_date":"2026-09-14","known_lagna":"1"}
    r1=calculate_birth(validate_birth(dict(sample)))
    r2=calculate_birth(validate_birth(dict(sample)))
    assert r1["person"]["timezone_offset"] == 6.0
    assert r1["lagna"]["rashi"]["name"] == "වෘෂභ"
    assert r1["calculation_audit"]["crosscheck_difference"] < 0.05
    assert r1["calculation_audit"]["standard_time_0530_equivalent"].endswith("09:50")
    assert r1["advanced"]["panchanga"]["vara"] == "අඟහරුවාදා"
    assert r1["calculation_audit"]["natal_signature"] == r2["calculation_audit"]["natal_signature"]
    assert r1["lagna"]["longitude"] == r2["lagna"]["longitude"]
    for k in r1["planets"]:
        assert r1["planets"][k]["longitude"] == r2["planets"][k]["longitude"]
    match=porondam(r1,r1); assert len(match["factors"])>=10
    return True



# --- V4.0 Accuracy / database / update center ---
def localdb_integrity(repair=False):
    with DB_LOCK:
        con=_db_connect()
        try:
            row=con.execute("PRAGMA integrity_check").fetchone()
            result=str(row[0] if row else "unknown")
            if repair and result.lower()=="ok":
                con.execute("PRAGMA optimize")
                con.commit()
            return {"ok":result.lower()=="ok","result":result,"optimized":bool(repair and result.lower()=="ok"),**localdb_info()}
        finally:
            con.close()

def calculation_accuracy(data):
    clean=validate_birth(dict(data or {}))
    # Run the locked natal calculation twice without consuming trial quota.
    a=calculate_birth(dict(clean)); b=calculate_birth(dict(clean))
    pa=a.get("planets",{}); pb=b.get("planets",{})
    rows=[]; same=True
    for k in PLANET_ORDER:
        if k not in pa or k not in pb: continue
        x=float(pa[k]["longitude"]); y=float(pb[k]["longitude"]); diff=abs(x-y)
        rows.append({"planet":pa[k].get("name",k),"longitude":round(x,6),"repeat_longitude":round(y,6),"difference":round(diff,8),"same":diff<1e-9})
        same = same and diff < 1e-9
    la=float(a["lagna"]["longitude"]); lb=float(b["lagna"]["longitude"]); ldiff=abs(la-lb)
    same = same and ldiff < 1e-9 and a.get("calculation_audit",{}).get("natal_signature")==b.get("calculation_audit",{}).get("natal_signature")
    audit=a.get("calculation_audit",{})
    return {
      "ok":True,"deterministic":same,"profile":audit.get("calculation_profile_name"),
      "natal_signature":audit.get("natal_signature"),"timezone_used":audit.get("timezone_used"),
      "timezone_source":audit.get("timezone_source"),"utc_datetime":audit.get("utc_datetime"),
      "julian_day":audit.get("julian_day"),"ayanamsa":audit.get("ayanamsa_name"),
      "node_mode":audit.get("node_mode"),"house_method":audit.get("house_method"),
      "ascendant":{"name":a["lagna"]["rashi"]["name"],"longitude":round(la,6),"repeat_longitude":round(lb,6),"difference":round(ldiff,8),"same":ldiff<1e-9},
      "moon":{"sign":a["moon_sign"]["name"],"nakshatra":a["birth_nakshatra"]["name"],"pada":a["birth_nakshatra"]["pada"]},
      "crosscheck_difference":audit.get("crosscheck_difference"),"rows":rows,
      "warning":"මෙය ගණිත ස්ථාවරත්වය සහ භාවිත කරන ගණිත පැතිකඩ පරීක්ෂා කරයි. අර්ථකථන සම්ප්‍රදාය අනුව වෙනස් විය හැක."
    }

def app_meta():
    return {"ok":True,"app":APP_NAME,"version":APP_VERSION,"publisher":PUBLISHER,"whatsapp":SUPPORT_WHATSAPP,"database":localdb_info()}

def check_for_update():
    # Release manifest is optional. Example JSON: {"version":"4.1","download_url":"https://...","notes":"..."}
    cfg_path=BASE.parent / "commercial_config.json"
    try: cfg=json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception: cfg={}
    url=str(cfg.get("release_manifest_url") or "").strip()
    if not url:
        return {"ok":True,"configured":False,"current":APP_VERSION,"message":"යාවත්කාලීන සබැඳිය තව සකසා නැත."}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"HelaJyotishya/4.0"})
        with urllib.request.urlopen(req,timeout=8) as r:
            data=json.loads(r.read().decode("utf-8","replace"))
        return {"ok":True,"configured":True,"current":APP_VERSION,"latest":data.get("version"),"download_url":data.get("download_url"),"notes":data.get("notes","")}
    except Exception as e:
        return {"ok":False,"configured":True,"current":APP_VERSION,"message":str(e)}

class Handler(BaseHTTPRequestHandler):
    server_version = f"{APP_NAME}/{APP_VERSION}"

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args), flush=True)

    def send_json(self, obj, status=200):
        b = jbytes(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def send_file(self, p):
        p = p.resolve()
        if BASE.resolve() not in p.parents and p != BASE.resolve():
            self.send_error(403)
            return
        if not p.is_file():
            self.send_error(404)
            return
        b = p.read_bytes()
        c = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", c + ("; charset=utf-8" if c.startswith("text/") or c in ("application/javascript", "application/json") else ""))
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self.send_json({"ok": True, "app": APP_NAME, "version": APP_VERSION})
        if path == "/api/commercial/status":
            return self.send_json(commercial_state())
        if path == "/api/app/meta":
            return self.send_json(app_meta())
        if path == "/api/update/check":
            return self.send_json(check_for_update())
        if path == "/api/localdb/state":
            return self.send_json({"ok": True, "state": localdb_get_all(), "info": localdb_info()})
        if path == "/api/localdb/info":
            return self.send_json({"ok": True, **localdb_info()})
        if path == "/":
            return self.send_file(BASE / "static" / "index.html")
        if path.startswith("/static/"):
            rel = path[len("/static/"):].lstrip("/")
            return self.send_file(BASE / "static" / rel)
        self.send_error(404)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n <= 0 or n > 2_000_000:
                raise ValueError("Invalid request size")
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            path = urlparse(self.path).path
            if path == "/api/localdb/set":
                localdb_set(data.get("key"), data.get("value"))
                return self.send_json({"ok": True, "info": localdb_info()})
            if path == "/api/localdb/delete":
                localdb_delete(data.get("key"))
                return self.send_json({"ok": True, "info": localdb_info()})
            if path == "/api/localdb/restore":
                localdb_restore(data.get("state") or {})
                return self.send_json({"ok": True, "info": localdb_info()})
            if path == "/api/localdb/integrity":
                return self.send_json(localdb_integrity(bool(data.get("repair"))))
            if path == "/api/accuracy":
                return self.send_json(calculation_accuracy(data))
            if path == "/api/calculate":
                _trial_consume()
                return self.send_json(calculate_birth(validate_birth(data)))
            if path == "/api/analyze_reference":
                return self.send_json(analyze_reference(data))
            if path == "/api/autofill_reference":
                _trial_consume()
                birth = validate_birth(dict(data.get("birth") or {}))
                anchors = dict(data.get("anchors") or {})
                ref = auto_reference_from_birth(birth, anchors)
                return self.send_json({"reference": ref, "analysis": analyze_reference(ref), "calculated": calculate_birth(birth)})
            if path == "/api/porondam":
                if ACCESS_MODE == "trial":
                    return self.send_json({"error": f"පොරොන්දම් සම්පූර්ණ විග්‍රහය ගෙවූ සංස්කරණයට පමණි. PHKS Creation WhatsApp {SUPPORT_WHATSAPP}"}, 402)
                g = calculate_birth(validate_birth(dict(data.get("groom") or {})))
                b = calculate_birth(validate_birth(dict(data.get("bride") or {})))
                return self.send_json(porondam(g, b))
            if path == "/api/muhurta":
                if ACCESS_MODE == "trial":
                    return self.send_json({"error": f"මුහුර්ත හා සුභ කාල ගණනය ගෙවූ සංස්කරණයට පමණි. PHKS Creation WhatsApp {SUPPORT_WHATSAPP}"}, 402)
                return self.send_json(muhurta_search(data))
            self.send_error(404)
        except Exception as e:
            traceback.print_exc()
            self.send_json({"error": str(e)}, 400)


# --- v3.0 chart-specific reading + timing layer ---
VIMSHOTTARI_YEAR_DAYS = 365.25


def dasha_timeline(birth_dt_local, moon_lon, as_of=None):
    n=nak_info(moon_lon); lord=n['lord']; span=360/27
    elapsed_fraction=n['inside_degree']/span
    current_start=birth_dt_local-timedelta(days=DASHA_YEARS[lord]*elapsed_fraction*VIMSHOTTARI_YEAR_DAYS)
    idx=DASHA_LORDS.index(lord); periods=[]; cursor=current_start
    for k in range(12):
        l=DASHA_LORDS[(idx+k)%9]; end=cursor+timedelta(days=DASHA_YEARS[l]*VIMSHOTTARI_YEAR_DAYS)
        periods.append({'lord':l,'name':DASHA_SI[l],'years':DASHA_YEARS[l],'start':cursor.date().isoformat(),'end':end.date().isoformat(),'start_dt':cursor.isoformat(timespec='minutes'),'end_dt':end.isoformat(timespec='minutes')})
        cursor=end
    check=as_of or datetime.now()
    cur=next((p for p in periods if datetime.fromisoformat(p['start_dt'])<=check<datetime.fromisoformat(p['end_dt'])),None)
    return {'birth_nakshatra_lord':lord,'periods':periods,'current':cur,'moon_fraction_elapsed':round(elapsed_fraction,9),'as_of_dt':check.isoformat(timespec='minutes'),'year_days':VIMSHOTTARI_YEAR_DAYS}


def _chart_seed(lagna, planets):
    s=lagna['rashi']['index']*97
    for i,k in enumerate(sorted(planets)):
        p=planets[k]; s += (i+3)*int(round(p['longitude']*1000)) + p.get('house',0)*31
    return abs(s)


def _pick(options, seed, salt):
    return options[(seed + salt*131) % len(options)]


def _planet_phrase(p, dmap):
    return f"{p['name']} {p.get('house')} වන භාවයේ {p['rashi']['name']} රාශියේ {_planet_state_text(p['name'],dmap)} තත්ත්වයේ"


def _timing_windows(planets, lagna, dasha):
    md=dasha.get('current') or {}; ad=antardasha_for_current(dasha).get('current') or {}; pd=pratyantardasha_for_current(dasha).get('current') or {}
    rows=[]
    def add(label, item, weight):
        if not item: return
        lord=item.get('lord'); p=planets.get(lord)
        if not p: return
        houses={p.get('house')}
        themes=[]
        if houses & {10,11,6}: themes.append('රැකියාව හා ආදායම')
        if houses & {7,2}: themes.append('විවාහය හා සබඳතා')
        if houses & {9,12}: themes.append('විදේශ හා දුර ගමන්')
        if houses & {4}: themes.append('නිවස හා දේපළ')
        if houses & {5}: themes.append('අධ්‍යාපනය, නිර්මාණශීලීත්වය හා දරුවන්')
        if houses & {8,12,6}: themes.append('වියදම්, බාධා හා නැවත සැලසුම් කිරීම')
        if not themes: themes.append(HOUSE_MEANINGS.get(p.get('house'),'ජීවිතයේ අදාළ අංශ'))
        rows.append({'level':label,'lord':p['name'],'start':item.get('start'),'end':item.get('end'),'theme':' / '.join(themes),'weight':weight})
    add('මහා දශාව',md,3); add('අතුරු දශාව',ad,2); add('ප්‍රත්‍යන්තර දශාව',pd,1)
    return rows


def expanded_reading(lagna, planets, dasha, reference=False):
    lag_i=lagna['rashi']['index']; aspects=_aspect_map(planets,lag_i); dmap=_dignity_map(planets); seed=_chart_seed(lagna,planets)
    moon=planets['Moon']; nak=moon['nakshatra']; laglord=planets[RASHI_LORD[lag_i]]
    md=dasha.get('current') or {}; ad=antardasha_for_current(dasha).get('current') or {}; pd=pratyantardasha_for_current(dasha).get('current') or {}
    summary=[
      f"{lagna['rashi']['name']} ලග්නයේ අධිපති {laglord['name']} {laglord.get('house')} වන භාවයේ පිහිටා ඇති නිසා මෙම කේන්දරයේ මුල් ජීවිත රටාව {HOUSE_MEANINGS.get(laglord.get('house'),'එම භාවයේ කරුණු')} වටා ගොඩනැඟේ.",
      f"චන්ද්‍රයා {moon['rashi']['name']} රාශියේ {nak['name']} නැකතේ {nak.get('pada')} පාදයේය. මනස සහ ප්‍රතිචාර රටාවට {NAK_TRAITS[nak['index']]} ගුණය වැඩිපුර පෙනේ.",
    ]
    if md:
        summary.append(f"දැනට {md['name']} මහා දශාව ක්‍රියාත්මකයි. එය {md.get('start')} සිට {md.get('end')} දක්වා පවතින අතර, එම ග්‍රහයාගේ ජන්ම භාවය මේ කාලයේ මූලික ජීවිත තේමාව තීරණය කරයි.")
    if ad:
        summary.append(f"මේ මහා දශාව ඇතුළත {ad['name']} අතුරු දශාව ක්‍රියාත්මක වන නිසා, මහා දශාවේ පුළුල් තේමාවට {HOUSE_MEANINGS.get(planets[ad['lord']].get('house'),'අදාළ කරුණු')} කෙටි කාලීනව එකතු වේ.")

    section_specs=[
      ('1. පුද්ගලත්වය සහ ජීවිත දිශාව',[1],['ස්වාධීන තීරණ','වගකීම් භාරගැනීම','අභ්‍යන්තර ස්ථාවරත්වය']),
      ('2. මනස සහ හැඟීම්',[1,4],['සිතේ වේගය','අතීත අත්දැකීම්වල බලපෑම','පවුල් පරිසරයට සංවේදී බව']),
      ('3. මුදල් සහ පවුල් වගකීම්',[2,11],['ඉතිරි කිරීම','ආදායම් මාර්ග','පවුල් සඳහා වියදම්']),
      ('4. අධ්‍යාපනය සහ කුසලතා',[4,5,9],['තාක්ෂණික දැනුම','භාෂා/ලිවීම','උසස් අධ්‍යාපනය']),
      ('5. රැකියාව සහ වෘත්තීය මාර්ගය',[6,10,11],['තනතුරු වෙනස්කම්','ස්ථාවර වෘත්තිය','අමතර ආදායම්']),
      ('6. ව්‍යාපාර සහ හවුල්කාරීත්වය',[3,7,10,11],['හවුල් ව්‍යාපාර','ගිවිසුම්','ස්වයං රැකියාව']),
      ('7. විවාහය සහ සබඳතා',[2,7,8,11],['දිගුකාලීන බැඳීම','සන්නිවේදනය','පවුල් දෙපාර්ශවය']),
      ('8. විදේශ ගමන් සහ පදිංචි වෙනස්කම්',[9,12],['විදේශ අවස්ථා','දිගු ගමන්','පදිංචි මාරු']),
      ('9. නිවස, ඉඩම් සහ වාහන',[4,8,11],['නිවසක් ලබාගැනීම','ඉඩම්/දේපළ','වාහන']),
      ('10. දරුවන් සහ නිර්මාණශීලීත්වය',[5,9],['දරුවන්','නිර්මාණ කුසලතා','ඉගෙනීම ඉගැන්වීම']),
      ('11. අභියෝග සහ නැවත ගොඩනැගීම',[6,8,12],['ණය/වියදම් පාලනය','අනපේක්ෂිත වෙනස්කම්','මානසික පීඩනය පාලනය']),
      ('12. ගෞරවය සහ සමාජ වර්ධනය',[9,10,11],['ප්‍රසිද්ධිය','වෘත්තීය ජාලය','ගුරුවරුන්ගේ සහය']),
    ]
    sections=[]
    for idx,(title,houses,focus) in enumerate(section_specs):
        ev=[]; good=[]; caution=[]
        for h in houses:
            ev.append(_house_evidence(h,lag_i,planets,aspects,dmap))
            p,c=_section_judgement([h],lag_i,planets,aspects,dmap,md.get('lord'))
            good.extend(p); caution.extend(c)
        good=list(dict.fromkeys(good)); caution=list(dict.fromkeys(caution))
        intro=_pick([
          f"මෙම අංශයේ ප්‍රධාන අවධානය {', '.join(focus)} වෙත යොමු වේ.",
          f"මෙහි ප්‍රතිඵල තීරණය කරන්නේ {', '.join(focus)} සම්බන්ධ භාව අධිපති සහ එම භාවවල ග්‍රහ පිහිටීම්ය.",
          f"මෙම කේන්දරයේ {', '.join(focus)} එකම රටාවකට නොව ග්‍රහ සම්බන්ධතා අනුව මිශ්‍රව පෙනේ."
        ],seed,idx)
        body=' '.join(ev)+' '+intro
        if good: body += ' ශක්තිමත් පැත්ත: ' + '; '.join(good[:3]) + '.'
        if caution:
            body += ' දුර්වල/පීඩන පැත්ත: ' + '; '.join(caution[:3]) + '.'
            effects=[
              'ආත්මවිශ්වාසය හෝ තීරණ ගැනීමේදී දෙගිඩියාව, වැඩි වගකීම් හෝ ප්‍රමාද අත්විඳිය හැකි ප්‍රවණතාවක් පෙන්වයි',
              'මානසික පීඩනය, පවුල් කරුණු ගැන වැඩිපුර සිතීම හෝ තීරණ ප්‍රමාද වීමක් අත්විඳිය හැකි ප්‍රවණතාවක් පෙන්වයි',
              'ආදායම්-වියදම් සමතුලිතතාව, පවුල් වගකීම් හෝ ඉතිරි කිරීමේදී පීඩනයක් ඇතිවිය හැකි ප්‍රවණතාවක් පෙන්වයි',
              'අධ්‍යාපනයේ මාර්ග වෙනස්කම්, විභාග/අයදුම් ප්‍රමාද හෝ කුසලතා නැවත ගොඩනැගීමේ අවශ්‍යතාවක් ඇතිවිය හැක',
              'රැකියා වෙනස්කම්, උසස්වීම් ප්‍රමාද, වැඩ බර හෝ වගකීම් වැඩිවීම අත්විඳිය හැකි ප්‍රවණතාවක් පෙන්වයි',
              'හවුල්කරුවන් සමඟ මතභේද, ගිවිසුම් ප්‍රමාද හෝ ලාභ බෙදීම ගැන පැහැදිලිභාවය අවශ්‍ය විය හැක',
              'සබඳතා තුළ දුරස්වීම්, ප්‍රමාද, වැරදි අවබෝධ හෝ වැඩි ඉවසීම අවශ්‍ය කාල පෙන්විය හැක',
              'විදේශ/ගමන් සැලසුම්වල ලේඛන ප්‍රමාද, වියදම් හෝ සැලසුම් වෙනස්කම් ඇතිවිය හැකි ප්‍රවණතාවක් පෙන්වයි',
              'නිවස, ඉඩම් හෝ වාහන කටයුතු වල ප්‍රමාද, අමතර වියදම් හෝ ලේඛන පරීක්ෂාව අවශ්‍ය විය හැක',
              'දරුවන්/නිර්මාණශීලී වැඩ/ඉගෙනීමේ අංශයේ ඉවසීම, සැලසුම් වෙනස්කම් හෝ වැඩි අවධානය අවශ්‍ය විය හැක',
              'ණය, අනපේක්ෂිත වියදම්, ආතතිය හෝ නැවත සැලසුම් කිරීමේ අවශ්‍යතාව වැඩි විය හැක',
              'ගෞරවය හෝ සමාජ වර්ධනය මන්දගාමී වීම, සහය ලැබීමට ප්‍රමාද වීම හෝ වැඩි උත්සාහයක් අවශ්‍ය විය හැක'
            ]
            body += ' ඇතිවිය හැකි අත්දැකීම්: ' + effects[idx] + '. මේවා නියත සිදුවීම් නොව, අදාළ දශා/ගෝචර සක්‍රීය කාලවල වැඩිපුර පෙනිය හැකි සාම්ප්‍රදායික ජ්‍යෝතිෂ්‍ය ප්‍රවණතා ලෙස සලකන්න.'
        # unique example tied to actual strongest planet/house
        related=[p for p in planets.values() if p.get('house') in houses]
        if related:
            p=related[(seed+idx)%len(related)]
            body += f" උදාහරණයක්: {_planet_phrase(p,dmap)} බැවින් {HOUSE_MEANINGS.get(p.get('house'),'එම අංශය')} ගැන තීරණයකදී එම ග්‍රහයාගේ ස්වභාවය ප්‍රතිඵලයට සෘජුව එක් වේ."
        sections.append({'title':title,'text':body})

    # timing is chart-specific and date-bounded
    tw=_timing_windows(planets,lagna,dasha)
    timing=[]
    for r in tw:
        timing.append(f"{r['level']} — {r['lord']}: {r['start']} සිට {r['end']} දක්වා. ප්‍රධාන තේමාව: {r['theme']}.")
    if timing:
        timing.append('දිනයක් “නියත සිදුවීමක්” ලෙස නොව, දශා මට්ටම් එකිනෙක එකතු වන කාල පරාසයක් ලෙස බලන්න. ගෝචරය ඒ කාල පරාසය තුළ සිදුවීමේ තීව්‍රතාව වැඩි හෝ අඩු කළ හැක.')
    sections.append({'title':'13. කාල විග්‍රහය — මහා දශා, අතුරු දශා සහ ප්‍රත්‍යන්තර දශා','text':' '.join(timing) if timing else 'දශා කාල දත්ත සම්පූර්ණ නැත.'})

    # remedies are also tied to actual pressured houses
    weak=[]
    for h in range(1,13):
        p,c=_section_judgement([h],lag_i,planets,aspects,dmap,md.get('lord'))
        if len(c)>len(p): weak.append(h)
    remedies=[]
    for h in weak[:4]:
        remedies.append(f"{h} වන භාවය ({HOUSE_MEANINGS[h]}) සඳහා: අදාළ ලේඛන, වියදම්, කාලසටහන් සහ වගකීම් ලිඛිතව පාලනය කරන්න. සාම්ප්‍රදායිකව පින්කම්, දානය සහ සංයමය යෝග්‍ය ලෙස සලකයි.")
    if md.get('lord'):
        remedies.append(f"වත්මන් {md['name']} මහා දශාව සඳහා: {PLANET_SI.get(md['lord'],md['lord'])} සම්බන්ධ අධිකත්වය පාලනය කර, එම ග්‍රහයා පිහිටි {planets[md['lord']].get('house')} වන භාවයේ වගකීම් ක්‍රමවත් කරන්න.")
    remedies.append('පිළියම් ප්‍රතිඵල තහවුරු කරන ප්‍රතිකාර ලෙස නොව, සංයමය, පින්කම් සහ ප්‍රායෝගික පාලනය වැඩි කරන සාම්ප්‍රදායික ක්‍රියා ලෙස භාවිතා කරන්න.')
    sections.append({'title':'14. මෙම කේන්දරයට අදාළ පිළියම් සහ ප්‍රායෝගික උපදෙස්','text':' '.join(remedies)})

    signature=f"{lagna['rashi']['name']} ලග්නය • {moon['rashi']['name']} චන්ද්‍ර රාශිය • {nak['name']} {nak.get('pada')} පාදය • {md.get('name','—')} මහා දශාව"
    sections.append({'title':'15. කේන්දරයේ අනන්‍ය සාරාංශය','text':f"මෙම විග්‍රහය {signature} යන සංයෝගයට ගැලපෙන ලෙස සකස් කර ඇත. වෙනත් කේන්දරයක ලග්නය, චන්ද්‍රයා, භාව අධිපති, යුති, දෘෂ්ටි හෝ දශාව වෙනස් නම් මෙම කොටස්වල තේමාව සහ නිගමනද වෙනස් විය යුතුය."})
    return {'summary':summary,'sections':sections}


def detailed_reading(lagna, planets, dasha):
    return expanded_reading(lagna,planets,dasha,reference=False)


# --- PHKS Cloud/Web entrypoint (must stay at file end) ---
def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", str(PORT)))
    print(f"{APP_NAME} {APP_VERSION} running at http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()
