from app.config import ENV

SERVICE_URLS = {
    "localhost": {
        "loki": "http://localhost:3100"
    },
    "production": {
        "loki": "http://loki:3100"
    }
}

def get_url_loki():
    return SERVICE_URLS[ENV]["loki"]