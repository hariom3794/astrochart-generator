from flask import Flask, render_template, request, send_file
import requests
from datetime import datetime
import csv
import io

app = Flask(__name__)

API_USER = "642932"
API_KEY = "4b79d66c268f357cd3e495fb3b655fa1506cd944"
BASE_URL = "https://json.astrologyapi.com/v1"

planet_data_cache = []  # to temporarily store planet data for CSV download

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/get_details", methods=["POST"])
def get_details():
    global planet_data_cache
    dob = request.form["dob"]
    tob = request.form["tob"]
    lat = float(request.form["lat"])
    lon = float(request.form["lon"])
    tzone = float(request.form["tzone"])

    dob_obj = datetime.strptime(dob.strip(), "%Y-%m-%d")
    tob_obj = datetime.strptime(tob.strip(), "%H:%M")

    payload = {
        "day": dob_obj.day,
        "month": dob_obj.month,
        "year": dob_obj.year,
        "hour": tob_obj.hour,
        "min": tob_obj.minute,
        "lat": lat,
        "lon": lon,
        "tzone": tzone
    }

    # Get Birth Details
    birth_response = requests.post(f"{BASE_URL}/birth_details", auth=(API_USER, API_KEY), json=payload)
    birth_data = birth_response.json() if birth_response.status_code == 200 else None

    # Get Planet Details
    planet_response = requests.post(f"{BASE_URL}/planets", auth=(API_USER, API_KEY), json=payload)
    planet_data = planet_response.json() if planet_response.status_code == 200 else None

    planet_data_cache = planet_data if isinstance(planet_data, list) else []

    return render_template("index.html", birth_data=birth_data, planet_data=planet_data)

@app.route("/download_csv")
def download_csv():
    global planet_data_cache
    if not planet_data_cache:
        return "No planet data to download.", 400

    # Prepare CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=planet_data_cache[0].keys())
    writer.writeheader()
    writer.writerows(planet_data_cache)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='planet_details.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
