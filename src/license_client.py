from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Tuple

PRODUCT_SLUG = "hela-jyotishya"
LICENSE_API = "https://api.lemonsqueezy.com/v1/licenses"
REG_PATH = r"Software\HelaJyotishya"
REG_TRIAL_START = "TrialStartUtc"
REG_TRIAL_DEVICE = "TrialDeviceId"
REG_LAST_RUN = "LastRunUtc"

OWNER_UNLIMITED_KEY_HASH = "ebd5872f0be11c92802b955f895d565253513ad37255f6495a1c303d6e2c4ef2"
OWNER_PROVIDER = "phks-owner-local"


def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def load_config() -> Dict[str, Any]:
    p = resource_path("commercial_config.json")
    return json.loads(p.read_text(encoding="utf-8"))


def app_data_dir() -> Path:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
    p = Path(root) / "HelaJyotishya"
    p.mkdir(parents=True, exist_ok=True)
    return p


def cache_path() -> Path:
    return app_data_dir() / "license.json"


def trial_file_path() -> Path:
    return app_data_dir() / "trial.json"


def _windows_machine_guid() -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            value, _ = winreg.QueryValueEx(k, "MachineGuid")
            return str(value)
    except Exception:
        return ""


def device_id() -> str:
    raw = "|".join([
        PRODUCT_SLUG,
        _windows_machine_guid(),
        platform.node(),
        platform.machine(),
        os.environ.get("COMPUTERNAME", ""),
    ])
    return hashlib.sha256(raw.encode("utf-8", "ignore")).hexdigest()[:32]


def instance_name() -> str:
    host = platform.node() or socket.gethostname() or "Windows-PC"
    return f"Hela Jyotishya - {host} - {device_id()[:8]}"


def load_cache() -> Dict[str, Any]:
    p = cache_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(data: Dict[str, Any]) -> None:
    data = dict(data)
    data["device_id"] = device_id()
    cache_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clear_cache() -> None:
    try:
        cache_path().unlink(missing_ok=True)
    except Exception:
        pass


def _reg_get(name: str) -> str:
    if os.name != "nt":
        return ""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
            value, _ = winreg.QueryValueEx(k, name)
            return str(value or "")
    except Exception:
        return ""


def _reg_set(name: str, value: str) -> None:
    if os.name != "nt":
        return
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as k:
            winreg.SetValueEx(k, name, 0, winreg.REG_SZ, str(value))
    except Exception:
        pass


def _post(endpoint: str, fields: Dict[str, str], timeout: int = 12) -> Dict[str, Any]:
    body = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        f"{LICENSE_API}/{endpoint}",
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "HelaJyotishya/Commercial",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8", "replace")
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return {"error": f"HTTP {e.code}"}
    except Exception as e:
        raise ConnectionError(str(e)) from e


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        x = v.replace("Z", "+00:00")
        dt = datetime.fromisoformat(x)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _extract_status(data: Dict[str, Any]) -> str:
    obj = data.get("license_key") or {}
    return str(obj.get("status") or "").lower()


def _extract_expiry(data: Dict[str, Any]) -> str:
    obj = data.get("license_key") or {}
    for k in ("expires_at", "expires"):
        if obj.get(k):
            return str(obj[k])
    return ""


def activate(license_key: str) -> Tuple[bool, str, Dict[str, Any]]:
    key = (license_key or "").strip()
    if not key:
        return False, "බලපත්‍ර යතුර ඇතුළත් කරන්න.", {}

    # PHKS Creation owner/test key: unlimited local paid mode.
    # Only the SHA-256 hash is embedded; the plaintext key is not stored in the package.
    if hashlib.sha256(key.encode("utf-8")).hexdigest() == OWNER_UNLIMITED_KEY_HASH:
        cache = {
            "provider": OWNER_PROVIDER,
            "license_key": key,
            "instance_id": "owner-" + device_id(),
            "instance_name": instance_name(),
            "status": "active",
            "plan": "owner-unlimited",
            "unlimited": True,
            "expires_at": "",
            "last_validated": _iso_now(),
            "meta": {"edition": "PHKS Creation Owner Unlimited"},
        }
        save_cache(cache)
        return True, "PHKS Creation Unlimited බලපත්‍රය සාර්ථකව සක්‍රීය විය.", cache

    try:
        data = _post("activate", {"license_key": key, "instance_name": instance_name()})
    except ConnectionError:
        return False, "අන්තර්ජාල සම්බන්ධතාව පරීක්ෂා කර නැවත උත්සාහ කරන්න.", {}

    if not data.get("activated"):
        return False, str(data.get("error") or "බලපත්‍රය සක්‍රීය කළ නොහැක."), data

    inst = data.get("instance") or {}
    cache = {
        "provider": "lemonsqueezy",
        "license_key": key,
        "instance_id": inst.get("id", ""),
        "instance_name": inst.get("name", instance_name()),
        "status": _extract_status(data) or "active",
        "expires_at": _extract_expiry(data),
        "last_validated": _iso_now(),
        "meta": data.get("meta") or {},
    }
    save_cache(cache)
    return True, "බලපත්‍රය සාර්ථකව සක්‍රීය විය.", cache


