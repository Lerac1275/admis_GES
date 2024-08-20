import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re
import helper as hp

@st.cache_data
def load_main_df():
    main_df = hp.load_main_df()
    # Get unique set of uni - course
    course_df = main_df[['uni', 'course']].drop_duplicates()
    return main_df, course_df

# Load in the main dataframe
df, course_df = load_main_df()

# List of unique universities
uni_list = ['NUS', 'NTU', 'SMU']

# University the user selected

# User selects a university
selected_uni = st.selectbox("Select a University", uni_list)

# Filter courses based on the selected university
filtered_courses = course_df[course_df['uni'] == selected_uni]['course']

# User selects a course from the filtered list
selected_course = st.selectbox("Select a Course", filtered_courses)

# Display the selected university and course
st.write(f"Selected University: {selected_uni}")
st.write(f"Selected Course: {selected_course}")

# Compute button. Only run when user wants to recompute
if st.button('Visualize'):
    with st.spinner():
        # ADMISSIONS CRITERIA
        admissions_plot = hp.plot_admission(
            selected_course=selected_course
            , selected_uni=selected_uni
            , input_df=df)
        # Configure the plotly chart to disable zoom and resize functionality
        config = {
            # 'staticPlot':True,
            'scrollZoom': False,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
        }
        st.plotly_chart(admissions_plot
                        , use_container_width=True
                        , theme=None
                        # , config=config
                        )