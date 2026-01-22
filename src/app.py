import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from writer import plot_commit_graph
from grid import dict_to_matrix, matrix_to_dict, df_to_matrix
from dates import year_dict
from github_interaction import github_upload_commits

# # Streamlit app
st.title("GitHub Contribution Graph Editor")

# streamlit setup variables
st.set_page_config(layout="wide")

## Data Structure : Dict of Dates to Counts
st.session_state.commit_date_counts = year_dict()
st.session_state.commit_matrix = dict_to_matrix(st.session_state.commit_date_counts)
st.session_state.commit_df = pd.DataFrame(st.session_state.commit_matrix[1:,:])  # exclude empty top row

## User Input Variables
with st.container(border=False):

# random fill toggle
    v1, v2 = st.columns(2,gap='small')
    with v1:
        if st.button("Random Fill Contributions"):
            st.session_state.commit_df = pd.DataFrame(
                np.random.randint(0, 4, size=(7, 52))
            )
            st.session_state.commit_date_counts = matrix_to_dict(st.session_state.commit_df.values, year= datetime.now().date().year)

    # reset commit graph data
    with v2:
        if st.button("Reset Contribution Graph"):
            st.session_state.commit_df = pd.DataFrame([
                [0]*52 for _ in range(7)
            ])
            st.session_state.commit_date_counts = year_dict()

## Editable DataFrame
st.subheader("Manually Edit")
st.write("Edit the number of contributions (0-4) for each day in the grid below:")

## display editable dataframe
st.session_state.commit_df = st.data_editor(
    st.session_state.commit_df,
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
st.subheader("")

# convert df to np array expected in plot_commit_graph
st.session_state.commit_matrix = df_to_matrix(st.session_state.commit_df)

# convert df back to dict of date: counts
st.session_state.commit_date_counts = matrix_to_dict(st.session_state.commit_matrix, year= datetime.now().date().year)

# plot the committed data
fig = plot_commit_graph(st.session_state.commit_matrix)
st.pyplot(fig)

## Metrics Display
st.metric(label="Total Contributions", value=sum(st.session_state.commit_date_counts.values()))

## Upload to Gitlab
st.subheader("Upload to GitHub Repository")

if sum(st.session_state.commit_date_counts.values()) > 0:
    # check to see if streamlit secrets are set
    try:
        st.secrets["GITHUB_USERNAME"]
        st.secrets["GITHUB_EMAIL"]
        st.secrets["GITHUB_TOKEN"]
        st.secrets["REPO_URL"]
        if "GITHUB_USERNAME" in st.secrets and "GITHUB_EMAIL" in st.secrets and "GITHUB_TOKEN" in st.secrets and "REPO_URL" in st.secrets:
            
            # upload button and trigger github upload push
            if st.button("Upload to Github Repository"):
                with st.spinner("Generating commits..."):

                    # Pull secrets from expected streamlit secrets under .streamlit/secrets.toml
                    GIT_USERNAME = st.secrets["GITHUB_USERNAME"]
                    GIT_EMAIL = st.secrets["GITHUB_EMAIL"]
                    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
                    github_upload_commits(GITHUB_TOKEN=GITHUB_TOKEN,
                                        GIT_USERNAME=GIT_USERNAME,
                                        GIT_EMAIL=GIT_EMAIL,
                                        REPO_URL=st.secrets["REPO_URL"],
                                        commit_date_counts=st.session_state.commit_date_counts)
                    st.success("Commits uploaded successfully!", icon="✅")
        else:
            st.warning("GitHub credentials not found in Streamlit secrets. Please add GITHUB_USERNAME, GITHUB_EMAIL, GITHUB_TOKEN, and REPO_URL to .streamlit/secrets.toml", icon="⚠️")
    except:
        st.warning("Please ensure Github credentials are properly configured in .streamlit/secrets.toml", icon="⚠️")
else:
    st.info("Add at least one contribution required to enable upload to Github Repository.", icon="ℹ️")




