from pubsub import pub
import time
import requests

from . import settings


COLORS = {
    "green": 60,
    "orange": 80,
    "red": 100,
}


def change_light(littlebits_id, color, duration=15):
    """Duration is in minutes."""
    try:
        percent = COLORS[color.lower()]
    except KeyError:
        raise ValueError("Invalid input color type: {0}".format(color))

    fifteen_min = 1000 * 60 * 15
    littlebits = settings.load()['littlebits']
    url = "https://api-http.littlebitscloud.cc/devices/{0}/output"
    requests.post(
        url.format(littlebits['device']),
        headers={"Authorization": "Bearer {0}".format(littlebits['token'])},
        data={"percent": percent, "duration_ms": fifteen_min}
    )
