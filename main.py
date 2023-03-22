import json
import logging
import logging.config
from datetime import datetime, timedelta

import pandas as pd
import requests

from mailer import send_mail

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

READ_KEY = ""


def get_members_data(read_key=READ_KEY, group_id=1683):
    url = f"https://api.purpleair.com/v1/groups/{group_id}/members?fields=name%2Clast_seen"
    resp = requests.get(url, headers={"x-api-key": read_key})
    logger.debug(f"Group ID: {group_id}, Response status: {resp.status_code}")
    if resp.status_code == 200:
        return resp.json()
    logger.error(
        f"Status not 200 for group ID: {group_id}\n"
        f"Status: {resp.status_code}\n"
        f"Response text: \n {resp.text}"
    )


def get_offline_sensors_df(response):
    df = pd.DataFrame(response["data"], columns=response["fields"])
    df["last_seen"] = pd.to_datetime(df["last_seen"], unit="s").dt.tz_localize(
        "UTC"
    )
    utc_now = pd.Timestamp.utcnow()
    df["downtime"] = utc_now - df["last_seen"]
    # df["last_seen"] = df["last_seen"].dt.tz_convert("Europe/Athens")

    offline = df.loc[df["downtime"] > pd.Timedelta(minutes=2)][
        ["name", "downtime"]
    ]
    return offline


def get_offline_sensors_list(response):
    offline = []
    fields = response["fields"]
    for values in response["data"]:
        sensor = dict(zip(fields, values))
        last_seen_dt = datetime.utcfromtimestamp(sensor["last_seen"])
        utc_now = datetime.utcnow()
        downtime = utc_now - last_seen_dt
        if downtime > timedelta(minutes=2):
            sensor["downtime"] = downtime
            offline.append(sensor)
    return offline


response = get_members_data()
offline = get_offline_sensors_list(response)
for sensor in offline:
    print(json.dumps(sensor, indent=4, sort_keys=True, default=str))
# offline = get_offline_sensors_df(response)
# if len(offline) > 0:
#     send_mail(offline.to_html(index=False))


# df_styler = offline.style.format(
#     {"last_seen": lambda t: t.strftime("%a %e %b %I:%M")}
# ).hide(axis="index")
# df_styler.to_html("offline.html", index=False)
