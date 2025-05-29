import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np
from copy import deepcopy

# Load and process data
data = pd.read_pickle('data/processed/cleaned_data.pkl')

# ================= PREPARE CHOROPLETH DATA =================
choropleth_data = (
    data[['year', 'country_code', 'country_txt', 'total_casualties']]
    .rename(columns={'country_txt': 'Country'})
    .groupby(['year', 'country_code', 'Country'])['total_casualties']
    .sum()
    .reset_index()
)

total_by_country = (
    choropleth_data
    .groupby(['country_code', 'Country'])['total_casualties']
    .sum()
    .reset_index()
)

# COMMON LAYOUT PROPERTIES
common_geo = dict(
    showland=True,
    landcolor='lightgray',
    domain=dict(x=[0, 1], y=[0.12, 1]),
    center=dict(lon=0, lat=20),  # fixed map center
    projection_scale=1.15       # fixed zoom level
)
common_colorbar = dict(
    len=0.5,
    y=0.5,
    title_side='top',
    title_font=dict(size=12, family='Arial, sans-serif'),
    tickfont=dict(size=10, family='Arial, sans-serif')
)
common_layout = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=0, b=0, l=0, r=0),
    coloraxis_colorbar=common_colorbar,
    font=dict(color='black', family='Arial, sans-serif'),
    uirevision='choromap',        # preserve view on callback
    autosize=True                 # let container control size
)

# ================= FIGURE 1: Total Casualties Static Map =================
fig1 = px.choropleth(
    total_by_country,
    locations='country_code',
    color='total_casualties',
    hover_name='Country',
    range_color=(0, total_by_country['total_casualties'].max()),
    color_continuous_scale=px.colors.sequential.Reds,
    labels={'total_casualties': 'Total Casualties'},
    template='plotly_white'
)
fig1.update_layout(**common_layout)
fig1.update_geos(**common_geo)
fig1.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Total Casualties: %{z:.0f}<extra></extra>",
    hoverlabel=dict(font=dict(family='Arial, sans-serif'))
)

# ================= FIGURE 2: Yearly Casualties Animated Map =================
fig2 = px.choropleth(
    choropleth_data,
    locations='country_code',
    color='total_casualties',
    hover_name='Country',
    animation_frame='year',
    range_color=(0, choropleth_data['total_casualties'].max()),
    color_continuous_scale=px.colors.sequential.Reds,
    labels={'total_casualties': 'Yearly Casualties'},
    template='plotly_white'
)
fig2.update_layout(**common_layout)
fig2.update_geos(**common_geo)
fig2.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Total Casualties: %{z:.0f}<extra></extra>",
    hoverlabel=dict(font=dict(family='Arial, sans-serif'))
)
fig2.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 120
fig2.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 30
fig2.layout.sliders[0].y = 0.05
fig2.layout.sliders[0].yanchor = 'bottom'
fig2.layout.updatemenus[0].y = 0.12
fig2.layout.updatemenus[0].yanchor = 'bottom'

# ================= FIGURE 3: Correlation Heatmap =================
numeric_cols = data.select_dtypes(include='number')
corr_matrix = numeric_cols.corr().round(2)
fig_corr = px.imshow(
    corr_matrix,
    text_auto=True,
    color_continuous_scale='Reds',
    labels=dict(color='Correlation'),
    template='plotly_white'
)
fig_corr.update_layout(
    title={'text': '<b>Correlation Matrix</b>', 'x': 0.5, 'xanchor': 'center', 'font': {'family': 'Arial, sans-serif'}},
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, b=20, l=10, r=10),
    coloraxis_colorbar=common_colorbar,
    font=dict(color='black', family='Arial, sans-serif')
)
fig_corr.update_traces(
    hovertemplate="<b>%{x} x %{y}</b><br>Correlation: %{z:.2f}<extra></extra>",
    hoverlabel=dict(font=dict(family='Arial, sans-serif'))
)

# ================= PAGE LAYOUT =================
layout_quantitative_analysis = html.Section(
    id='quantitative',
    style={'width': '100%', 'height': '100vh', 'padding': '16px', 'boxSizing': 'border-box'},
    children=[
        html.H1('Quantitative Analysis', style={
                'textAlign': 'left',
                'fontSize': '2.5rem',
                'fontWeight': 'bold',
                'color': 'rgb(200, 0, 0)',
                'borderBottom': '3px solid rgb(200, 0, 0)',
                'paddingBottom': '4px',
                'marginBottom': '20px',
                'fontFamily': 'Arial, sans-serif'
            }),
        html.Div(
            dcc.Dropdown(
                id='figure-dropdown',
                options=[
                    {'label': 'Total Casualties', 'value': 'fig1'},
                    {'label': 'Yearly Casualties', 'value': 'fig2'},
                ],
                value='fig1', clearable=False,
                style={'color': 'black', 'width': '50%', 'fontFamily': 'Arial, sans-serif'}
            ),
            style={'display': 'flex', 'justifyContent': 'center', 'margin': '20px 0'}
        ),
        html.Div(
            children=[
                html.Div(
                    dcc.Graph(
                        id='selected-figure',
                        figure=fig1,
                        className='dcc-graph',
                        style={'height': '70vh'}
                    ),
                    style={'width': '50%', 'display': 'inline-block', 'boxSizing': 'border-box', 'paddingRight': '8px'}
                ),
                html.Div(
                    dcc.Graph(
                        figure=fig_corr,
                        className='dcc-graph',
                        style={'height': '70vh'}
                    ),
                    style={'width': '50%', 'display': 'inline-block', 'boxSizing': 'border-box', 'paddingLeft': '8px'}
                )
            ],
            style={'display': 'flex', 'width': '100%'}
        )
    ]
)

@callback(
    Output('selected-figure', 'figure'),
    Input('figure-dropdown', 'value')
)
def update_quantitative_figure(val):
    return deepcopy(fig1) if val == 'fig1' else deepcopy(fig2)
