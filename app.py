import json
from dash import Dash, html, dcc, Input, Output, State, ALL, callback_context
import dash_bootstrap_components as dbc

# Import các trang hiện có
from pages.actual_statistics import layout_actual_statistics, make_map
from pages.global_overview import layout_global_overview, df, make_group_fig, make_weapon_fig, make_pie_target, make_pie_attack, make_treemap
from pages.time_analysis import layout_time_analysis

# Import các trang mới bạn cung cấp
from pages.region_analysis import layout_region_analysis   # file regional_overview.py
from pages.quantitative_analysis import layout_quantitative_analysis  # file quantitative_analysis.py

# Khởi tạo app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server
app.title = "Fighting Terrorism: A Global Dashboard Analysis"

# Custom index để điều khiển scroll-opacity (giữ nguyên)
app.index_string = '''
<!DOCTYPE html>
<html>
  <head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <script>
      window.addEventListener('scroll', function(){
        var scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        var textOpacity = scrollTop>0 ? 1 : 0.1;
        document.querySelectorAll('.hero-text, .hero-image')
          .forEach(el => el.style.opacity = textOpacity);
        var overlay = scrollTop<=0? 0 :
          Math.min(Math.max(0.6 + (scrollTop/maxScroll)*0.2, 0), 0.8);
        document.documentElement.style.setProperty('--overlay-opacity', overlay);
      });
    </script>
  </head>
  <body>
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
  </body>
</html>
'''

# Sidebar và Hero (fix typo, cải thiện mô tả các anchor)
sidebar = html.Div([
    html.A("Actual Statistics", href="#Actual-Statistic", className="page-button"),
    html.A("Global Overview", href="#Global-Overview", className="page-button"),
    html.A("Region Analysis", href="#Region-Analysis", className="page-button"),
    html.A("Time Analysis", href="#Time-Analysis", className="page-button"),
    html.A("Quantitative Analysis", href="#Quantitative-Analysis", className="page-button")
], className="sidebar", id="sidebar")

hero = html.Section([
    html.Div([
        html.H1("Terrorism Worldwide Analysis Dashboard", className="title"),
        html.P([
            "*According to the Global Terrorism Index 2025 ",
            html.A("[1]", href="https://www.visionofhumanity.org/wp-content/uploads/2025/03/Global-Terrorism-Index-2025.pdf", target="_blank"),
            " report, the number of countries recording at least one terrorist attack rose from 58 to 66, demonstrating that the threat is spreading more widely than ever.*"
        ], style={"font-size":"1.25rem","color":"#000"})
    ], className="hero-text"),
    html.Div([
        html.Img(src=app.get_asset_url("terrorism_map.png"), alt="Terrorism Overview")
    ], className="hero-image")
], className="hero")

# Thêm các div anchor để scroll đúng vị trí
layout_actual_statistics.children.insert(0, html.Div(id="Actual-Statistic"))
layout_global_overview.children.insert(0, html.Div(id="Global-Overview"))
layout_region_analysis.children.insert(0, html.Div(id="Region-Analysis"))
layout_time_analysis.children.insert(0, html.Div(id="Time-Analysis"))
layout_quantitative_analysis.children.insert(0, html.Div(id="Quantitative-Analysis"))

# Kết hợp toàn bộ layout
app.layout = html.Div([
    hero,
    sidebar,
    html.Main([
        layout_actual_statistics,
        layout_global_overview,
        layout_region_analysis,
        layout_time_analysis,
        layout_quantitative_analysis,
    ], className="content")
], className="app")

# Callback để zoom và highlight trên choropleth map khi click panel
@app.callback(
    [Output("world-map", "figure"), Output("map-desc", "children")],
    [Input({"type": "country-btn", "key": ALL}, "n_clicks")],
    [State({"type": "country-btn", "key": ALL}, "id")]
)
def update_map(n_clicks_list, ids):
    ctx = callback_context
    if not ctx.triggered or all(n is None or n == 0 for n in n_clicks_list):
        fig, _ = make_map()
        return fig, ""
    raw = ctx.triggered[0]["prop_id"].split('.')[0]
    key = json.loads(raw)["key"]
    fig, desc = make_map(selected_iso_key=key)
    return fig, desc

# Callback cho dashboard Home
@app.callback(
    [Output('bar-group', 'figure'), Output('bar-weapon', 'figure'),
     Output('pie-target', 'figure'), Output('pie-attack', 'figure')],
    Input('treemap', 'clickData')
)
def update_charts(clickData):
    df_region = df.copy()
    if clickData and clickData.get('points'):
        pt = clickData['points'][0]
        raw_id = pt.get('id') or pt.get('label')
        path = raw_id.split('/') if raw_id else []
        if path:
            df_region = df[df['region_txt'] == path[0]]
        if len(path) > 1:
            df_region = df_region[df_region['success'] == (1 if path[1] == 'Success' else 0)]
    return (
        make_group_fig(df_region),
        make_weapon_fig(df_region),
        make_pie_target(df_region),
        make_pie_attack(df_region)
    )

if __name__ == "__main__":
    app.run(debug=True)