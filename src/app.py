import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from writer import plot_commit_graph
from grid import dict_to_matrix, matrix_to_dict, df_to_matrix
from dates import year_dict

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
            width="small",
            disabled=False
        ) for col in st.session_state.commit_df.columns
    }
)

## Display Commit Graph
st.subheader("")

# convert df to np array expected in plot_commit_graph
st.session_state.commit_matrix = df_to_matrix(st.session_state.commit_df)

# plot the committed data
fig = plot_commit_graph(st.session_state.commit_matrix)
st.pyplot(fig)






