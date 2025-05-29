# introduction.py
import plotly.graph_objects as go
from dash import html, dcc
import pandas as pd

UNIFORM_SCALE = 3

# Coordinates for each ISO
coord_map = {
    "NER": (14.0, 1.5),       # Niger
    "BFA": (13.3, -1.1),      # Burkina Faso
    "RUS": (55.7558, 37.6176),# Russia
    "NGA": (11.9, 13.6),      # Nigeria
    "IRN": (30.2839, 57.0834) # Iran
}

# All 20 panels, only first 8 shown in sidebar
panels = [
    {"index": 1, "name": "Niger",         "iso": "NER", "date": "21/07/2024", "desc": "Over 300 attackers killed 237 soldiers, 21 July.", "value": 237},
    {"index": 2, "name": "Burkina Faso",  "iso": "BFA", "date": "24/08/2024", "desc": "Gunmen killed 200+ civilians in Barsalogho, 24 August.", "value": 200},
    {"index": 3, "name": "Burkina Faso",  "iso": "BFA", "date": "11/06/2024", "desc": "Attackers killed 170+ in Mansila; JNIM claimed, 11 June.", "value": 170},
    {"index": 4, "name": "Russia",        "iso": "RUS", "date": "22/03/2024", "desc": "Gunmen killed 144, wounded 551 at Moscow concert, 22 March.", "value": 144},
    {"index": 5, "name": "Burkina Faso",  "iso": "BFA", "date": "16/03/2024", "desc": "At least 100 killed in Kompienga village attacks, 16 March.", "value": 100},
    {"index": 6, "name": "Nigeria",       "iso": "NGA", "date": "01/09/2024", "desc": "Around 150 killed in Mafa market attack, 1 September.", "value": 100},
    {"index": 7, "name": "Iran",          "iso": "IRN", "date": "03/01/2024", "desc": "Two blasts killed 95, wounded 284 in Kerman; IS-K claimed, 3 January.", "value": 95},
    {"index": 8, "name": "Iran",          "iso": "IRN", "date": "03/01/2024", "desc": "Second Kerman blast killed 95, wounded similar, 3 January.", "value": 95},
    {"index": 9, "name": "Nigeria",       "iso": "NGA", "date": "24/04/2024", "desc": "ISWA–Boko Haram clash killed 85 fighters, 24–26 April.", "value": 85},
    {"index": 10, "name": "Burkina Faso", "iso": "BFA", "date": "22/05/2024", "desc": "JNIM attack killed 70 civilians in Goubre, 22 May.", "value": 70},
    {"index": 11, "name": "Burkina Faso", "iso": "BFA", "date": "30/06/2024", "desc": "Gunmen killed 70 soldiers in Partiaga camp attack, 30 June.", "value": 70},
    {"index": 12, "name": "Mali",         "iso": "MLI", "date": "17/09/2024", "desc": "JNIM attack killed 60 soldiers at Bamako school, 17 September.", "value": 60},
    {"index": 13, "name": "Syria",        "iso": "SYR", "date": "10/12/2024", "desc": "Assailants killed 54 regime soldiers near Kaziya, 10 December.", "value": 54},
    {"index": 14, "name": "Burkina Faso", "iso": "BFA", "date": "07/02/2024", "desc": "Gunmen killed 50 civilians in Galgnoini, 7 February.", "value": 50},
    {"index": 15, "name": "Niger",        "iso": "NER", "date": "25/06/2024", "desc": "JNIM attack killed 47 soldiers in Gotheye, 25 June.", "value": 47},
    {"index": 16, "name": "Burkina Faso", "iso": "BFA", "date": "29/05/2024", "desc": "JNIM attack killed 46 in Kogo, 29 May.", "value": 46},
    {"index": 17, "name": "Burkina Faso", "iso": "BFA", "date": "26/06/2024", "desc": "JNIM attack killed 45 police in Yourkoudguen, 26 June.", "value": 45},
    {"index": 18, "name": "Burkina Faso", "iso": "BFA", "date": "26/06/2024", "desc": "Attack killed 45 civilians in Boanekuy, 26 June.", "value": 45},
    {"index": 19, "name": "Democratic Republic of the Congo", "iso": "COD", "date": "12/06/2024", "desc": "IS attack killed 42 civilians in Mayikengo, 12 June.", "value": 42},
    {"index": 20, "name": "Democratic Republic of the Congo", "iso": "COD", "date": "07/06/2024", "desc": "IS attack killed 41 civilians in Beni territory, 7 June.", "value": 41},
]

# Compute global min/max for values
values = [p['value'] for p in panels]
min_val, max_val = min(values), max(values)

