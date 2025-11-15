from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_BASE = "https://api.parclick.com"

def obtener_coordenadas(city):
    try:
        r = requests.get(f"{API_BASE}/search/autocomplete?q={city}", timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return data[0].get("latitude"), data[0].get("longitude")
    except Exception as e:
        app.logger.exception("Error autocomplete")
        return None

def buscar_parkings(lat, lng, entrada, salida, radius=1000):
    entrada_api = entrada.replace(" ", "+")
    salida_api = salida.replace(" ", "+")
    url = (
        f"{API_BASE}/search/parkings/available"
        f"?latitude={lat}&longitude={lng}&from={entrada_api}&to={salida_api}"
        f"&radius={radius}&vehicleType=1&limit=200&locale=es_ES"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        app.logger.exception("Error buscar_parkings")
        return []

@app.get("/")
def home():
    return jsonify({"status":"ok","service":"parclick-api (docker, requests-only)","time": datetime.utcnow().isoformat()})

@app.get("/autocomplete")
def autocomplete():
    city = request.args.get("city")
    if not city:
        return jsonify({"error":"Falta parámetro city"}), 400
    coords = requests.get(f"{API_BASE}/search/autocomplete?q={city}", timeout=10)
    try:
        coords.raise_for_status()
        return jsonify(coords.json())
    except Exception as e:
        return jsonify({"error":"autocomplete failed","details": str(e)}), 500

@app.get("/available")
def available():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    start = request.args.get("from")
    end = request.args.get("to")
    radius = request.args.get("radius", "1000")
    if not all([lat,lng,start,end]):
        return jsonify({"error":"Faltan parámetros: lat, lng, from, to"}), 400
    parkings = buscar_parkings(lat,lng,start,end,int(radius))
    return jsonify(parkings)

@app.get("/search")
def search():
    city = request.args.get("city")
    start = request.args.get("from")
    end = request.args.get("to")
    radius = request.args.get("radius", "1000")
    if not all([city,start,end]):
        return jsonify({"error":"Faltan parámetros: city, from, to"}), 400
    coords = obtener_coordenadas(city)
    if not coords:
        return jsonify({"error":"No se pudieron obtener coordenadas para la ciudad"}), 500
    lat,lng = coords
    parkings = buscar_parkings(lat,lng,start,end,int(radius))
    return jsonify({
        "city": city,
        "latitude": lat,
        "longitude": lng,
        "from": start,
        "to": end,
        "radius_m": int(radius),
        "resultados": parkings
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
