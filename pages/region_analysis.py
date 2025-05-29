import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

# Load and process data
data = pd.read_pickle('data/processed/cleaned_data.pkl')

# 1) Chuẩn hoá attack_type: strip và map nếu cần gom chung
data['attack_type'] = data['attack_type'].str.strip()

# Abbreviation and full-name mapping for regions
abbr_map = {
    'South Asia': 'SA',
    'Middle East & North Africa': 'MENA',
    'Sub-Saharan Africa': 'SSA',
    'Southeast Asia': 'SEA',
    'Western Europe': 'WE',
    'North America': 'NA',
    'Central America & Caribbean': 'CAC',
    'East Asia': 'EA',
    'Eastern Europe': 'EE',
    'South America': 'SAM',
    'Australasia & Oceania': 'A&O',
    'Central Asia': 'CA'
}
full_map = {v: k for k, v in abbr_map.items()}

data['region_abbr'] = data['region_txt'].map(abbr_map).fillna(data['region_txt'])
data['region_full'] = data['region_abbr'].map(full_map).fillna(data['region_txt'])

# --- Sunburst (Pie) --- #
sunburst_df = (
    data[['region_abbr','region_full','country_txt']]
    .groupby(['region_abbr','region_full','country_txt'])
    .size().reset_index(name='attack_sum')
)
fig3 = px.sunburst(
    sunburst_df,
    path=['region_abbr','country_txt'],
    values='attack_sum',
    color='attack_sum',
    color_continuous_scale=px.colors.sequential.Reds,
    template='plotly_white',
    custom_data=['region_abbr','region_full']
)
fig3.update_traces(domain=dict(x=[0.1, 1], y=[0,1]))
fig3.update_traces(
    textinfo='label',
    insidetextorientation='radial'
)
fig3.update_traces(
    hovertemplate="Region: %{customdata[1]}<br>Attacks: %{value:,}".replace(',', ' ')
)
fig3.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font_color='black',
    font=dict(family='Arial, sans-serif'),
    margin=dict(t=20, b=20, l=10, r=10),
    coloraxis_colorbar=dict(
        yanchor='top', y=0.9, x=-0.3, xanchor='left', orientation='v',
        lenmode='fraction', len=0.8,
        title='Attacks', title_font_size=12, tickfont_size=12
    )
)

# --- Bar chart data & function --- #
type_df = (
    data[['region_abbr','region_full','attack_type']]
    .groupby(['region_abbr','region_full','attack_type'])
    .size().reset_index(name='count')
)

def make_bar(selected_region=None):
    df = type_df.copy()
    if selected_region is None:
        df['opacity'] = 1.0
    else:
        df['opacity'] = df['region_abbr'].apply(
            lambda x: 1.0 if x == selected_region else 0.2
        )

    fig = px.bar(
        df, x='count', y='region_abbr', color='attack_type', orientation='h',
        template='plotly_white',
        color_discrete_sequence=px.colors.sequential.Reds,
        custom_data=['region_full','attack_type']
    )
    fig.update_traces(
        marker_opacity=df['opacity'],
        hovertemplate=(
            "Attack Type: %{customdata[1]}<br>"
            "Count: %{x:,}"
            "<extra></extra>"
        )
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=30, r=10), barmode='stack', font_color='black',
        font=dict(family='Arial, sans-serif'),
        yaxis={'categoryorder':'total descending'},
        legend_title_text='Attack Type', legend_title_font_size=12, legend_font_size=12,
        xaxis=dict(tickfont=dict(size=12))
    )
    return fig

initial_bar = make_bar()

layout_region_analysis = html.Section(
    id='regional',
    style={'width': '100%', 'height': '100vh', 'padding': '16px', 'boxSizing': 'border-box'},
    children=[
        html.Div([
            html.H1(
                'Region Analysis',
                style={
                    'textAlign': 'left',
                    'fontSize': '2.5rem',
                    'fontWeight': 'bold',
                    'color': 'rgb(200, 0, 0)',
                    'borderBottom': '3px solid rgb(200, 0, 0)',
                    'paddingBottom': '4px',
                    'marginBottom': '20px',
                    'fontFamily': 'Arial, sans-serif'
                }
            )
        ], style={'marginBottom': '1rem', 'textAlign': 'left'}),
        html.Div(
            style={
                'display':'flex', 'alignItems':'start', 'columnGap':'20px'
            },
            children=[
                html.Div([
                    html.Div('Attack By Region', style={
                        'fontSize':'12px','fontWeight':'bold','marginBottom':'4px', 'fontFamily': 'Arial, sans-serif'}),
                    dcc.Graph(
                        id='sunburst', figure=fig3,
                        style={'width':'100%','height':'60vh'}
                    )
                ], style={'width':'36%'}),

                html.Div([
                    html.Div('Attack Type By Region', style={
                        'fontSize':'12px','fontWeight':'bold','marginBottom':'4px', 'fontFamily': 'Arial, sans-serif'}),
                    dcc.Graph(
                        id='bar-chart', figure=initial_bar,
                        style={'width':'100%','height':'60vh'}
                    )
                ], style={'width':'60%'}),
            ]
        )
    ]
)