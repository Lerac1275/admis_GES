import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re
import helper as hp

st.set_page_config(layout='wide')
@st.cache_data
def load_main_df():
    main_df = hp.load_main_df()
    # Get unique set of uni - course
    course_df = main_df[['uni', 'course', 'summary_row']].drop_duplicates()
    return main_df, course_df

# Load in the main dataframe
df, course_df = load_main_df()

# List of unique universities
uni_list = ['NUS', 'NTU', 'SMU']


st.title("Starting Salary Visualizer")
st.markdown(
"""
Select a degree and observe how its admission critieria, starting salaries, and employment prospects have changed over the years!
"""

)

# University the user selected

# User selects a university
selected_uni = st.selectbox("Select a University", uni_list)


# Filter courses based on the selected university and not a summary roIt'w.
filtered_courses = course_df.loc[(course_df['uni'] == selected_uni)
                             & (course_df['summary_row']==0), 'course']

# User selects a course from the filtered list
selected_course = st.selectbox("Select a Course", filtered_courses)

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
        st.subheader(f"RP Criteria for {selected_course}")
        st.write(f"RP score is the 10th percentile admission score for that year")
        st.plotly_chart(admissions_plot
                        , use_container_width=True
                        , theme=None
                        # , config=config
                        )
        # RP VS MEDIAN INCOME
        median_rp_plot = hp.plot_median_vs_RP(
            selected_course=selected_course
            , selected_uni=selected_uni
            , input_df=df
        )
        st.subheader(f"RP vs Median Gross salary for 2023")
        st.write(f"Each point represents a course from a university in Singapore. **Hover over** the point for more details on that course.")
        # st.write(f"RP score is the 10th percentile admission score for that year")
        st.plotly_chart(median_rp_plot
                        , use_container_width=True
                        , theme=None
                        # , config=config
                        )
        st.markdown(
        """
        With reference to the selected course (in <span style="background-color: #F587F4">pink</span>),  points to the: 
        - **Left** and **Up** are courses with <span style='background-color:#FF9C9C'>lower</span> entry criteria and <span style='background-color:#AAF9C1'>higher</span> starting salaries
        - **Left** and **Down** are courses with <span style='background-color:#FF9C9C'>lower</span> entry criteria and <span style='background-color:#FF9C9C'>lower</span> starting salaries
        - **Right** and **Up** are courses with <span style='background-color:#AAF9C1'>higher</span> entry criteria and <span style='background-color:#AAF9C1'>higher</span> starting salaries
        - **Right** and **Down** are courses with <span style='background-color:#AAF9C1'>higher</span> entry criteria and <span style='background-color:#FF9C9C'>lower</span> starting salaries                          
        """
        , unsafe_allow_html=True)
        # Earnings Percentiles
        percentile_earnings_plot = hp.plot_percentile_earnings(
            selected_course=selected_course
            , selected_uni=selected_uni
            , input_df=df
        )
        st.subheader(f"Percentile earnings for {selected_course}")
        st.markdown(
        """
        - Upper band indicates the 75th percentile salary
        - Middle point indicates the median salary
        - Lower band indicates the 25th percentile salary
        """
        )
        # st.write(f"RP score is the 10th percentile admission score for that year")
        st.plotly_chart(percentile_earnings_plot
                        , use_container_width=True
                        , theme=None
                        # , config=config
                        )
        # Employment Rates
        employment_rates_plot = hp.plot_employment_rates(
            selected_course=selected_course
            , selected_uni=selected_uni
            , input_df=df
        )
        st.subheader(f"Employment rates for {selected_course}")
        st.write(f"FT refers to Full-Time employment. The overall figure includes contract / part-time employment.")
        # st.write(f"RP score is the 10th percentile admission score for that year")
        st.plotly_chart(employment_rates_plot
                        , use_container_width=True
                        , theme=None
                        # , config=config
                        )
        
