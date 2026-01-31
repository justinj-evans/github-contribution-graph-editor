import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import matplotlib.pyplot as plt
from io import BytesIO

from writer import plot_commit_graph
from grid import dict_to_matrix, matrix_to_dict, df_to_matrix
from dates import year_dict, github_contribution_api, convert_api_response_to_dict, safe_date_dict_merge, subtract_date_dicts
from github_interaction import github_upload_commits

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
# )

# # Streamlit app
st.sidebar.image("docs\contribution_icon.PNG", width='stretch')
st.sidebar.title("GitHub Contribution Graph Editor")

# streamlit setup variables
st.set_page_config(layout="wide")

## Data Structure : Dict of Dates to Counts
DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

if "commit_date_counts" not in st.session_state:
    print('Initializing blank year of commits')
    st.session_state.commit_date_counts = year_dict()
    st.session_state.commit_matrix = dict_to_matrix(st.session_state.commit_date_counts)
    st.session_state.commit_df = pd.DataFrame(st.session_state.commit_matrix[:,:], index=DAYS)  # exclude empty top row

## User Input Variables
# Github Username
with st.sidebar.form("github_username_form", clear_on_submit=False):
    username = st.text_input(label="Your GitHub Username",key="github_username", on_change=None)
    submitted = st.form_submit_button("Submit")

if "api_date_dict" not in st.session_state:
    st.session_state.api_date_dict = {}
if submitted and st.session_state.github_username:
    with st.spinner("Pulling commit history..."):
        response = github_contribution_api(st.session_state.github_username)
        if 'error' in response:
            st.toast(f"Failed to fetch data for user: {st.session_state.github_username}. Please check the username and try again.", icon="❌")
        elif response != {}:
            st.session_state.api_date_dict = convert_api_response_to_dict(response) 
            st.toast(f"Successfully pulled {sum(st.session_state.api_date_dict.values())} for user: {st.session_state.github_username}", icon="✅")
            st.session_state.commit_date_counts = safe_date_dict_merge(st.session_state.commit_date_counts, st.session_state.api_date_dict)
            st.session_state.commit_matrix = dict_to_matrix(st.session_state.commit_date_counts)
            st.session_state.commit_df = pd.DataFrame(st.session_state.commit_matrix[:,:], index=DAYS)  # exclude empty top row
            print(f'API Pulled Commits: {sum(st.session_state.api_date_dict.values())}')

with st.sidebar.container(border=False):

    # random fill toggle
    v1, v2 = st.columns(2,gap='small')
    with v1:
        if st.button("Random Fill Contributions"):
            print('Generating random contributions')
            st.session_state.commit_df = pd.DataFrame(
                np.random.randint(0, 4, size=(7, 52))
            )

    # reset commit graph data
    with v2:
        if st.button("Reset Contribution"):
            print('Resetting contribution graph to zero')
            st.session_state.commit_df = pd.DataFrame([
                [0]*52 for _ in range(7)
            ])
            st.session_state.commit_date_counts = year_dict()
            st.session_state.api_date_dict = {}

## Editable DataFrame
st.write("Manually add contributions (0-4) for each day in the grid below")

## display editable dataframe
st.session_state.interactive_commit_df = st.data_editor(
    st.session_state.commit_df,
    key="contribution_grid",
    hide_index=True,
    column_config={
        col: st.column_config.NumberColumn(
            min_value=0,
            max_value=4,
            step=1,
            width="small",
            disabled=False
        ) for col in st.session_state.commit_df.columns
    }
)

## Display Commit Graph

# convert df to np array expected in plot_commit_graph
st.session_state.commit_matrix = df_to_matrix(st.session_state.interactive_commit_df)

# convert df back to dict of date: counts
st.session_state.commit_date_counts = matrix_to_dict(st.session_state.commit_matrix)

# plot the committed data
fig = plot_commit_graph(st.session_state.commit_matrix)
st.pyplot(fig)

## Download Plot
# convert fig to png for download
buf = BytesIO()
fig.savefig(buf, format='png')

st.sidebar.download_button(
    label="Download Graph",
    data=buf.getvalue(),
    file_name="contribution_graph.png",
    mime="image/png"
)

## Prepare Commits
st.session_state.submit_commit_date_count = subtract_date_dicts(dict1=st.session_state.commit_date_counts, 
                                                                dict2=st.session_state.api_date_dict)

## Metrics Display
with st.sidebar.container(border=False):

    # random fill toggle
    l1, l2 = st.sidebar.columns(2,gap='small')
    l1.metric(label="Total Contributions", value=sum(st.session_state.commit_date_counts.values()))
    l2.metric(label="Manual Added", value=sum(st.session_state.submit_commit_date_count.values()))

## Upload to Gitlab
#st.sidebar.subheader("Upload to GitHub Repository")

if sum(st.session_state.commit_date_counts.values()) > 0:
    # check to see if streamlit secrets are set
    try:
        if "GITHUB_USERNAME" in st.secrets and "GITHUB_EMAIL" in st.secrets and "GITHUB_TOKEN" in st.secrets and "REPO_URL" in st.secrets:
            
            # upload button and trigger github upload push
            if st.sidebar.button("Upload to Github Repository"):
                with st.spinner("Generating commits..."):

                    # Calculate the commits to submit: user modifications (current - api)
                    st.session_state.submit_commit_date_count = subtract_date_dicts(
                        dict1=st.session_state.commit_date_counts, 
                        dict2=st.session_state.api_date_dict
                    )

                    # Pull secrets from expected streamlit secrets under .streamlit/secrets.toml
                    GIT_USERNAME = st.secrets["GITHUB_USERNAME"]
                    GIT_EMAIL = st.secrets["GITHUB_EMAIL"]
                    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
                    github_upload_commits(GITHUB_TOKEN=GITHUB_TOKEN,
                                        GIT_USERNAME=GIT_USERNAME,
                                        GIT_EMAIL=GIT_EMAIL,
                                        REPO_URL=st.secrets["REPO_URL"],
                                        commit_date_counts=st.session_state.submit_commit_date_count)
                    st.sidebar.success("Commits uploaded successfully!", icon="✅")
        else:
            st.sidebar.warning("GitHub credentials not found in Streamlit secrets. Please add GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, and REPO_URL to .streamlit/secrets.toml", icon="⚠️")
    except:
        st.sidebar.warning("Please ensure Github credentials are properly configured in .streamlit/secrets.toml", icon="⚠️")
else:
    st.sidebar.info("Add at least one contribution required to enable upload to Github Repository.", icon="ℹ️")




