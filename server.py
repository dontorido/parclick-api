import asyncio
from flask import Flask, request, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

async def buscar_parkings(city, entrada, salida):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        page = await context.new_page()

        # URL de la web de Parclick
        url = f"https://parclick.es/search?q={city}&df={entrada}&dt={salida}&group=search&isAirport=0"

        await page.goto(url, wait_until="networkidle")

        # Capturar XHR
        async def intercept_response(response):
            try:
                if "parkings/available" in response.url and response.status == 200:
                    return await response.json()
            except:
                    return None

        responses = []
        page.on("response", lambda r: responses.append(r))

        # Esperar resultados
        await page.wait_for_timeout(5000)

        # Buscar JSON real
        parkings_data = None
        for r in responses:
            if "parkings/available" in r.url:
                try:
                    parkings_data = await r.json()
                except:
                    pass

        await browser.close()
        return parkings_data

@app.route("/search")
def search():
    city = request.args.get("city")
    entrada = request.args.get("from")
    salida = request.args.get("to")

    if not all([city, entrada, salida]):
        return jsonify({"error": "city, from, to son obligatorios"}), 400

    result = asyncio.run(buscar_parkings(city, entrada, salida))

    return jsonify(result or {"error": "sin resultados"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
