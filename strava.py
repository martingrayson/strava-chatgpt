import requests
from datetime import datetime

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
    headers = {'Authorization': f'Bearer {access_token}'}
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
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f'https://www.strava.com/api/v3/activities/{activity_id}?include_all_efforts=',
        headers=headers
    )
    response.raise_for_status()
    return response.json()