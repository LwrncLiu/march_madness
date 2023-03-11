# Streamlit app that renders a full-court 3D shot chart using NCAA Men's basketball court dimensions.

![alt text](https://github.com/LwrncLiu/march_madness/blob/main/static/example.png)

The play by play data was acquired from <a href="https://py.sportsdataverse.org/docs/mbb/">sportsdataverse's</a> men's college basketball python package and loaded into a Snowflake table with the following schema: 

```
CREATE TABLE PLAY_BY_PLAY (
    GAME_ID INT,
    SCORE_VALUE INT,
    SHOOTING_PLAY BOOLEAN,
    SEQUENCE_NUMBER INT,
    COORDINATE_X INT,
    COORDINATE_Y INT,
    TEAM_ID INT,
    TEXT VARCHAR,
    SCORING_PLAY BOOLEAN,
    AWAY_TEAM_ID INT,
    HOME_TEAM_ID INT,
);
```

Without access the the play_by_play table, a sample play_by_play.csv file is available in the static folder.  

## Virtual environment setup

To set up a virtual environment to be compatible with Snowpark and the packages in this repo, run the following commands:

```
conda create --name snowpark --override-channels -c https://repo.anaconda.com/pkgs/snowflake python=3.8 numpy pandas plotly
```

```
conda activate snowpark
```

```
conda install snowflake-snowpark-python
```

```
pip install streamlit 
```
