from flask import request, render_template
from config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN
from strava import get_access_token, get_activity_data, get_recent_runs
from formatter import format_run_summary
from datetime import datetime


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

    return render_template("index.html", runs=runs, summary=summary, error=error)
