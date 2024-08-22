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
        print(agg_row)
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
        # title = f"RP cutoff standing for {selected_course} in {selected_uni}", 
        xaxis_title = 'Year', 
        yaxis_title = 'Rank Points', 
        yaxis=dict(
            range=[min_rp_limit, 87],  # Ensure Y-axis ends at 85
            tick0=min_rp_limit,        # Start ticks at the calculated lower limit
            dtick=5                   # Set distance between ticks
        ),
        # For legend at top
        legend=dict(orientation="h",yanchor="bottom", y=1.08,xanchor="center", x=0.5, traceorder="normal"),             
        # legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.08),
        xaxis=dict(range = [x_min, x_max], tickmode='linear', tick0=course_data['year'].min(), dtick=1),
        margin=dict(l=50, r=50, t=15, b=100), 
        hovermode='x',
        # width=800,
        height=350
    )

    # fig.update_xaxes(tickangle=45)
    return fig

def plot_median_vs_RP(selected_course:str, selected_uni:str, input_df:pd.DataFrame)->go.Figure:
    # Filtering data for the latest year available for the selected course
    latest_year = input_df.loc[(input_df['course'] == selected_course)
                            & (input_df['uni']==selected_uni), 'year'].max()
    filtered_df = input_df[(input_df['year'] == latest_year)
                        & (input_df.summary_row==0)].copy()

    # Divide gross_monthly_median by 1,000 for formatting
    filtered_df['gross_monthly_median'] = filtered_df['gross_monthly_median'] / 1000

    # Add custom data for tooltips (course name, RP, and gross monthly median)
    filtered_df['tooltip'] = filtered_df.apply(lambda row: f"{row['course']}<br>RP: {row['RP']}<br>Median Salary: ${row['gross_monthly_median']:.2f}K", axis=1)
    filtered_df['empty'] = ""

    # Creating the scatter plot [NUS, NTU, SMU]
    colors = ['#fe4a49', '#09814a', '#1438CA']
    color_map = {uni: colors[i % len(colors)] for i, uni in enumerate(filtered_df['uni'].unique())}
    # Store Graph Object traces
    traces = []

    # Highlighting the selected course
    selected_data = filtered_df[(filtered_df['course'] == selected_course)
                                & (filtered_df.uni==selected_uni)]
    selected_trace= go.Scatter(
                x=selected_data['RP'], 
                y=selected_data['gross_monthly_median'], 
                mode='markers', 
                name=f"{selected_course} ({selected_uni})", 
                marker=dict(color='#F587F4', size=16),
                hovertemplate='<b>{}</b><br>RP: {}<br>Median Salary: ${:.2f}K'.format(selected_course, selected_data['RP'].values[0], selected_data['gross_monthly_median'].values[0])
            )
    traces.append(selected_trace)

    # Other courses data
    other_courses_df = filtered_df.loc[~((filtered_df.course == selected_course)
                                    & (filtered_df.uni==selected_uni))]

    # Iterate over all other uni courses by uni
    for uni in other_courses_df['uni'].unique():
        uni_data = other_courses_df[other_courses_df['uni'] == uni]
        trace = go.Scatter(
            x=uni_data['RP'],
            y=uni_data['gross_monthly_median'],
            mode='markers',
            name=uni,
            marker=dict(color=color_map[uni], size=8, opacity=0.4),
            customdata=uni_data['tooltip'],
            hovertemplate='%{customdata}'  # This ensures only the custom tooltip is displayed
        )
        # Add the trace
        traces.append(trace)

    # Create the layout
    layout = go.Layout(
        # title=f"RP vs Gross Monthly Median Salary (Year: {latest_year})",
        xaxis=dict(title='Rank Points'),
        yaxis=dict(title='Median Gross Salary (thousands)'),
        # For legend at top
        legend=dict(orientation="h",yanchor="bottom", y=1.08,xanchor="center", x=0.5, traceorder="normal"),  
        # legend=dict(title=None, orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=50, r=50, t=15, b=100),
        # height=300

    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

    return fig

def plot_percentile_earnings(selected_course:str, selected_uni:str, input_df:pd.DataFrame)->go.Figure:
    plot_course = selected_course
    plot_uni = selected_uni

    # Filter data for the selected course and university
    course_data = input_df[(input_df['course'] == plot_course) & (input_df['uni'] == plot_uni) & (input_df['course_row'] == 1)].copy()

    # Filter data for the university median
    uni_median_data = input_df[(input_df['course'] == f"{plot_uni} Median") & (input_df['summary_row'] == 1)].copy()

    # X axis: Years where gross_monthly_median is available
    years = course_data['year']

    # Convert gross monthly salary values to thousands of dollars
    course_data['gross_monthly_median'] = course_data['gross_monthly_median'] / 1000
    course_data['gross_mthly_75_percentile'] = course_data['gross_mthly_75_percentile'] / 1000
    course_data['gross_mthly_25_percentile'] = course_data['gross_mthly_25_percentile'] / 1000

    uni_median_data['gross_monthly_median'] = uni_median_data['gross_monthly_median'] / 1000
    uni_median_data['gross_mthly_75_percentile'] = uni_median_data['gross_mthly_75_percentile'] / 1000
    uni_median_data['gross_mthly_25_percentile'] = uni_median_data['gross_mthly_25_percentile'] / 1000

    # Course line with error bars and custom hover text
    course_trace = go.Scatter(
        x=years,
        y=course_data['gross_monthly_median'],
        error_y=dict(
            type='data',
            symmetric=False,
            array=course_data['gross_mthly_75_percentile'] - course_data['gross_monthly_median'],
            arrayminus=course_data['gross_monthly_median'] - course_data['gross_mthly_25_percentile'],
            visible=True
        ),
        line=dict(color='#0F7A8F'),
        mode='lines+markers',
        name=f"{plot_course}",
        hovertemplate=
            '%{x}<br>' +
            'Median: %{y:.2f}k<br>' +
            '75th Pct: %{customdata[0]:.2f}k<br>' +
            '25th Pct: %{customdata[1]:.2f}k',
        customdata=np.stack((course_data['gross_mthly_75_percentile'], course_data['gross_mthly_25_percentile']), axis=-1)
    )

    # Colormapping. Will cycle 
    agg_col_map = ['#7c6354', '#DB3F3F', '#317A41', '#222323', '#011638']

    idx = 0
    # University median line
    uni_median_trace = go.Scatter(
        x=uni_median_data['year'],
        y=uni_median_data['gross_monthly_median'],
        mode='lines',
        line=dict(dash='dot', color=agg_col_map[idx%len(agg_col_map)]),
        name=f'{plot_uni} Median', 
        hovertemplate=
            "%{x}<br>"+"%{y:.2f}k"
    )
    idx +=1

    # University 25th percentile line
    uni_25th_trace = go.Scatter(
        x=uni_median_data['year'],
        y=uni_median_data['gross_mthly_25_percentile'],
        mode='lines',
        line=dict(dash='dot', color=agg_col_map[idx%len(agg_col_map)]),
        name=f'{plot_uni} 25th Percentile', 
        hovertemplate=
            "%{x}<br>"+"%{y:.2f}k"
    )
    idx +=1

    # University 75th percentile line
    uni_75th_trace = go.Scatter(
        x=uni_median_data['year'],
        y=uni_median_data['gross_mthly_75_percentile'],
        mode='lines',
        line=dict(dash='dot', color=agg_col_map[idx%len(agg_col_map)]),
        name=f'{plot_uni} 75th Percentile', 
        hovertemplate=
            "%{x}<br>"+"%{y:.2f}k"
    )
    idx +=1
    

    # Create the figure
    fig = go.Figure(data=[course_trace, uni_median_trace, uni_75th_trace, uni_25th_trace])

    # Adding padding to the X-axis
    padding = 0.5
    x_min = course_data['year'].min() - padding
    x_max = course_data['year'].max() + padding



    # Set titles and labels
    fig.update_layout(
        # title=f"Gross Monthly Salary for {plot_course} at {plot_uni} Over Time",
        title_x=0.5,
        xaxis_title="Year",
        xaxis=dict(range = [x_min, x_max], tickmode='linear', tick0=course_data['year'].min(), dtick=1),
        yaxis_title="Gross Monthly Salary (Thousands)",
        # For legend at top
        legend=dict(orientation="h",yanchor="bottom", y=1.08,xanchor="center", x=0.5, traceorder="normal"),  
        # legend=dict(
        #     orientation="h",
        #     yanchor="top",
        #     y=-0.2,  # Move legend below x-axis
        #     xanchor="center",
        #     x=0.5,
        # )
        height=400
        , margin=dict(l=50, r=50, t=15,  b=100)
        , hovermode='x'
    )

    # Set x-axis ticks to show every year
    fig.update_xaxes(
        dtick=1  # Set tick interval to 1 year
    )

    return fig

def plot_employment_rates(selected_course:str, selected_uni:str, input_df:pd.DataFrame)->go.Figure:
    plot_course = selected_course
    plot_uni = selected_uni

    # Filter the data for the selected course
    course_data = input_df[(input_df['course'] == plot_course) & (input_df['uni'] == plot_uni) & (input_df['course_row'] == 1)].copy()

    # Filter the summary data for the university's median
    summary_data = input_df[(input_df['course'] == f"{plot_uni} Median") & (input_df['uni'] == plot_uni) & (input_df['summary_row'] == 1)].copy()

    # Create the grouped bar plot
    fig = go.Figure()

    # Add bars for 'employment_rate_ft_perm'
    fig.add_trace(go.Bar(
        x=course_data['year'],
        y=course_data['employment_rate_ft_perm'],
        name='FT Permanent',
        marker_color='indianred',
        hovertemplate='%{y:.1f}%'  # Hover template for bar plot
    ))

    # Add bars for 'employment_rate_overall'
    fig.add_trace(go.Bar(
        x=course_data['year'],
        y=course_data['employment_rate_overall'],
        name='Overall',
        marker_color='lightsalmon',
        hovertemplate='%{y:.1f}%'  # Hover template for bar plot
    ))

    # Add dotted line for 'employment_rate_ft_perm' from summary data
    fig.add_trace(go.Scatter(
        x=summary_data['year'],
        y=summary_data['employment_rate_ft_perm'],
        mode='lines',
        name=f'{selected_uni} Median FT Permanent',
        line=dict(color='royalblue', dash='dot')
    ))

    # Add dotted line for 'employment_rate_overall' from summary data
    fig.add_trace(go.Scatter(
        x=summary_data['year'],
        y=summary_data['employment_rate_overall'],
        mode='lines',
        name=f'{selected_uni} Median Overall',
        line=dict(color='darkblue', dash='dot')
    ))

    # Update layout for the legend, axes, and X-ticks
    fig.update_layout(
        barmode='group',
        # title=f"Employment Rates for {plot_course} at {plot_uni}",
        xaxis_title="Year",
        yaxis_title="Employment Rate (%)",
        # For legend at top
        legend=dict(orientation="h",yanchor="bottom", y=1.08,xanchor="center", x=0.5, traceorder="normal"),  
        # legend=dict(
        #     orientation="h",
        #     yanchor="top",
        #     y=-0.15,
        #     xanchor="center",
        #     x=0.5
        # ),
        xaxis=dict(
            tickmode='linear',  # Ensure every year is shown on X-axis
            tick0=course_data['year'].min(),
            dtick=1  # Set interval to 1 year
    
        )
        , margin=dict(l=50, r=50, t=15,  b=100)
        , hovermode='x'
    )

    return fig