def validate_online(cache: Dict[str, Any] | None = None) -> Tuple[bool, str, Dict[str, Any]]:
    cache = dict(cache or load_cache())
    key = cache.get("license_key", "")
    instance_id = cache.get("instance_id", "")
    if not key:
        return False, "බලපත්‍රයක් සක්‍රීය කර නැත.", cache

    if cache.get("provider") == OWNER_PROVIDER and cache.get("unlimited") is True:
        if cache.get("device_id") not in {None, "", device_id()}:
            return False, "මෙම Unlimited බලපත්‍රය වෙනත් පරිගණකයකට බැඳී ඇත.", cache
        if hashlib.sha256(str(key).encode("utf-8")).hexdigest() != OWNER_UNLIMITED_KEY_HASH:
            return False, "Unlimited බලපත්‍ර යතුර වලංගු නොවේ.", cache
        cache["status"] = "active"
        cache["last_validated"] = _iso_now()
        save_cache(cache)
        return True, "PHKS Creation Unlimited බලපත්‍රය වලංගුයි.", cache
    fields = {"license_key": key}
    if instance_id:
        fields["instance_id"] = instance_id
    try:
        data = _post("validate", fields)
    except ConnectionError:
        return False, "ජාල සම්බන්ධතාව නොමැත.", cache

    if not data.get("valid"):
        cache["status"] = _extract_status(data) or "invalid"
        save_cache(cache)
        return False, str(data.get("error") or "බලපත්‍රය වලංගු නොවේ."), cache

    status = _extract_status(data) or "active"
    cache["status"] = status
    cache["expires_at"] = _extract_expiry(data)
    cache["last_validated"] = _iso_now()
    cache["meta"] = data.get("meta") or cache.get("meta", {})
    save_cache(cache)
    return status in {"active", "inactive"}, "බලපත්‍රය වලංගුයි.", cache


def offline_allowed(cache: Dict[str, Any] | None = None, grace_days: int = 3) -> bool:
    cache = cache or load_cache()
    if cache.get("provider") == OWNER_PROVIDER and cache.get("unlimited") is True:
        return (cache.get("device_id") in {None, "", device_id()} and
                hashlib.sha256(str(cache.get("license_key", "")).encode("utf-8")).hexdigest() == OWNER_UNLIMITED_KEY_HASH)
    if not cache.get("license_key") or cache.get("device_id") not in {None, "", device_id()}:
        return False
    if str(cache.get("status", "")).lower() not in {"active", "inactive"}:
        return False
    last = _parse_iso(cache.get("last_validated"))
    if not last:
        return False
    now = datetime.now(timezone.utc)
    if now - last > timedelta(days=max(0, int(grace_days))):
        return False
    expiry = _parse_iso(cache.get("expires_at"))
    if expiry and now >= expiry:
        return False
    return True


def _load_trial_raw() -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    p = trial_file_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    reg_start = _reg_get(REG_TRIAL_START)
    reg_device = _reg_get(REG_TRIAL_DEVICE)
    reg_last = _reg_get(REG_LAST_RUN)
    if reg_start:
        data["started_at"] = reg_start
    if reg_device:
        data["device_id"] = reg_device
    if reg_last:
        data["last_run"] = reg_last
    return data


def _save_trial(data: Dict[str, Any]) -> None:
    payload = dict(data)
    payload["device_id"] = device_id()
    trial_file_path().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if payload.get("started_at"):
        _reg_set(REG_TRIAL_START, str(payload["started_at"]))
    _reg_set(REG_TRIAL_DEVICE, device_id())
    if payload.get("last_run"):
        _reg_set(REG_LAST_RUN, str(payload["last_run"]))


def start_trial(config: Dict[str, Any] | None = None) -> Tuple[bool, str, Dict[str, Any]]:
    config = config or load_config()
    if not config.get("trial_enabled", True):
        return False, "නොමිලේ අත්හදා බැලීම මෙම සංස්කරණයේ සක්‍රීය කර නැත.", {}
    existing = _load_trial_raw()
    if existing.get("started_at"):
        ok, msg, status = trial_status(config)
        return ok, msg, status
    now = datetime.now(timezone.utc)
    data = {
        "started_at": now.isoformat(),
        "last_run": now.isoformat(),
        "device_id": device_id(),
    }
    _save_trial(data)
    days = max(1, int(config.get("trial_days", 14)))
    return True, f"දින {days} නොමිලේ අත්හදා බැලීම ආරම්භ විය.", {
        "status": "trial",
        "trial_days_left": days,
        "started_at": data["started_at"],
    }


