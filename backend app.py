from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import requests

app = Flask(__name__)
CORS(app)

def calculate_impact(diameter, velocity, density):
    radius = diameter / 2
    volume = (4/3) * math.pi * (radius ** 3)
    mass = volume * density
    energy = 0.5 * mass * (velocity ** 2)
    tnt_megatons = (energy / 4.184e9) / 1e6
    destruction_radius_km = (tnt_megatons ** (1/3)) * 5
    return {
        "mass_kg": mass,
        "impact_energy_megatons": tnt_megatons,
        "destruction_radius_km": destruction_radius_km
    }

@app.route('/impact', methods=['POST'])
def impact():
    data = request.get_json()
    city = data.get("city", "London")
    try:
        diameter = float(data.get("diameter", 100))
        velocity = float(data.get("velocity", 20000))
        density = float(data.get("density", 3000))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric input"}), 400

    geo_url = f"https://nominatim.openstreetmap.org/search?city={city}&format=json"
    headers = {"User-Agent": "AsteroidImpactApp/1.0"}
    try:
        geo_response = requests.get(geo_url, headers=headers, timeout=5).json()
    except requests.RequestException as e:
        return jsonify({"error": "City lookup failed", "details": str(e)}), 500

    if not geo_response:
        return jsonify({"error": "City not found"}), 404

    lat = float(geo_response[0]["lat"])
    lon = float(geo_response[0]["lon"])

    impact_data = calculate_impact(diameter, velocity, density)
    impact_data["city"] = city
    impact_data["lat"] = lat
    impact_data["lon"] = lon

    return jsonify(impact_data)

if __name__ == '__main__':
    app.run(debug=True)
