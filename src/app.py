import streamlit as st
import pandas as pd
import numpy as np

from writer import plot_commit_graph
from grid import df_to_8x52

# # Streamlit app
st.title("GitHub Contribution Graph Editor")

# streamlit setup variables
st.set_page_config(layout="wide")

## User Input Variables
with st.container(border=False):

# random fill toggle
    v1, v2 = st.columns(2,gap='small')
    with v1:
        if st.button("Random Fill Contributions"):
            st.session_state.df = pd.DataFrame(
                np.random.randint(0, 4, size=(7, 52))
            )
        else:
            if "df" not in st.session_state:
                st.session_state.df = pd.DataFrame([
                    [0]*52 for _ in range(7)
                ])

    # reset commit graph data
    with v2:
        if st.button("Reset Contribution Graph"):
            st.session_state.df = pd.DataFrame([
                [0]*52 for _ in range(7)
            ])

## Editable DataFrame
st.subheader("Manually Edit")
st.write("Edit the number of contributions (0-4) for each day in the grid below:")

## display editable dataframe
edited = st.data_editor(
    st.session_state.df,
    hide_index=True,
    column_config={
        col: st.column_config.NumberColumn(
            width="small",
            disabled=False
        ) for col in st.session_state.df.columns
    }
)

## Display Commit Graph
st.subheader("")

# convert df to np array expected in plot_commit_graph
grid = df_to_8x52(edited)

# plot the committed data
fig = plot_commit_graph(grid)
st.pyplot(fig)