def trial_status(config: Dict[str, Any] | None = None) -> Tuple[bool, str, Dict[str, Any]]:
    config = config or load_config()
    data = _load_trial_raw()
    if not data.get("started_at"):
        return False, "අත්හදා බැලීම තවම ආරම්භ කර නැත.", {"status": "trial-not-started"}
    if data.get("device_id") and data.get("device_id") != device_id():
        return False, "මෙම අත්හදා බැලීම වෙනත් පරිගණකයකට බැඳී ඇත.", {"status": "trial-device-mismatch"}
    started = _parse_iso(data.get("started_at"))
    last_run = _parse_iso(data.get("last_run"))
    now = datetime.now(timezone.utc)
    if not started:
        return False, "අත්හදා බැලීමේ දත්ත වලංගු නොවේ.", {"status": "trial-invalid"}
    # Block obvious clock rollback. Small clock drift is tolerated.
    if last_run and now < last_run - timedelta(hours=2):
        return False, "පරිගණකයේ දිනය/වේලාව වෙනස් වී ඇති නිසා අත්හදා බැලීම තහවුරු කළ නොහැක.", {"status": "trial-clock-error"}
    days = max(1, int(config.get("trial_days", 14)))
    expires = started + timedelta(days=days)
    if now >= expires:
        return False, "නොමිලේ අත්හදා බැලීම අවසන් වී ඇත. දිගටම භාවිතයට සැලැස්මක් තෝරන්න.", {
            "status": "trial-expired",
            "trial_days_left": 0,
            "expires_at": expires.isoformat(),
        }
    remaining_seconds = max(0, int((expires - now).total_seconds()))
    days_left = max(1, (remaining_seconds + 86399) // 86400)
    data["last_run"] = now.isoformat()
    _save_trial(data)
    return True, f"නොමිලේ අත්හදා බැලීම — තව දින {days_left} ක්.", {
        "status": "trial",
        "trial_days_left": days_left,
        "started_at": started.isoformat(),
        "expires_at": expires.isoformat(),
    }


def startup_check(config: Dict[str, Any] | None = None) -> Tuple[bool, str, Dict[str, Any]]:
    config = config or load_config()
    if not config.get("license_required", True):
        return True, "license not required", {"status": "not-required"}

    cache = load_cache()
    if cache:
        ok, msg, updated = validate_online(cache)
        if ok:
            return True, msg, updated
        if msg == "ජාල සම්බන්ධතාව නොමැත." and offline_allowed(cache, int(config.get("offline_grace_days", 3))):
            return True, "අන්තර්ජාලය නොමැති නිසා තාවකාලිකව නොබැඳි භාවිතය සක්‍රීයයි.", cache
        # A paid key exists but is invalid/expired: trial must not override it unless no trial was used before.
        trial_ok, trial_msg, trial = trial_status(config)
        if trial_ok:
            return True, trial_msg, trial
        return False, msg, updated

    trial_ok, trial_msg, trial = trial_status(config)
    if trial_ok:
        return True, trial_msg, trial
    return False, trial_msg, trial


def deactivate() -> Tuple[bool, str]:
    cache = load_cache()
    key = cache.get("license_key", "")
    instance_id = cache.get("instance_id", "")
    if cache.get("provider") == OWNER_PROVIDER:
        clear_cache()
        return True, "PHKS Creation Unlimited බලපත්‍රය මෙම පරිගණකයෙන් ඉවත් කළා."
    if not key or not instance_id:
        clear_cache()
        return True, "මෙම පරිගණකයේ බලපත්‍ර සටහන ඉවත් කළා."
    try:
        data = _post("deactivate", {"license_key": key, "instance_id": instance_id})
    except ConnectionError:
        return False, "අන්තර්ජාල සම්බන්ධතාව පරීක්ෂා කරන්න."
    if data.get("deactivated"):
        clear_cache()
        return True, "මෙම පරිගණකයෙන් බලපත්‍රය ඉවත් කළා."
    return False, str(data.get("error") or "බලපත්‍රය ඉවත් කළ නොහැක.")


def display_status(cache: Dict[str, Any] | None = None) -> Dict[str, str]:
    cache = cache or load_cache()
    key = str(cache.get("license_key") or "")
    return {
        "status": str(cache.get("status") or ""),
        "key_short": key[-8:] if key else "",
        "expires_at": str(cache.get("expires_at") or ""),
        "instance_name": str(cache.get("instance_name") or ""),
    }


def self_test() -> bool:
    assert len(device_id()) == 32
    assert isinstance(load_config(), dict)
    cfg = load_config()
    assert int(cfg.get("trial_days", 14)) >= 1
    assert cfg.get("license_required", True) in {True, False}
    assert len(OWNER_UNLIMITED_KEY_HASH) == 64
    return True
