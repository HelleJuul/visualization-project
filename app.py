import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import json
import pandas as pd


### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         I N I T I A L I Z I N G    T H E   A P P                                                ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True) 

# Setting the main layout with a fixed navbar at the top
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
            dbc.NavItem(dbc.NavLink("Average Price per m2", href="/page-1", active='exact')),
            dbc.NavItem(dbc.NavLink("House Prices", href="/page-2", active='exact')),
            dbc.NavItem(dbc.NavLink("Sales per Month", href="/page-3", active='exact')),
        ]
    ),
    color="primary",
    dark=True,
    fixed="top",
)

app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        navbar,
        dbc.Container(id='page-content', class_name='main', style={"padding-top": "90px"}),
        html.Hr()
    ],
    fluid=True,
)


### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         P A G E   1  -  price per m2                                                            ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

#
# Loading the data
#

# Geojson file with the shape of the zip code areas on Fyn with a unique ID pr shape 
with open('zip_code_areas_fyn_with_id.geojson', "r") as f:
    zip_code_areas = json.load(f)

# Dataset with the average m2 price for houses sold on Fyn optimized for the choropleth map
with open('m2prices_for_choropleth.csv', "r") as f:
    m2prices_map = pd.read_csv(f)

# Dataset with the average m2 price for houses sold on Fyn optimized for the line chart
with open('m2prices_for_line_chart.csv', 'r') as f:
    m2prices_line_chart = pd.read_csv(f)
    

#
#   Helper functions
#
def translate_zips_to_ids(zips):
    '''Return a list with the IDs corresponding to the zip codes in zips'''
    ids = []
    for zip_code in zips:
        zip_text = str(zip_code)
        for item in zip_code_areas['features']:
            if item['properties']['POSTNR_TXT'] == zip_text:
                ids.append(item['id'])
    return ids


#
# Creating the content
#

# A list with the months covered in the dataset (i.e. 2021-11)
dates = list(m2prices_map.columns)[4:]

# Slider for choosing the month and year
marks = {i: {'label': ""} for i in range(0, len(dates))}
for i in range(0, len(dates), 2):
    marks[i] = {'label': dates[i]}

m2price_slider = dcc.Slider(id='month_slider',
                       min=0, 
                       max=len(dates)-1, 
                       value=len(dates)-1,
                       step=1,
                       marks=marks)

# Dropdown menu for selecting zip code areas
zips_and_names = m2prices_map[['zip_code', 'name']].copy()
zips_and_names.sort_values('zip_code', inplace=True)
zips_and_names.drop_duplicates(inplace=True)
zipped = zip(zips_and_names.zip_code, zips_and_names.name)
dropdown_options = [{'label': str(z) + " " + name, 'value': z} for z, name in zipped]

m2price_dropdown = dcc.Dropdown(id="zip_dropdown",
                                options=dropdown_options,
                                value=[5000, 5900],
                                multi=True)

# The content of page 1 styled to be two rows
page1 = [
        dbc.Container(
            [                
                html.H4(id="m2price_header", children="November 2021"), 
            ],
            style={'width':'50%', 'display':'inline-block', 'vertical-align':'top'}
        ), 
        dbc.Container(
            [
                html.H4("Development over Time"),
            ], 
            style={'width':'50%','display':'inline-block','vertical-align':'top'}
        ),
        dbc.Container(
            [                
                dcc.Graph(id='m2price_map'),
            ],
            style={'width':'50%', 'display':'inline-block', 'vertical-align':'top'}
        ), 
        dbc.Container(
            [   
                html.Div("Choose Zip Code Areas", className="form-label"),
                m2price_dropdown,
                dcc.Graph(id="m2price_plot")
            ], 
            style={'width':'50%','display':'inline-block', 'vertical-align':'top'}
        ),
        dbc.Container(
            [  
                html.Div("Choose Month", className="form-label"),
                
                m2price_slider,
                
                html.Div("If no sales were made in a given zip code area during a "
                       "given month the average price per m2 is set to 0 DKK.", className="blockquote-footer")
            ],
        ),
    ]

#
#   Callbacks
#

@app.callback(
    Output("m2price_map", "figure"),
    Input("month_slider", "value"),
    Input("zip_dropdown", "value")
    )
def update_choropleth_with_m2_prices(month, selected_zips):
    '''Create and update the choropleth map of Fyn with the average m2 price'''
    # Change the coloring according to the chosen month
    fig = px.choropleth(m2prices_map,
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
    # Zoom in on Fyn
    fig.update_geos(fitbounds="locations", visible=False)
    # Remove margins
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # Move colorbar to the left
    fig.update_layout(coloraxis_colorbar_x=-0.08)
    # Change ticks on colorbar from the default 10k to 10000
    fig.update_coloraxes(colorbar_tickformat=',2f')
    # Highlight selected zips on the map
    id_list = translate_zips_to_ids(selected_zips)
    fig.add_trace(go.Choropleth(geojson=zip_code_areas,
                                locationmode="geojson-id",
                                locations=id_list,
                                z = [1]*len(id_list),
                                colorscale = [[0, 'rgba(0,0,0,0)'],[1, 'rgba(0,0,0,0)']],
                                colorbar=None,
                                showscale =False,
                                marker = {"line": {"color": "#F39C12", "width": 1}},
                                hoverinfo='skip'))
    return  fig


@app.callback(
    Output("m2price_header", "children"),
    Input("month_slider", "value")
    )
def update_title_to_match_chosen_month(month):
    '''Change the title to show the chosen month and year.'''
    time = dates[month]
    month_index = int(time[-2:]) - 1
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 
                   'August', 'September', 'October', 'November', 'December']
    month = month_names[month_index]
    year = time[:4]
    title = month + " " + year
    return  title


@app.callback(
    Output("zip_dropdown", "value"),
    Input("m2price_map", "clickData"),
    State("zip_dropdown", "value")   
)
def update_dropdown(clickData, selected_zips):
    '''Add regions selected on the choropleth map to the selected values in 
    the dropdown menu.'''
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
def update_line_chart_with_m2_prices(month, selected_zips):
    '''Create and update the line chart showing the development in m2 prices
    in the selected zip code areas'''
    # Draw a line for each of the selected zip code areas
    fig = px.line(m2prices_line_chart, 
                  x='index', 
                  y=[str(i) for i in selected_zips],
                  range_y=[0, 35000], 
                  markers=True,
                  template='simple_white',
                  color_discrete_sequence=px.colors.qualitative.Vivid,
                  height=450,
                  labels={'index': 'Year and Month', 
                          'value': 'Average Price pr m2 in DKK',
                          'variable': 'Zip Code'})
    # Force the y-axis to always start at zero
    fig.update_yaxes(rangemode="tozero")
    # Change the ticks from the standard 10k to 10000
    fig.update_layout(yaxis={'tickformat': ',2f'})
    # Add a vertical line in the plot showing the chosen month and year
    fig.add_vline(x=dates[month], 
                  line_width=3, 
                  line_dash="dash", 
                  line_color="#3398db")
    return fig


### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         P A G E   2  -  Sales prices                                                            ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###


page2 = html.P("This is page 2!")



### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         P A G E   3   -   Sales per month                                                       ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###


page3 = html.P("You found page 3!")



### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         R E N D E R   P A G E   C O N T E N T                                                   ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname")
    )
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return page1
    elif pathname == "/page-2":
        return page2
    elif pathname == "/page-3":
        return page3
    # If the user tries to reach a different page, return a 404 message
    else:
        return html.H1("404: Not found", className="text-danger")


if __name__ == "__main__":
    app.run_server(debug=True, port=8080)
