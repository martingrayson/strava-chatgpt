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
            f"Avg Speed: {lap.get('average_speed')} m/s, Avg HR: {lap.get('average_heartrate')} bpm, Average cadence(spm): {lap.get('average_cadence')}"
        )
    return lines

def format_regular_splits(splits):
    lines = ["Here are the splits:\n"]
    for split in splits:
        lines.append(
            f"Split {split.get('split')}: {split.get('distance')}m in {split.get('moving_time')}s, Elevation change(m): {split.get('elevation_difference')}, "
            f"Avg Speed: {split.get('average_speed')} m/s, Avg HR: {split.get('average_heartrate')} bpm"
        )
    return lines
