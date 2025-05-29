import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import numpy as np

# Load and preprocess data
df = pd.read_pickle('data/processed/cleaned_data.pkl')
if 'prorperty_damage' in df.columns:
    df.rename(columns={'prorperty_damage': 'property_damage'}, inplace=True)
df['property_damage'] = df['property_damage'].fillna(0).apply(lambda x: max(x, 0))
year_col, region_col = 'year', 'region_txt'
df[year_col] = pd.to_datetime(df[year_col], format='%Y').dt.year

# Precompute aggregates
df_attacks = df.groupby([year_col, region_col]).size().reset_index(name='total_attacks')
df_stats = df.groupby([year_col, region_col]).agg(
    total_killed=('total_killed', 'sum'),
    total_wounded=('total_wounded', 'sum'),
    property_damage=('property_damage', 'sum')
).reset_index()

# Ensure grid of all years and regions
all_years = pd.DataFrame({year_col: range(df[year_col].min(), df[year_col].max() + 1)})
all_regions = pd.DataFrame({region_col: df[region_col].unique()})
grid = pd.MultiIndex.from_product(
    [all_years[year_col], all_regions[region_col]],
    names=[year_col, region_col]
).to_frame(index=False)

# Merge and fill
merged = (
    grid
    .merge(df_attacks, on=[year_col, region_col], how='left')
    .merge(df_stats,   on=[year_col, region_col], how='left')
    .fillna({
        'total_attacks': 0,
        'total_killed': 0,
        'total_wounded': 0,
        'property_damage': 0
    })
)

# Pivot for wide format
pivot = merged.pivot(
    index=year_col,
    columns=region_col,
    values=['total_attacks', 'total_killed', 'total_wounded', 'property_damage']
).fillna(0)
regions = sorted(pivot.columns.levels[1])

# Custom abbreviations for region labels
abbr_map = {
    'Australasia & Oceania':   ' Aus & Ocenia',
    'Central America & Caribbean': ' Central America & Caribbean',
    'Central Asia':            ' Central Asia',
    'East Asia':               ' East Asia',
    'Eastern Europe':          ' East Europe',
    'Middle East & North Africa': ' Middle East & North Africa',
    'North America':           ' North America',
    'South America':           ' South America',
    'South Asia':              ' South Asia',
    'Southeast Asia':          ' Southeast Asia',
    'Sub-Saharan Africa':      ' Sub-Saharan Africa',
    'Western Europe':          ' Western Europe'
}

# Color mapping
colors = px.colors.qualitative.Plotly
color_map = {reg: colors[i % len(colors)] for i, reg in enumerate(regions)}

def make_aggregates(df):
    # Tạo bảng merged + pivot giống hệt phần đầu
    df_attacks = df.groupby([year_col, region_col]).size().reset_index(name='total_attacks')
    df_stats = df.groupby([year_col, region_col]).agg(
        total_killed=('total_killed', 'sum'),
        total_wounded=('total_wounded', 'sum'),
        property_damage=('property_damage', 'sum')
    ).reset_index()

    grid = pd.MultiIndex.from_product(
        [range(df[year_col].min(), df[year_col].max()+1), regions],
        names=[year_col, region_col]
    ).to_frame(index=False)

    merged = (
        grid
        .merge(df_attacks, on=[year_col, region_col], how='left')
        .merge(df_stats,   on=[year_col, region_col], how='left')
        .fillna(0)
    )

    pivot = merged.pivot(index=year_col,
                         columns=region_col,
                         values=['total_attacks','total_killed','total_wounded','property_damage']
                        ).fillna(0)
    return pivot

