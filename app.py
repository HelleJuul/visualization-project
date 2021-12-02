import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import total_sales

import json
import pandas as pd


with open('zip_code_areas_fyn_with_id.geojson', "r") as f:
    zip_code_areas = json.load(f)

with open('average_m2prices_per_zip_code_with_unique_id.csv', "r") as f:
    data = pd.read_csv(f)
    
with open('m2prices.csv', 'r') as f:
    m2prices = pd.read_csv(f)

dates = list(data.columns)[4:]

month_names = ['January', 
               'February', 
               'March', 
               'April', 
               'May', 
               'June', 
               'July', 
               'August', 
               'September', 
               'October', 
               'November', 
               'December']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src="assets/house_blue.png", height="40px")),
                    dbc.Col(dbc.NavbarBrand("The Fyn Housing Market", className="ms-2", href="/")),
                ],
                align="center",
                className="g-0",
            ),
            dbc.NavItem(dbc.NavLink("Average price per m2", href="/page-1", active='exact')),
            dbc.NavItem(dbc.NavLink("Total sales", href="/page-2", active='exact')),
            dbc.NavItem(dbc.NavLink("Page 3", href="/page-3", active='exact')),
        ]
    ),
    color="primary",
    dark=True,
    fixed="top",
)

m2price_header = html.H4(id="m2price_header", 
                         children="Average Price per m2 in November 2021")

m2price_note = html.Div(children=["Note",
                                  html.Br(),  
                                  "If no sales were made in a given zip code area " 
                                  "during the chosen month the average price per m2 is set to 0 kr."], 
                        className="alert alert-info")




m2price_map = dcc.Graph(id='m2price_map')

marks = {i: {'label': ""} for i in range(0, len(dates))}
for i in range(0, len(dates), 4):
    marks[i] = {'label': dates[i]}

m2price_slider = dcc.Slider(id='month_slider',
                       min=0, 
                       max=len(dates)-1, 
                       value=len(dates)-1,
                       step=1,
                       marks=marks)




zips_and_names = data[['zip_code', 'name']].copy()
zips_and_names.sort_values('zip_code', inplace=True)
zips_and_names.drop_duplicates(inplace=True)
dropdown_options = [{'label': str(z) + " " + name, 'value': z} for z, name in zip(zips_and_names.zip_code, zips_and_names.name)]

m2price_dropdown = dcc.Dropdown(id="zip_dropdown",
                                options=dropdown_options,
                                value=[5000, 5300],
                                multi=True,
                                className=".DropdownMenu"
                               )

m2price_graph = dcc.Graph(id="m2price_plot")


app.layout = dbc.Container([
        dcc.Location(id="url"),
        navbar,
        dbc.Container(id='page-content', class_name='main', style={"padding-top": "90px"}),
        html.Hr()
    ],
    fluid=True)




@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname")
    )
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return [dbc.Container(children=[m2price_header, 
                                        m2price_note, 
                                        m2price_map,
                                        html.Div("Choose Month", className="form-label"),
                                        m2price_slider],
                              style={'width':'50%', 'display':'inline-block','vertical-align':'top'}
                             ), 
                dbc.Container(children=[html.H4("Development over Time"),
                                        html.Div("Choose Zip Code Areas", className="form-label"),
                                        m2price_dropdown,
                                        m2price_graph], 
                              style={'width':'50%','display':'inline-block','vertical-align':'top'}
                              )
                ]
    elif pathname == "/page-2":
        return dcc.Graph(figure=total_sales.fig)
    elif pathname == "/page-3":
        return html.P("You found page 3!")
    # If the user tries to reach a different page, return a 404 message
    else:
        return html.H1("404: Not found", className="text-danger")


def translate_zips_to_ids(zips):
    ids = []
    for zip_code in zips:
        zip_text = str(zip_code)
        for item in zip_code_areas['features']:
            if item['properties']['POSTNR_TXT'] == zip_text:
                ids.append(item['id'])
    return ids

@app.callback(
    Output("m2price_map", "figure"),
    Input("month_slider", "value"),
    Input("zip_dropdown", "value")
    )
def change_month_of_m2price_choropleth(month, selected_zips):
    fig = px.choropleth(data,
                geojson=zip_code_areas, 
                color=dates[month], 
                locations='id',
                projection="mercator",
                hover_name="name",
                hover_data=["zip_code"],
                range_color=[0,35000],
                color_continuous_scale='Viridis',
                template='simple_white',
                labels={dates[month]: 'Average price per m2 in DKK'},)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(coloraxis_colorbar_x=-0.08)
    
    # Highlight selected zips
    id_list = translate_zips_to_ids(selected_zips)
    fig.add_trace(go.Choropleth(geojson=zip_code_areas,
                                locationmode="geojson-id",
                                locations=id_list,
                                z = [1]*len(id_list),
                                colorscale = [[0, 'rgba(0,0,0,0)'],[1, 'rgba(0,0,0,0)']],
                                colorbar=None,
                                showscale =False,
                                marker = {"line": {"color": "#F39C12", "width": 1}},
                                hoverinfo='skip'
                                ))
    return  fig


@app.callback(
    Output("m2price_header", "children"),
    Input("month_slider", "value")
    )
def update_title_to_match_chosen_month(month):
    time = dates[month]
    month_index = int(time[-2:]) - 1
    month = month_names[month_index]
    year = time[:4]
    title = "Average Price per m2 in " + month + " " + year
    return  title


@app.callback(
    Output("zip_dropdown", "value"),
    Input("m2price_map", "clickData"),
    State("zip_dropdown", "value")   
)
def add_regions_selected_on_map_to_dropdown(clickData, selected_zips):
    if clickData:
        zip_from_map = clickData['points'][0]['customdata'][0]
        if zip_from_map not in selected_zips:
            selected_zips.append(zip_from_map)
    return selected_zips


@app.callback(
    Output("m2price_plot", "figure"),
    Input("month_slider", "value"),
    Input("zip_dropdown", "value"),
    )
def update_potition_of_vertical_line(month, selected_zips):
    fig = px.line(m2prices, 
                  x='index', 
                  y=[str(i) for i in selected_zips], 
                  markers=True,
                  template='simple_white',
                  color_discrete_sequence=px.colors.qualitative.Vivid,
                  height=600,
                  labels={'index': 'Year and Month', 
                          'value': 'Average Price pr m2 in DKK',
                          'variable': 'Zip Code'})
    fig.update_yaxes(rangemode="tozero")
    fig.add_vline(x=dates[month], 
                  line_width=3, 
                  line_dash="dash", 
                  line_color="#3398db")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
