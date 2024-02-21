import os
import streamlit as st
import pandas as pd
from collegebaseball import *

ALWAYS_COLS = ['name', 'Yr', 'GP']
BATTING_COLS = ALWAYS_COLS + ['PA', 'HR', 'SB', 'BB/PA', 'K/PA', 'ISO', 'BABIP', 'BA', 'OBP', 'SLG', 'wOBA', 'wRC']
PITCHING_COLS = ALWAYS_COLS + ['GS', 'IP', 'K/PA', 'BB/PA', 'BABIP-against', 'ERA', 'FIP']

def ratio_to_percentage(value: float):
    return f"{value*100:.1f}%"

def rate_stat(value: float):
    formatted_number = f"{value:.3f}".lstrip('0')
    return formatted_number if formatted_number.startswith('.') else formatted_number.lstrip()

column_transformations = {
    'name': ('Name', None),
    'GP': ('G', None),
    'BB/PA': ('BB%', ratio_to_percentage),
    'K/PA': ('K%', ratio_to_percentage),
    'ISO': ('ISO', rate_stat),
    'BABIP': ('BABIP', rate_stat),
    'BA': ('AVG', rate_stat),
    'OBP': ('OBP', rate_stat),
    'SLG': ('SLG', rate_stat),
    'wOBA': ('wOBA', rate_stat),
    'BABIP-against': ('BABIP', rate_stat),
}

def get_batting_df(school_name: str, year: int) -> pd.DataFrame:
    team_stats_df = ncaa_team_stats(school_name, year, 'batting')
    existing_cols = team_stats_df.columns
    
    missing_cols = [col for col in BATTING_COLS if col not in existing_cols]
    if missing_cols:
        raise ValueError(f"Missing columns in the dataset: {missing_cols}")

    team_stats_df = team_stats_df[BATTING_COLS].sort_values('wRC', ascending=False)
    transformed_df = pd.DataFrame(columns=[column_transformations.get(col, (col, None))[0] for col in BATTING_COLS])

    for col in BATTING_COLS:
        new_col, func = column_transformations.get(col, (col, None))
        if func is not None:
            transformed_df[new_col] = team_stats_df[col].apply(func)
        else:
            transformed_df[new_col] = team_stats_df[col]

    return transformed_df

def get_pitching_df(school_name: str, year: int) -> pd.DataFrame:
    included_cols = PITCHING_COLS + ['HR-A', 'IP-adj']
    team_stats_df = ncaa_team_stats(school_name, year, 'pitching')[included_cols].sort_values('FIP')
    team_stats_df['HR-A'] = (team_stats_df['HR-A'] / team_stats_df['IP-adj'] * 9).apply(lambda x: f"{x:.2f}")
    team_stats_df.rename(columns={'HR-A': 'HR/9'}, inplace=True)

    included_cols = PITCHING_COLS.copy()
    included_cols.insert(7, 'HR/9')
    transformed_df = pd.DataFrame(columns=[column_transformations.get(col, (col, None))[0] for col in included_cols])
    
    for col in included_cols:
        new_col, func = column_transformations.get(col, (col, None))
        if func is not None:
            transformed_df[new_col] = team_stats_df[col].apply(func)
        else:
            transformed_df[new_col] = team_stats_df[col]

    return transformed_df

def get_schools() -> pd.DataFrame:
    dir_path = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(dir_path, 'data', 'schools.csv')
    return pd.read_csv(csv_file_path)

def team(container):
    container.title("Team Stats")

    with container.form("team_stats"):
        col1, col2 = st.columns(2)

        school_name = col1.selectbox(
            "School Name", 
            get_schools()['ncaa_name'],
            index=None,
            placeholder="Enter school name.."
            )
        year = col2.selectbox(
            "Year",
            tuple(range(2023, 2012, -1))
        )
        team_stats_submitted = st.form_submit_button()

    if team_stats_submitted:
        school_info = lookup_school(school_name)
        valid = isinstance(school_info, tuple)
        
        if not valid:
            container.error("Invalid School Name")

        if valid:
            container.header(f"{school_name} {year} Stats")
            container.write(f"Division {'I' * school_info[1]}")
            b, p = container.tabs(["Batting", "Pitching"])

            b.subheader("Batting Leaders")
            batting = get_batting_df(school_name, year)
            b.dataframe(batting, hide_index=True)

            p.subheader("Pitching Leaders")
            pitching = get_pitching_df(school_name, year)
            p.dataframe(pitching, hide_index=True)