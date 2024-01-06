import os
import streamlit as st
import pandas as pd
from collegebaseball import *

always_cols = ['season', 'school_id', 'GP']
batting_cols = always_cols + ['PA', 'HR', 'SB', 'BB/PA', 'K/PA', 'ISO', 'BABIP', 'BA', 'OBP', 'SLG', 'wOBA', 'wRC']

def ratio_to_percentage(value: float):
    return f"{value*100:.1f}%"

def rate_stat(value: float):
    formatted_number = f"{value:.3f}".lstrip('0')
    return formatted_number if formatted_number.startswith('.') else formatted_number.lstrip()

column_transformations = {
    'season': ('Season', lambda x: str(x)),
    'school_id': ('School', None),
    'GP': ('G', None),
    'BB/PA': ('BB%', ratio_to_percentage),
    'K/PA': ('K%', ratio_to_percentage),
    'ISO': ('ISO', rate_stat),
    'BABIP': ('BABIP', rate_stat),
    'BA': ('AVG', rate_stat),
    'OBP': ('OBP', rate_stat),
    'SLG': ('SLG', rate_stat),
    'wOBA': ('wOBA', rate_stat),
}

def get_batting_df(player_seq: int) -> pd.DataFrame:
    team_stats_df = ncaa_career_stats(player_seq, 'batting')[batting_cols].sort_values('season', ascending=True)
    transformed_df = pd.DataFrame(columns=[column_transformations.get(col, (col, None))[0] for col in batting_cols].insert(2, 'Division'))

    for col in batting_cols:
        new_col, func = column_transformations.get(col, (col, None))
        if new_col == 'School':
            school, division = zip(*team_stats_df[col].apply(lookup_school_reverse))
            transformed_df['School'] = school
            transformed_df['Division'] = division
        elif func is not None:
            transformed_df[new_col] = team_stats_df[col].apply(func)
        else:
            transformed_df[new_col] = team_stats_df[col]

    return transformed_df

def get_schools() -> pd.DataFrame:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(dir_path, 'data', 'schools.csv')
    return pd.read_csv(csv_file_path)

def player(container):
    container.title("Individual Stats")

    with container.form("player_stats"):
        col1, col2 = st.columns(2)

        player_name = col1.text_input(
            "Player Name",
            placeholder="Enter player name..."
        )
        school_name = col2.selectbox(
            "School Name", 
            get_schools()['ncaa_name'],
            index=None,
            placeholder="Enter school name.."
            )
        player_stats_submitted = st.form_submit_button()

    if player_stats_submitted:
        stats_player_seq = lookup_player(player_name, school_name)
        valid = isinstance(stats_player_seq, int)
        
        if not valid:
            container.error("Invalid Player Name")

        if valid:
            container.header(f"{player_name} Career Stats")

            container.subheader("Batting Stats")
            batting = get_batting_df(stats_player_seq)
            container.dataframe(batting, hide_index=True)