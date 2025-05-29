import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# Chuẩn bị dữ liệu
df = pd.read_pickle('data/processed/cleaned_data.pkl')

# Custom màu
my_reds = [
    '#ffb3b3', '#ff6666', '#ff4d4d', '#ff0000', '#b30000', '#660000'
]

def make_group_fig(df_region):
    unk_group = df_region[df_region['te_group'] != 'Unknown']
    grp = unk_group.groupby('te_group')['civ_killed'].sum().nlargest(5).reset_index()
    fig = px.bar(
        grp, x='civ_killed', y='te_group', orientation='h',
        labels={'te_group': 'Group', 'civ_killed': 'Civilians Killed'},
        color='civ_killed', color_continuous_scale=my_reds,
        template='plotly_white'
    )
    fig.update_layout(
        font=dict(family='Arial, sans-serif', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    fig.update_coloraxes(showscale=False)
    fig.update_traces(hovertemplate='Group: %{y}<br>Civilians Killed: %{x}<extra></extra>')
    return fig

def make_weapon_fig(df_region):
    series = df_region[df_region['weapon_type']!='Unknown']['weapon_type'].value_counts().nlargest(5)
    top5 = series.rename_axis('weapon_type').reset_index(name='attacks')
    fig = px.bar(
        top5, x='attacks', y='weapon_type', orientation='h',
        labels={'weapon_type': 'Weapon', 'attacks': 'Number of Attacks'},
        color='attacks', color_continuous_scale=my_reds,
        template='plotly_white'
    )
    fig.update_layout(
        font=dict(family='Arial, sans-serif', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    fig.update_coloraxes(showscale=False)
    fig.update_traces(hovertemplate='Weapon: %{y}<br>Number of Attacks: %{x}<extra></extra>')
    return fig

def make_pie_target(df_region):
    cnt = df_region['target_type'].value_counts()
    top = cnt.head(5).to_dict(); top['Others'] = cnt.iloc[5:].sum()
    fig = px.pie(
        names=list(top.keys()), values=list(top.values()), hole=0.4,
        color_discrete_sequence=my_reds, template='plotly_white'
    )
    fig.update_layout(font=dict(family='Arial, sans-serif', size=12), margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(hovertemplate='%{label}<br>Count: %{value}<br>Percent: %{percent}<extra></extra>')
    return fig

def make_pie_attack(df_region):
    cnt = df_region['attack_type'].value_counts()
    top = cnt.head(5).to_dict(); top['Others'] = cnt.iloc[5:].sum()
    fig = px.pie(
        names=list(top.keys()), values=list(top.values()), hole=0.4,
        color_discrete_sequence=my_reds, template='plotly_white'
    )
    fig.update_layout(font=dict(family='Arial, sans-serif', size=12), margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(hovertemplate='%{label}<br>Count: %{value}<br>Percent: %{percent}<extra></extra>')
    return fig

def make_treemap(df):
    succ = df[df['success'] == 1].groupby('region_txt').size().reset_index(name='total')
    fail = df[df['success'] == 0].groupby('region_txt').size().reset_index(name='total')
    df_tm = pd.concat([
        pd.DataFrame({'region_txt': succ['region_txt'], 'status': 'Success', 'total': succ['total']}),
        pd.DataFrame({'region_txt': fail['region_txt'], 'status': 'Failure', 'total': fail['total']})
    ], ignore_index=True)

    fig = px.treemap(df_tm, path=['region_txt', 'status'], values='total', color='total',
                     color_continuous_scale=my_reds, template='plotly_white')

    fig.update_layout(font=dict(family='Arial, sans-serif', size=12), margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(insidetextfont=dict(size=12),
                      hovertemplate='<b>%{label}</b><br>Value: %{value}<extra></extra>')
    return fig

fig_grp = make_group_fig(df)
fig_wpn = make_weapon_fig(df)
fig_pie_t = make_pie_target(df)
fig_pie_a = make_pie_attack(df)
fig_tm = make_treemap(df)

layout_global_overview = html.Section(
    id='home', className='container-fluid',
    style={'width': '100%', 'height': '100vh', 'padding': '16px', 'boxSizing': 'border-box'},
    children=[
        html.Div([
            html.H1('Global Overview', style={
                'textAlign': 'left', 'fontSize': '2.5rem', 'fontWeight': 'bold',
                'color': 'rgb(200, 0, 0)', 'borderBottom': '3px solid rgb(200, 0, 0)',
                'paddingBottom': '4px', 'marginBottom': '10px', 'fontFamily': 'Arial, sans-serif'
            })
        ], style={'marginBottom': '0.5rem', 'textAlign': 'left'}),

        dbc.Row([
            dbc.Col(html.Div("Total Attacks by Region", style={
                'writingMode': 'vertical-rl', 'textOrientation': 'mixed',
                'fontSize': '12px', 'fontWeight': 'bold', 'marginRight': '0.5rem',
                'fontFamily': 'Arial, sans-serif'
            }), width='auto'),
            dbc.Col(html.Div(dcc.Graph(id='treemap', figure=fig_tm, config={'displayModeBar': False},
                style={'height': '30vh', 'width': '72%', 'margin': '0 auto', 'fontWeight': 'bold', 'align': 'center'}),
                style={'display': 'flex', 'justifyContent': 'center'}), width=True)
        ], className='mb-3', align='center'),

        dbc.Row([
            dbc.Col(html.Div("Target Type Distribution", style={
                'fontWeight':'bold', 'fontSize':'12px', 'marginBottom':'0.1rem', 'textAlign': 'center',
                'fontFamily': 'Arial, sans-serif'
            }), md=6),
            dbc.Col(html.Div("Top 5 Terrorist Groups by Civilians Killed", style={
                'fontWeight':'bold', 'fontSize':'12px', 'marginBottom':'0.1rem', 'textAlign': 'center',
                'fontFamily': 'Arial, sans-serif'
            }), md=6)
        ], className='mb-1'),

        dbc.Row([
            dbc.Col(dcc.Graph(id='pie-target', figure=fig_pie_t, config={'displayModeBar': False},
                style={'height': '22vh', 'width': '80%', 'margin': '0 auto', 'display': 'block'}), md=6),
            dbc.Col(dcc.Graph(id='bar-group', figure=fig_grp, config={'displayModeBar': False},
                style={'height': '22vh', 'width': '80%', 'margin': '0 auto', 'display': 'block'}), md=6)
        ], className='mb-2'),

        dbc.Row([
            dbc.Col(html.Div("Attack Type Distribution", style={
                'fontWeight':'bold', 'fontSize':'12px', 'marginBottom':'0.1rem', 'textAlign': 'center',
                'fontFamily': 'Arial, sans-serif'
            }), md=6),
            dbc.Col(html.Div("Top 5 Weapons by Number of Attacks", style={
                'fontWeight':'bold', 'fontSize':'12px', 'marginBottom':'0.1rem', 'textAlign': 'center',
                'fontFamily': 'Arial, sans-serif'
            }), md=6)
        ], className='mb-1'),

        dbc.Row([
            dbc.Col(dcc.Graph(id='pie-attack', figure=fig_pie_a, config={'displayModeBar': False},
                style={'height': '22vh', 'width': '80%', 'margin': '0 auto', 'display': 'block'}), md=6),
            dbc.Col(dcc.Graph(id='bar-weapon', figure=fig_wpn, config={'displayModeBar': False},
                style={'height': '22vh', 'width': '80%', 'margin': '0 auto', 'display': 'block'}), md=6)
        ], className='mb-0')
    ]
)