def create_figure(data, title):
    fig = px.area(
        data,
        x=data.index,
        y=data.columns,
        title=f'<b>{title}</b>',
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig.update_traces(
        showlegend=False,
        hovertemplate=(
            'Region: %{fullData.name}<br>'
            'Year: %{x}<br>'
            'Value: %{y}<extra></extra>'
        )
    )
    fig.update_layout(
        title={'text': f'<b>{title}</b>', 'x':0.5, 'font':{'size':12,'color':'#000'}},
        margin=dict(l=0,r=0,t=30,b=20),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showline=True,linecolor='#333',gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(showline=True,linecolor='#333',gridcolor='rgba(0,0,0,0.1)'),
        font_color='#333'
    )
    return fig


# Initialize figures
fig1 = create_figure(pivot['total_attacks'], 'Number of Terrorist Attacks')
fig2 = create_figure(pivot['total_killed'], 'Number of Fatalities Caused')
fig3 = create_figure(pivot['total_wounded'], 'Number of People Wounded')
fig4 = create_figure(pivot['property_damage'], 'Estimated Property Damage (USD)')

layout_time_analysis = html.Section(
    id='time',
    style={'width': '100%', 'height': '100vh', 'padding': '16px', 'boxSizing': 'border-box'},
    children=[
        html.H2(
            'Time Dashboard',
            className='section-title',
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
        ),

        # Div bao bên ngoài để chia 3 cột: controls + 2 cột đồ thị
        html.Div(
            children=[
                # Column 1: Controls (radio + checklist)
                html.Div([
                    html.Label('Select Status:', className='label', style={'fontWeight': 'bold', 'fontSize': '12px'}),
                    dcc.RadioItems(
                        id='success-radioitems',
                        options=[
                            {'label': ' All',          'value': 'All'},
                            {'label': ' Successful',  'value': 'Successful'},
                            {'label': ' Unsuccessful','value': 'Unsuccessful'}
                        ],
                        value='All',
                        style={
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '4px',
                            'fontSize': '12px'
                        }
                    ),

                    html.Label('Filter by Region:', className='label', style={'marginTop': '12px', 'fontWeight': 'bold', 'fontSize': '12px'}),
                    dcc.Checklist(
                        id='region-checklist',
                        options=[{'label': abbr_map.get(reg, reg), 'value': reg} for reg in regions],
                        value=regions,
                        style={
                            'display': 'flex',
                            'flexDirection': 'column',
                            'gap': '4px',
                            'fontSize': '12px',
                            'maxHeight': '400px',
                            'overflowY': 'auto'  # nếu danh sách region dài thì cuộn được
                        }
                    )
                ],
                style={
                    'padding': '10px',
                    'border': '1px solid #ddd',
                    'borderRadius': '4px',
                    'backgroundColor': '#fff'
                }
),

                # Column 2: 2 đồ thị (số vụ tấn công + số người chết)
                html.Div([
                    dcc.Graph(
                        id='graph-attacks', 
                        figure=fig1,
                        style={'height': '270px', 'width': '100%', 'margin': '0'}
                    ),
                    dcc.Graph(
                        id='graph-fatalities', 
                        figure=fig2,
                        style={'height': '270px', 'width': '100%', 'margin': '0'}
                    ),
                ],
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '12px'
                }
                ),

                # Column 3: 2 đồ thị (số người bị thương + thiệt hại tài sản)
                html.Div([
                    dcc.Graph(
                        id='graph-injuries', 
                        figure=fig3,
                        style={'height': '270px', 'width': '100%', 'margin': '0'}
                    ),
                    dcc.Graph(
                        id='graph-damage', 
                        figure=fig4,
                        style={'height': '270px', 'width': '100%', 'margin': '0'}
                    ),
                ],
                style={
                    'display': 'flex',
                    'flexDirection': 'column',
                    'gap': '12px'
                }
                ),
            ],
            style={
                'display': 'grid',
                'gridTemplateColumns': '200px 1fr 1fr',  # Cột 1 rộng 220px, cột 2 và 3 chia đều phần còn lại
                'gap': '20px',                           # Khoảng cách giữa 3 cột
                'alignItems': 'start'
            }
        )
    ]
)


@callback(
    Output('graph-attacks',    'figure'),
    Output('graph-fatalities', 'figure'),
    Output('graph-injuries',   'figure'),
    Output('graph-damage',     'figure'),
    Input('region-checklist',  'value'),
    Input('success-radioitems','value'),
)
def update_all(selected_regions, selected_status):
    # 1) Lọc theo status
    if selected_status != 'All':
        df_filtered = df[df['success'] == selected_status]
    else:
        df_filtered = df.copy()

    # 2) Lọc theo region
    df_filtered = df_filtered[df_filtered[region_col].isin(selected_regions)]

    # 3) Tạo lại pivot
    pivot_filtered = make_aggregates(df_filtered)

    # 4) Trả về 4 figure
    fig1 = create_figure(pivot_filtered['total_attacks'], 'Number of Terrorist Attacks')
    fig2 = create_figure(pivot_filtered['total_killed'], 'Number of Fatalities Caused')
    fig3 = create_figure(pivot_filtered['total_wounded'], 'Number of People Wounded')
    fig4 = create_figure(pivot_filtered['property_damage'], 'Estimated Property Damage')
    return fig1, fig2, fig3, fig4