# This is a python file you need to have in the same directory as your code so you can import it
import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd
import datetime
import os
from dotenv import load_dotenv, find_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Load your credentials
load_dotenv(find_dotenv())

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

server=Oauth2.OAuth2Server(CLIENT_ID,
                           CLIENT_SECRET)
server.browser_authorize()
ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])
auth2_client=fitbit.Fitbit(CLIENT_ID,
                           CLIENT_SECRET,
                           oauth2=True,
                           access_token=ACCESS_TOKEN,
                           refresh_token=REFRESH_TOKEN)

cache = dict()


def get_heart_df_from_server(oneDate):
    oneDayData = auth2_client.intraday_time_series('activities/heart', oneDate, detail_level='1min')
    return (pd.DataFrame(oneDayData["activities-heart-intraday"]["dataset"])
            .assign(time = lambda x: pd.to_datetime(str(f"{oneDate} ") + x["time"]))
           )


def get_heart_df(oneDate):
    if f"{str(oneDate)}_heart" not in cache:
        cache[f"{str(oneDate)}_heart"] = get_heart_df_from_server(oneDate)

    return cache[f"{str(oneDate)}_heart"]


def get_steps_df_from_server(oneDate):
    oneDayData = auth2_client.intraday_time_series('activities/steps', oneDate, detail_level='1min')
    return (pd.DataFrame(oneDayData["activities-steps-intraday"]["dataset"])
            .assign(time = lambda x: pd.to_datetime(str(f"{oneDate} ") + x["time"]))
           )


def get_steps_df(oneDate):
    if f"{str(oneDate)}_steps" not in cache:
        cache[f"{str(oneDate)}_steps"] = get_steps_df_from_server(oneDate)

    return cache[f"{str(oneDate)}_steps"]