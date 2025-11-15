from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def get_autocomplete(query):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.parclick.es/search/autocomplete?q={query}"
            page.goto(url, wait_until="networkidle")

            try:
                content = page.content()
            except:
                browser.close()
                return {"error": "No se pudo cargar contenido"}

            try:
                data = page.evaluate("JSON.parse(document.querySelector('pre').innerText)")
            except:
                browser.close()
                return {"error": "No se pudo parsear JSON"}

            browser.close()
            return data

    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def home():
    return {"status": "OK", "message": "Parclick API funcionando ✔️"}

@app.route("/autocomplete")
def autocomplete():
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Falta parámetro city"}), 400

    result = get_autocomplete(city)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
