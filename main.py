import streamlit as st
import plotly.express as px
import pandas as pd
from utils.courtCoordinates import CourtCoordinates
from utils.basketballShot import BasketballShot
from snowflake.snowpark import Session

st.set_page_config(layout="wide")
st.title("UNC vs Kansas Men's Basketball Championship - National Championship 2022 ")

# create a connection
@st.cache_resource
def create_session_object():
    connection_parameters = {
       "account": "<ACCOUNT>",
       "user": "<USER>",
       "role": "<ROLE>",
       "warehouse": "<WAREHOUSE>",
       "database": "<DATABASE>",
       "schema": "<SCHEMA",
       "authenticator": "<AUTHENTICATOR>"
    }
    session = Session.builder.configs(connection_parameters).create()
    return session

session = create_session_object()

# query the data
@st.cache_data
def load_data(query):
    return session.sql(query).to_pandas() 
    
query = """
    SELECT  sequence_number,
            coordinate_x,
            coordinate_y,
            team_id,
            text,
            scoring_play,
            case 
                when team_id = home_team_id
                    then 'home'
                else 'away'
            end as scoring_team
    FROM    play_by_play
    WHERE   game_id = 401408636
    AND     shooting_play
    AND     score_value != 1  -- shot charts typically do not include free throws
"""

game_shots_df = load_data(query)

# draw court lines
court = CourtCoordinates()
court_lines_df = court.get_court_lines()

fig = px.line_3d(
    data_frame=court_lines_df,
    x='x',
    y='y',
    z='z',
    line_group='line_group',
    color='color',
    color_discrete_map={
        'court': '#000000',
        'hoop': '#e47041'
    }
)
fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)

game_coords_df = pd.DataFrame()
# generate coordinates for shot paths
for index, row in game_shots_df.iterrows():
    shot = BasketballShot(
        shot_start_x=row.COORDINATE_X, 
        shot_start_y=row.COORDINATE_Y, 
        shot_id=row.SEQUENCE_NUMBER,
        play_description=row.TEXT,
        shot_made=row.SCORING_PLAY,
        team=row.SCORING_TEAM)
    shot_df = shot.get_shot_path_coordinates()
    game_coords_df = pd.concat([game_coords_df, shot_df])

color_mapping = {
    'away': '#7BAFD4',
    'home': '#0051BA'
}

# draw shot paths
shot_path_fig = px.line_3d(
    data_frame=game_coords_df,
    x='x',
    y='y',
    z='z',
    line_group='line_id',
    color='team',
    color_discrete_map=color_mapping,
    custom_data=['description']
)

hovertemplate='Description: %{customdata[0]}'
shot_path_fig.update_traces(opacity=0.55, hovertemplate=hovertemplate, showlegend=False)

# shot start scatter plots
game_coords_start = game_coords_df[game_coords_df['shot_coord_index'] == 0]
shot_start_fig = px.scatter_3d(
    data_frame=game_coords_start,
    x='x',
    y='y',
    z='z',
    custom_data=['description'],
    color='team',
    color_discrete_map=color_mapping,
    symbol='shot_made',
    symbol_map={'made': 'circle', 'missed': 'x'}
)

shot_start_fig.update_traces(marker_size=4, hovertemplate=hovertemplate)

# add shot scatter plot to court plot
for i in range(len(shot_start_fig.data)):
    fig.add_trace(shot_start_fig.data[i])

# add shot line plot to court plot
for i in range(len(shot_path_fig.data)):
    fig.add_trace(shot_path_fig.data[i])

# graph styling
fig.update_traces(line=dict(width=5))
fig.update_layout(    
    margin=dict(l=20, r=20, t=20, b=20),
    scene_aspectmode="data",
    height=600,
    scene_camera=dict(
        eye=dict(x=1.3, y=0, z=0.7)
    ),
    scene=dict(
        xaxis=dict(title='', showticklabels=False, showgrid=False),
        yaxis=dict(title='', showticklabels=False, showgrid=False),
        zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#f7f0e8'),
    ),
    legend=dict(
        yanchor='bottom',
        y=0.05,
        x=0.3,
        xanchor='left',
        orientation='h',
        font=dict(size=15, color='black'),
        bgcolor='white',
        title='',
        itemsizing='constant'
    ),
    legend_traceorder="reversed"
)

st.plotly_chart(fig, use_container_width=True)
