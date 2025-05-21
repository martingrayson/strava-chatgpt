from flask import Flask, request, render_template_string
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# === LOAD ENV ===
load_dotenv()

CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("STRAVA_REFRESH_TOKEN")

app = Flask(__name__)

# === STRAVA API ===

def get_access_token(client_id, client_secret, refresh_token):
    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    response.raise_for_status()
    return response.json()['access_token']

def get_recent_runs(access_token, limit=5):
    headers = {'Authorization': f'Bearer ' + access_token}
    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities?per_page=10',
        headers=headers
    )
    response.raise_for_status()
    activities = response.json()
    runs = [a for a in activities if a.get('sport_type') == 'Run']
    for run in runs:
        run['date_pretty'] = datetime.strptime(run['start_date_local'], "%Y-%m-%dT%H:%M:%S%z").strftime("%d %b %Y")
    return runs[:limit]

def get_activity_data(activity_id, access_token):
    headers = {'Authorization': f'Bearer ' + access_token}
    response = requests.get(
        f'https://www.strava.com/api/v3/activities/{activity_id}?include_all_efforts=',
        headers=headers
    )
    response.raise_for_status()
    return response.json()

# === FORMATTERS ===

def format_run_summary(data):
    lines = [
        "I've just been on another run, here are the summary statistics and splits. Can you please analyse this and give me feedback. Adjust my plan if necessary.",
        f"Run Name: {data.get('name')}, Start time: {data.get('start_date_local')}, "
        f"Total distance (m): {data.get('distance')}, Total time (s): {data.get('moving_time')}, "
        f"Total elevation gain (m): {data.get('total_elevation_gain')}"
    ]

    gear = data.get('gear')
    if gear and gear.get('name'):
        lines.append(
            f"I was wearing {gear['name']} shoes. They've been used for a total of {gear.get('distance', 0)} meters of running."
        )

    if data.get('workout_type') == 3:
        lines += format_structured_splits(data.get('laps', []))
    else:
        lines += format_regular_splits(data.get('splits_metric', []))

    return "\n".join(lines)

def format_structured_splits(laps):
    lines = ["It was a structured session, here are the splits:\n"]
    for lap in laps:
        lines.append(
            f"Lap {lap.get('lap_index')}: {lap.get('distance')}m in {lap.get('moving_time')}s, "
            f"Speed: {lap.get('average_speed')} m/s, HR: {lap.get('average_heartrate')} bpm"
        )
    return lines

def format_regular_splits(splits):
    lines = ["Here are the splits:\n"]
    for split in splits:
        lines.append(
            f"Split {split.get('split')}: {split.get('distance')}m in {split.get('moving_time')}s, "
            f"Speed: {split.get('average_speed')} m/s, HR: {split.get('average_heartrate')} bpm"
        )
    return lines

# === UI TEMPLATE ===

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Strava Activity Viewer</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: auto;
            padding: 2rem;
            background-color: #f7f9fb;
            color: #333;
        }
        h1, h2, h3 {
            color: #222;
        }
        ul {
            list-style-type: none;
            padding-left: 0;
        }
        li {
            background: white;
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        a {
            font-weight: bold;
            text-decoration: none;
            color: #0077cc;
        }
        a:hover {
            text-decoration: underline;
        }
        pre {
            background: #eee;
            padding: 1rem;
            border-radius: 6px;
            white-space: pre-wrap;
            position: relative;
        }
        button.copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #0077cc;
            color: white;
            border: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            cursor: pointer;
        }
        form {
            margin-top: 2rem;
            padding: 1rem;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        input[type="text"] {
            width: 100%;
            padding: 0.5rem;
            margin-top: 0.5rem;
            margin-bottom: 1rem;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        button {
            padding: 0.5rem 1rem;
            background: #0077cc;
            color: white;
            border: none;
            border-radius: 4px;
        }
        button:hover {
            background: #005fa3;
        }
    </style>
</head>
<body>
    <h1>Strava: Recent Runs</h1>
    {% if runs %}
        <ul>
        {% for run in runs %}
            <li>
                <a href="/?activity_id={{ run.id }}">{{ run.name }}</a><br>
                <small>{{ run.date_pretty }} — {{ "%.2f"|format(run.distance / 1000) }} km</small>
            </li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No recent runs found.</p>
    {% endif %}

    {% if summary %}
        <h2>Activity Summary</h2>
        <pre id="summary-text">{{ summary }}</pre>
        <button class="copy-btn" onclick="copyToClipboard()">Copy</button>
        <script>
        function copyToClipboard() {
            const text = document.getElementById("summary-text").innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert("Copied to clipboard!");
            });
        }
        </script>
    {% elif error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}

    <form method="POST">
        <h3>Manually Fetch a Run</h3>
        <label for="activity_id">Strava Activity ID:</label>
        <input type="text" name="activity_id" required>
        <button type="submit">Fetch</button>
    </form>
</body>
</html>
"""

# === MAIN FLASK ROUTE ===

@app.route('/', methods=['GET', 'POST'])
def home():
    summary = None
    error = None
    runs = []
    activity_id = None

    try:
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
        runs = get_recent_runs(access_token)

        if request.method == 'POST':
            activity_id = request.form.get("activity_id")
        elif request.method == 'GET':
            activity_id = request.args.get("activity_id")

        if activity_id:
            activity_data = get_activity_data(activity_id, access_token)
            if activity_data.get('sport_type') == 'Run':
                summary = format_run_summary(activity_data)
            else:
                error = "That activity is not a run."

    except Exception as e:
        error = f"Something went wrong: {str(e)}"

    return render_template_string(HTML_TEMPLATE, runs=runs, summary=summary, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
