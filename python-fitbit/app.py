# This is a python file you need to have in the same directory as your code so you can import it
import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd
import datetime
import os
from dotenv import load_dotenv, find_dotenv

import dash
# from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

import dash_core_components as dcc
import dash_html_components as html

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


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/darkly/bootstrap.min.css']
# external_stylesheets = ['new_style.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

activity_choice_list = ["heart",
    "calories",
# "caloriesBMR",
"steps",
"distance",
"floors",
"elevation",
"minutesSedentary",
"minutesLightlyActive",
"minutesFairlyActive",
"minutesVeryActive",
# "activityCalories"
                        ]

# activity_choice_list = ["calories", "heart", "steps", "distance"]
date_choice_list = pd.date_range(start='1/1/2021', end=str(datetime.datetime.now())).astype(str).tolist()[:-1]

app.layout = html.Div([
    html.H1(id='H1', children='The daily fitbit data of James Twose', style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
    html.Div([dcc.Dropdown(
            id='activity_choice',
            options=[{'label': i.title().replace("_", " "), 'value': i} for i in activity_choice_list],
            value="heart"
        )], style={'width': '49.8%', 'display': 'inline-block', 'color': "#222"}),
    html.Div([dcc.Dropdown(
        id='date_choice',
        options=[{'label': i.title().replace("_", " "), 'value': i} for i in date_choice_list],
        value=date_choice_list[-1]
    )], style={'width': '49.8%', 'float': 'right', 'display': 'inline-block', 'color': "#222"}),

    # html.Div(id='display-value')
    dcc.Graph(id='line_plot'),
    dcc.Graph(id="heatmap_plot"),
    html.Div(html.A(children="Created by James Twose",
                    href="https://services.jms.rocks",
                    style={'color': "#743de0"}),
                    style = {'textAlign': 'center',
                             'color': "#743de0",
                             'marginTop': 40,
                             'marginBottom': 40})
]
)


@app.callback(Output(component_id='line_plot', component_property='figure'),
              [Input(component_id='activity_choice', component_property='value'),
              Input(component_id='date_choice', component_property='value')]
              )
def graph_update(activity_choice, date_choice):
    # print(dropdown_value)
    # fig = go.Figure([go.Scatter(x=df.loc[df["location"] == '{}'.format(activity_choice), 'date'],
    #                             y=df.loc[df["location"] == '{}'.format(activity_choice), date_choice],
    #
    #                             # line=dict(color='firebrick', width=1)
    #                             )
    #                  ])

    oneDate = pd.to_datetime(date_choice)

    if activity_choice == "heart":
        chosen_detail_level="1sec"
    else:
        chosen_detail_level = "1min"

    oneDayData = auth2_client.intraday_time_series(f'activities/{activity_choice}', oneDate,
                                                   detail_level=chosen_detail_level)

    df = pd.DataFrame(oneDayData[f"activities-{activity_choice}-intraday"]["dataset"])
    df = df.assign(time=lambda x: pd.to_datetime(str(f"{oneDate} ") + df["time"]))

    fig = px.line(
        data_frame=df,
        x='time',
        y='value',
        template="plotly_dark"
        # markers=True
    )
    fig.update_traces(line_color='#743de0')
    # fig.data[0].update(mode='markers+lines')

    fig.update_layout(title='jms fitbit data == {}'.format(activity_choice),
                      xaxis_title='Time',
                      yaxis_title='{}'.format(date_choice),
                      paper_bgcolor='rgb(34, 34, 34)',
                      plot_bgcolor='rgb(34, 34, 34)'
                      )
    return fig

@app.callback(Output(component_id='heatmap_plot', component_property='figure'),
              [Input(component_id='activity_choice', component_property='value'),
              # Input(component_id='date_choice', component_property='value')
               ]
              )
def heatmap_update(activity_choice):
    monthDiffDate = datetime.datetime.now().date() - datetime.timedelta(30)
    date_tmp_list = pd.date_range(start=str(monthDiffDate),
                                     end=str(datetime.datetime.now())).astype(str).tolist()[:-1]

    dfs_list = list()
    day_number = 1
    for oneDate in date_tmp_list:
        oneDayData = auth2_client.intraday_time_series('activities/heart', oneDate, detail_level='1min')
        df = pd.DataFrame(oneDayData["activities-heart-intraday"]["dataset"])
        df = (df
              .assign(time=lambda x: pd.to_datetime(str(f"{oneDate} ") + df["time"]))
              .rename(columns={"value": f"day_number_{day_number}_value"})
              .assign(hour=lambda d: d["time"].dt.hour)
              .assign(minute=lambda d: d["time"].dt.minute)
              .drop("time", axis=1)
              .set_index(["hour", "minute"])
              )
        dfs_list.append(df)
        day_number += 1

    tmp_df = pd.concat(dfs_list, axis=1)
    tmp_df.index = [str(x).replace(", ", "-").replace("(", "").replace(")", "") for x in tmp_df.index.values]

    fig = px.imshow(tmp_df.T)
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)