def value_to_color(val):
    ratio = (val - min_val) / (max_val - min_val) if max_val > min_val else 0
    gb = int(255 * (1 - ratio))
    return f'rgb(255,{gb},{gb})'

# Enrich panels with lat/lon and panel_color
for i, panel in enumerate(panels):
    panel['lat'], panel['lon'] = coord_map.get(panel['iso'], (0, 0))
    panel['panel_color'] = value_to_color(panel['value'])

all_countries = {f"{c['iso']}-{i}": c for i, c in enumerate(panels)}
first_eight_keys = list(all_countries.keys())[:10]

# Build choropleth map with optional zoom
def make_map(selected_iso_key=None):
    # Aggregate highest value per country
    df = pd.DataFrame(
        [(iso, max([p['value'] for p in panels if p['iso']==iso]),
          next(p['name'] for p in panels if p['iso']==iso))
         for iso in set([p['iso'] for p in panels])],
        columns=['iso','z','country']
    )
    df['values'] = df['iso'].apply(lambda x: ', '.join(str(p['value']) for p in panels if p['iso']==x))

    red_scale = [[0.0, 'rgb(255,240,240)'], [0.5, 'rgb(255,150,150)'], [1.0, 'rgb(255,0,0)']]
    fig = go.Figure(go.Choropleth(
        locations=df['iso'], z=df['z'], colorscale=red_scale,
        marker_line_color='white', marker_line_width=0.5,
        customdata=df[['country','values']].values,
        hovertemplate='<b>%{location}: %{customdata[0]}</b><br>Values: %{customdata[1]}<extra></extra>',
        colorbar=dict(lenmode='fraction', len=0.8, y=0.5, yanchor='middle', thickness=20)
    ))

    # Default geo settings
    fig.update_geos(showframe=False, showcountries=True,
                    projection_type='natural earth')

    # If selection, highlight and zoom
    if selected_iso_key:
        selected = all_countries[selected_iso_key]
        # Highlight with yellow overlay
        fig.add_trace(go.Choropleth(
            locations=[selected['iso']], z=[selected['value']], showscale=False,
            colorscale=[[0,'rgba(255,255,0,0.6)'],[1,'rgba(255,255,0,0.6)']],
            marker_line_color='black', marker_line_width=2
        ))
        # Center and zoom (x2 scale)
        fig.update_geos(
            center={'lat': selected['lat'], 'lon': selected['lon']},
            projection_scale=UNIFORM_SCALE * 2,
            visible=False
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20), autosize=True
    )

    desc = all_countries[selected_iso_key]['desc'] if selected_iso_key else ''
    return fig, desc

# Sidebar panel creator (unchanged)
def create_panel(panel, key):
    return html.Div(
        id={'type': 'country-btn', 'key': key}, n_clicks=0,
        style={
            'display': 'flex', 'alignItems': 'center', 'borderRadius': '4px',
            'padding': '4px 8px', 'marginBottom': '4px', 'cursor': 'pointer',
            'backgroundColor': panel['panel_color'], 'width': '100%'
        },
        children=[
            html.Div(
                str(panel['index']),
                style={
                    'width': '24px', 'height': '24px', 'borderRadius': '50%',
                    'backgroundColor': 'white', 'display': 'flex', 'alignItems': 'center',
                    'justifyContent': 'center', 'fontWeight': 'bold',
                    'marginRight': '6px', 'fontSize': '0.85rem', 'color': 'black'
                }
            ),
            html.Div([
                f"{panel['name']} ({panel['value']})", html.Br(), panel['date']
            ], style={'fontSize': '0.85rem', 'color': 'black'})
        ]
    )



# Layout: introduction section with sidebar and map
layout_actual_statistics = html.Section(
    id='introduction',
    style={'width': '100%', 'height': '100vh', 'padding': '16px', 'boxSizing': 'border-box'},
    children=[
        html.H1(
            'Actual Staistics',
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
        html.Div(
            style={'display': 'flex', 'height': 'calc(100% - 80px)'},
            children=[
                html.Div(
                    [create_panel(all_countries[k], k) for k in first_eight_keys],
                    style={
                        'width': '20%',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'overflowY': 'auto',
                        'paddingRight': '16px'
                    }
                ),
                html.Div(
                    style={'width': '80%', 'display': 'flex', 'flexDirection': 'column'},
                    children=[
                        html.Div(
                            id='map-desc',
                            style={
                                'textAlign': 'center',
                                'padding': '8px',
                                'fontSize': '1.1rem',
                                'fontWeight': 'bold',
                                'color': 'black'
                            }
                        ),
                        dcc.Graph(
                            id='world-map',
                            figure=make_map()[0],
                            style={'flex': 1, 'height': '100%'}
                        )
                    ]
                )
            ]
        )
    ]
)