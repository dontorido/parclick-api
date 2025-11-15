from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Debes enviar ?city=CIUDAD"}), 400

    url = f"https://api.parclick.com/search/autocomplete?q={city}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": "Error en autocomplete", "details": str(e)}), 500

@app.route("/available", methods=["GET"])
def available():
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    start = request.args.get("from")
    end = request.args.get("to")

    if not all([lat, lng, start, end]):
        return jsonify({"error": "Faltan parámetros"}), 400

    url = (
        "https://api.parclick.com/search/parkings/available"
        f"?latitude={lat}&longitude={lng}&from={start}&to={end}"
        "&radius=1000&vehicleType=1&limit=200&locale=es_ES"
    )

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": "Error consultando parkings", "details": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "service": "parclick-api"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
