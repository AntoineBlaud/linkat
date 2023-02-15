from collections import Counter
import random

call_site_shades = [
    "#db16cb", "#db1641", "#77FF77", "#AAFFAA", "#EEFFEE",
    "#FFBB00", "#FF9900", "#FF7700", "#FF5500", "#badb16"
]
markers_shades = [
    "#FF0000", "#44FF44", "#0000FF", "#FFFF00", "#FF7700", "#FF00FF", "#00FFFF"
]


def build_legends(trace):
    """Builds the legends for the events.

    Args:
        events (list): List of events.

    Returns:
        list: List of legends.
    """
    
    # fill markers_shades with random colors
    for _ in range(len(markers_shades), len(trace["markers_start"]) + 1):
        markers_shades.append("#%06x" % random.randint(0, 0xFFFFFF))

    events = trace["events"]
    # Count the number of events for each call site.
    call_site_count = Counter(event["call_site"] for event in trace["raw"])

    # Get the most common call sites.
    most_cs = [cs for cs, _ in call_site_count.most_common(10)]

    # Build the legends.
    legends = [{
        "name": cs,
        "color": call_site_shades[i],
        "type": "call_site",
    } for i, cs in enumerate(most_cs)]
    legends.extend({
        "name": f"marker_{i}",
        "timestamp": marker["timestamp"],
        "color": markers_shades[i],
        "type": "marker",
    } for i, marker in enumerate(trace["markers_start"]))
    legends.extend((
        {
            "color": "#FF00FF",
            "type": "empty_space",
            "name": "empty_space/never_used",
        },
        {
            "color": "#550000",
            "type": "others",
            "name": "others structure"
        },
    ))

    # Set the color for each event.
    for event_group in events:
        for legend in legends:
            for event in event_group:
                if event["call_site"] == legend["name"]:
                    event["color"] = legend["color"]
                    break
            if "color" not in event:
                event["color"] = None

    return legends