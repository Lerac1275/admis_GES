import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import re

# Load in data and perform university-level aggregations
def load_main_df(path:str='./data/graphing_table.csv')->pd.DataFrame:
    """
    Loads in the main table of degree information then performs the university aggregation of 25th percentile, median, 75th percentile values. 

    Note that 25th percentile takes the 25th percentile of all measures across all courses for that university for that year. Median takes the median. 75th percentile takes the 75th percentile. 

    Parameters
    ----------
    path:str
        The path to the table of information to read in
    
    Returns
    -------
    pd.DataFrame
    """
    # Load in dataframe
    df = pd.read_csv(path)
    # Get minimum and maximum year
    min_year, max_year = df.year.min().item(), df.year.max().item()
    # Identify rows that are summary stats at the university level
    df['summary_row'] = 0 
    # Do this for EVERY university
    for uni_tmp in df.uni.unique().tolist():

        # Filter for that uni, for records within the year range
        tdf = df.loc[(df.uni == uni_tmp)
                    & (df.year.between(min_year, max_year))]

        # Aggregate relevant metrics
        metrics = ['Places', 'GPA', 'RP',  'employment_rate_overall','employment_rate_ft_perm','basic_monthly_mean','basic_monthly_median','gross_monthly_mean','gross_monthly_median','gross_mthly_25_percentile','gross_mthly_75_percentile']
        # 25th Percentile rows
        uni_25th_pctile = tdf.groupby('year', as_index=False)[metrics].agg(lambda x: x.quantile(0.25))
        uni_25th_pctile['uni'] = uni_tmp
        uni_25th_pctile['course'] = f'{uni_tmp} 25th Percentile'
        # Median Rows
        uni_median = tdf.groupby('year', as_index=False)[metrics].agg(lambda x: x.quantile(0.5))
        uni_median['uni'] = uni_tmp
        uni_median['course'] = f'{uni_tmp} Median'
        # 75th Percentile Rows
        uni_75th_percentile = tdf.groupby('year', as_index=False)[metrics].agg(lambda x: x.quantile(0.75))
        uni_75th_percentile['uni'] = uni_tmp
        uni_75th_percentile['course'] = f'{uni_tmp} 75th Percentile'
        stats_table = pd.concat([uni_median, uni_25th_pctile, uni_75th_percentile], ignore_index=True)
        stats_table['summary_row'] = 1
        # Join back to df
        df = pd.concat([df,stats_table], ignore_index=True)

    # track if a row is a course row or not
    df['course_row'] = df.summary_row.replace({0: 1, 1: 0 })
    return df

def plot_admission(selected_course:str, selected_uni:str, input_df:pd.DataFrame)->go.Figure:
    """
    Plots how the RP for the course has changed over the years relative to the university level statistics. 
    """
    # Extracting data for the selected course and the university's aggregation rows
    course_data = input_df[(input_df['course'] == selected_course) & (input_df['uni'] == selected_uni)]
    agg_data = input_df[(input_df['summary_row'] == 1) & (input_df['uni'] == selected_uni)]

    # Creating the plot
    fig = go.Figure()

    # Adding line for the selected course
    fig.add_trace(go.Scatter(
        x=course_data['year'], y=course_data['RP'],
        mode='lines+markers', name=f"{selected_course}",
        line=dict(color='#0F7A8F', width=3, shape='linear')
    ))

    # Colormapping. Will cycle 
    agg_col_map = ['#7c6354', '#DB3F3F', '#317A41', '#222323', '#011638']
    # Adding lines for the aggregation row
    for idx, agg_row in enumerate(agg_data['course'].unique()):
        agg_row_data = agg_data[agg_data['course'] == agg_row]
        fig.add_trace(go.Scatter(
            x=agg_row_data['year'], y=agg_row_data['RP'],
            mode='lines', name=agg_row,
            line=dict(color= agg_col_map[idx%(len(agg_col_map)-1)], width=2, dash='dash'),
            opacity=1
        ))

    # Lower RP limit rounded down to the nearest 5
    min_rp = min(course_data.RP.min(), agg_data.RP.min())
    min_rp_limit = 5 * (min_rp // 5)

    # Adding padding to the X-axis
    padding = 0.5
    x_min = course_data['year'].min() - padding
    x_max = course_data['year'].max() + padding


    # Updating layout for the presentation preferences
    fig.update_layout(
        title = f"RP cutoff standing for {selected_course} in {selected_uni}", 
        xaxis_title = 'Year', 
        yaxis_title = 'Rank Points', 
        yaxis=dict(
            range=[min_rp_limit, 85],  # Ensure Y-axis ends at 85
            tick0=min_rp_limit,        # Start ticks at the calculated lower limit
            dtick=5                   # Set distance between ticks
        ),
        # For legend at top
        # legend=dict(orientation="h",yanchor="bottom", y=1.02,xanchor="center", x=0.5, traceorder="normal"),             
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        xaxis=dict(range = [x_min, x_max], tickmode='linear', tick0=course_data['year'].min(), dtick=1),
        margin=dict(l=50, r=50, t=50, b=100), 
        hovermode='x'
    )

    fig.update_xaxes(tickangle=45)
    return fig
