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

# You will need to put in your own CLIENT_ID and CLIENT_SECRET as the ones below are fake

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

# This is the date of data that I want.
# You will need to modify for the date you want
oneDate = pd.datetime(year = 2021, month = 1, day = 21)
oneDayData = auth2_client.intraday_time_series('activities/heart', oneDate, detail_level='1sec')

df = pd.DataFrame(oneDayData["activities-heart-intraday"]["dataset"])

df.head()

_ = sns.lineplot(data=df,
                 x="time",
                 y="value"
                 )
