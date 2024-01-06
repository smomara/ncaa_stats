import streamlit as st
from team import team
from player import player

st.set_page_config(
    page_title="NCAA Baseball",
    page_icon="⚾",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': 'https://github.com/smomara'
    }
)

st.title("NCAA Baseball")

with st.expander("Notes"):
    """
    Under Active Development

    Incoming features:
    - improved individual player search
    - pitching + 2 way stats for individuals (currently only support batters)
    - career totals for individuals
    - team totals for teams
    - splits for team and individual stats (vs LH, vs RH, runners on, bases empty, bases loaded, with RIPS, two outs)
    - plus stats
    """

t, p = st.tabs(["Team", "Individual"])

team(t)
player(p)