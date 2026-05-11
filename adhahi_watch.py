import json
import os
from pathlib import Path

import requests

def _get_api_url():
    value = os.getenv("ADHAHI_WILAYAS_URL", "").strip()
    if not value:
        return "https://adhahi.dz/api/v1/public/wilaya-quotas"
    return value


API_URL = _get_api_url()

DEFAULT_STATE_DIR = Path(__file__).resolve().parent / "state"
STATE_DIR = Path(os.getenv("ADHAHI_STATE_DIR", str(DEFAULT_STATE_DIR)))
STATE_PATH = STATE_DIR / "wilaya_state.json"


def fetch_items():
    response = requests.get(API_URL, headers={"Accept": "application/json"}, timeout=20)
    response.raise_for_status()
    return response.json()


def normalize(items):
    return {
        item["wilayaCode"]: {
            "available": bool(item.get("available")),
            "ar": item.get("wilayaNameAr", ""),
            "fr": item.get("wilayaNameFr", ""),
        }
        for item in items
    }


def load_state():
    if not STATE_PATH.exists():
        return None
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2),
        encoding="utf-8",
    )


def diff_state(old_state, new_state):
    changes = []
    old_state = old_state or {}
    all_codes = sorted(set(old_state) | set(new_state))

    for code in all_codes:
        old_item = old_state.get(code)
        new_item = new_state.get(code)

        if old_item is None:
            changes.append(f"+ {code} {new_item['fr']} available={new_item['available']}")
            continue
        if new_item is None:
            changes.append(f"- {code} {old_item['fr']} removed")
            continue

        if old_item.get("available") != new_item.get("available"):
            changes.append(
                f"* {code} {new_item['fr']} {old_item['available']} -> {new_item['available']}"
            )
            continue

        if old_item.get("fr") != new_item.get("fr") or old_item.get("ar") != new_item.get("ar"):
            changes.append(f"~ {code} name changed")

    return changes


def send_telegram(message):
    token = os.environ.get("TG_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if not token or not chat_id:
        raise SystemExit("Missing TG_BOT_TOKEN or TG_CHAT_ID environment variables.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=20)
    response.raise_for_status()


def main():
    items = fetch_items()
    new_state = normalize(items)
    old_state = load_state()

    changes = diff_state(old_state, new_state)
    if changes:
        message = "Wilaya availability changed:\n" + "\n".join(changes[:200])
        send_telegram(message)

    save_state(new_state)


if __name__ == "__main__":
    main()
