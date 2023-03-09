### Streamlit app that renders a full-court 3D shot chart using NCAA Men's basketball court line dimensions.

The play by play data was acquired from <a href="https://py.sportsdataverse.org/docs/mbb/">sportsdataverse's</a> men's college basketball python package and loaded into a Snowflake table with the following schema: 
    ```
    GAME_ID INT
    SCORE_VALUE INT
    SHOOTING_PLAY BOOLEAN
    SEQUENCE_NUMBER INT
    COORDINATE_X INT
    COORDINATE_Y INT
    TEAM_ID INT
    TEXT VARCHAR
    SCORING_PLAY BOOLEAN
    AWAY_TEAM_ID
    HOME_TEAM_ID
  ```
  
An example of the streamlit app live can be seen TBD
