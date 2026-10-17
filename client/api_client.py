#api_client
import requests

SERVER = "http://localhost:8000"


def login(name, password, register=False):
    """Возвращает (token, error). Если всё хорошо, error = None."""
    body = {"name": name, "password": password}
    try:
        if register:
            r = requests.post(f"{SERVER}/register", json=body, timeout=2)
            if r.status_code != 201:
                return None, r.json().get("detail", "Registration error")
        r = requests.post(f"{SERVER}/login", json=body, timeout=2)
        if r.status_code != 200:
            return None, r.json().get("detail", "Login error")
        return r.json()["token"], None
    except requests.RequestException:
        return None, "Server unavailable"


def save_score(token, score, boss_beaten=False):
    try:
        r = requests.post(f"{SERVER}/scores", json={"score": score, "boss_beaten": boss_beaten},
                          headers={"token": token}, timeout=2)
        print("POST /scores ->", r.status_code, r.text)
    except requests.RequestException as e:
        print("Server error, score not saved", e)


def load_top():
    """Возвращает (список рекордов, сервер_доступен)."""
    try:
        r = requests.get(f"{SERVER}/scores/top", timeout=2)
        return (r.json() if r.status_code == 200 else []), True
    except requests.RequestException:
        return [], False