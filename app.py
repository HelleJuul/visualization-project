import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

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

###         P A G E   0  -  Number of sales                                                         ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

#
# Loading the data
#

# Geojson file with the shape of the zip code areas on Fyn with a unique ID pr shape 
with open('zip_code_areas_fyn_with_id.geojson', "r") as f:
    zip_code_areas = json.load(f)

# Dataset with the number of sales per quarter optimized for the map
with open('total_sales_by_quarter.csv', "r") as f:
    total_sales = pd.read_csv(f)

# Dataset with the number of sales per quarter optimized for the bar chart
with open('total_sales_by_quarter_for_bar.csv', "r") as f:
    total_sales_bar = pd.read_csv(f)


#
# Creating the content
#

# A list with the quarters covered in the dataset
quarters = list(total_sales.quarter_name.unique())
# Slider for choosing the month and year
marks = {i: {'label': label} for i, label in enumerate(quarters)}

total_sales_slider = dcc.Slider(id='month_slider_total_sales',
                                min=0, 
                                max=len(quarters)-1, 
                                value=len(quarters)-1,
                                step=1,
                                marks=marks,
                                included=False)

# Dropdown menu for selecting zip code areas
zips_and_names = total_sales[['zip_code', 'name']].drop_duplicates()
zips_and_names.sort_values('zip_code', inplace=True)
zipped = zip(zips_and_names.zip_code, zips_and_names.name)
dropdown_options_total_sales = [{'label': str(z) + " " + str(name), 'value': z} for z, name in zipped]

total_sales_dropdown = dcc.Dropdown(id="zip_dropdown_total_sales",
                                options=dropdown_options_total_sales,
                                value=[5000, 5900],
                                multi=True)


# The content of the page styled to be two rows
page0 = [
        dbc.Container(
            [   html.H2("Number of Houses Sold"),
                dbc.RadioItems(options = [{'label': 'Number of Sales', 'value': 'abs_num'},
                                          {'label': 'Sales per 1000 Residences', 'value': 'rel_num'}],
                               value = 'abs_num',
                               labelStyle = {'display': 'inline-block'},
                               id = "rel_abs_radio"),
                html.Br(),   
                html.H4(id="total_sales_header", children="2021 - Q4"),      
                dcc.Graph(id='total_sales_map'),
                html.Div("Choose Quarter", className="form-label"),
                total_sales_slider
            ],
            style={'width':'50%', 'display':'inline-block', 'vertical-align':'top'}
        ), 
        dbc.Container(
            [   
                html.H4("Development over Time"),
                html.Div("Choose Zip Code Areas", className="form-label"),
                total_sales_dropdown,
                dcc.Graph(id="total_sales_bar")
            ], 
            style={'width':'50%','display':'inline-block', 'vertical-align':'top'}
        ),
    ]


#
#   Callbacks
#

@app.callback(
    Output("total_sales_map", "figure"),
    Input("rel_abs_radio", "value"),
    Input("month_slider_total_sales", "value"),
    Input("zip_dropdown_total_sales", "value")
    )
def update_choropleth_with_total_sales(rel_or_abs, date, selected_zips):
    '''Create and update the choropleth map of Fyn with number of sold houses'''
    if rel_or_abs == "rel_num":
        color = "rel_sales"
        range_color = [0, 75]
        color_scale = "dense"
    else:
        color = "sales"
        range_color = [0, 150]
        color_scale = "dense"
    selected_date = quarters[date]
    total_sales_selected_month = total_sales[total_sales.quarter_name==selected_date]
    # Change the coloring according to the chosen month
    fig = px.choropleth(total_sales_selected_month,
                geojson=zip_code_areas, 
                color=color, 
                locations='id',
                projection="mercator",
                range_color=range_color,
                color_continuous_scale=color_scale,
                template='simple_white',
                labels={"sales": 'Number of Sales',
                        "rel_sales": "Sales per 1000 Residences"})
    # Zoom in on Fyn
    fig.update_geos(fitbounds="locations", visible=False)
    # Remove margins
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # Move colorbar to the left
    fig.update_layout(coloraxis_colorbar_x=-0.08)
    # Make the hover data look nice
    area_zips_and_names = list(total_sales['zip_code'].apply(str) + " " + total_sales['name'].apply(str))
    fig.update_traces(hovertemplate='<b>%{customdata}</b><br>%{z}', 
                      customdata=area_zips_and_names)
    # Highlight selected zips on the map
    selected_areas_ids = translate_zips_to_ids(selected_zips)
    fig.add_trace(go.Choropleth(geojson=zip_code_areas,
                                locationmode="geojson-id",
                                locations=selected_areas_ids,
                                z = [1]*len(selected_areas_ids),
                                colorscale = [[0, 'rgba(0,0,0,0)'],[1, 'rgba(0,0,0,0)']],
                                colorbar=None,
                                showscale =False,
                                marker = {"line": {"color": "#F39C12", "width": 1}},
                                hoverinfo='skip'))
    return  fig


@app.callback(
    Output("total_sales_header", "children"),
    Input("month_slider_total_sales", "value")
    )
def update_title_to_match_chosen_quarter_total_sales(date):
    '''Change the title to show the chosen month and year.'''
    return  quarters[date]


@app.callback(
    Output("zip_dropdown_total_sales", "value"),
    Input("total_sales_map", "clickData"),
    State("zip_dropdown_total_sales", "value")   
)
def update_dropdown_total_sales(clickData, selected_zips):
    '''Add regions selected on the choropleth map to the selected values in 
    the dropdown menu.'''
    if clickData:
        zip_from_map = int(clickData['points'][0]['customdata'][0:4])
        if zip_from_map not in selected_zips:
            selected_zips.append(zip_from_map)
    return selected_zips


@app.callback(
    Output("total_sales_bar", "figure"),
    Input("rel_abs_radio", "value"),
    Input("zip_dropdown_total_sales", "value"),
    Input("month_slider_total_sales", "value"),
    )
def update_line_chart_with_total_sales(rel_or_abs, selected_zips, date):
    '''Create and update the line chart showing the development in m2 prices
    in the selected zip code areas'''
    if len(selected_zips) == 0:
        return {}
    if rel_or_abs == "rel_num":
        y_value = "rel_sales"
    else:
        y_value = "sales"
    total_sales_filtered = total_sales_bar[total_sales_bar.zip_code.isin(selected_zips)]
    # Draw a line for each of the selected zip code areas
    fig = px.bar(total_sales_filtered, 
                  x='quarter_name', 
                  y=y_value,
                  color=total_sales_filtered.zip_code.apply(str),
                  template='simple_white',
                  color_discrete_sequence=px.colors.qualitative.Vivid,
                  facet_row='zip_code',
                  height=600,
                  labels={'zip_code':   'Zip Code',
                          'color':      'Zip code',
                          'quarter_name':    'Quarter',
                          'sales':  'Number of Sales',
                          'rel_sales': "Sales per 1000<br>Residences"})
    # Smaller text on y-axis
    fig.update_yaxes(title_font=dict(size=10))
    # Add a rectangle to highlight the selected quarter
    selected_date = quarters[date]
    fig.add_vrect(x0=selected_date, x1=selected_date, col=1,
              fillcolor="green", opacity=0.10, line_width=45)
    # Make hover data look nice
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    return fig


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
                       marks=marks,
                       included=False)

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
                
                m2price_slider
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
    selected_month = dates[month]
    # Change the coloring according to the chosen month
    fig = px.choropleth(m2prices_map,
                geojson=zip_code_areas, 
                color=selected_month, 
                locations='id',
                projection="mercator",
                hover_name="name",
                hover_data={'id': False,
                            "zip_code": True,
                            selected_month: ':.2f'},
                
                range_color=[0,35000],
                color_continuous_scale='Viridis',
                template='simple_white',
                labels={selected_month: 'Average price per m2 in DKK'})
    # Zoom in on Fyn
    fig.update_geos(fitbounds="locations", visible=False)
    # Remove margins
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    # Move colorbar to the left
    fig.update_layout(coloraxis_colorbar_x=-0.08)
    # Change ticks on colorbar from the default 10k to 10000
    fig.update_coloraxes(colorbar_tickformat=',2f')
    # Make the hover data look nice
    area_zips_and_names = list(m2prices_map['zip_code'].apply(str) + " " + m2prices_map['name'])
    fig.update_traces(hovertemplate='<b>%{customdata}</b><br>%{z: .2f} kr.', 
                      customdata=area_zips_and_names)
    # Color NaN areas grey (and still make the hover data look nice)
    nan_filter = m2prices_map[selected_month].isna()
    nan_area_ids = m2prices_map['id'][nan_filter]
    nan_area_zips_and_names = list(m2prices_map['zip_code'][nan_filter].apply(str) + 
                                   " " + 
                                   m2prices_map['name'][nan_filter])
    fig.add_trace(go.Choropleth(geojson = zip_code_areas,
                                locationmode = "geojson-id",
                                locations = nan_area_ids,
                                z = [1] * len(nan_area_ids),
                                colorscale = [[0, 'rgba(192,192,192,1)'],[1, 'rgba(192,192,192,1)']],
                                colorbar = None,
                                showscale = False,
                                hovertemplate = '<b>%{customdata}</b>'+
                                                '<br>'+
                                                '<i>%{text}</i><extra></extra>',
                                text = ['No sales'] * len(nan_area_ids),
                                customdata = nan_area_zips_and_names
                                ))
    # Highlight selected zips on the map
    selected_areas_ids = translate_zips_to_ids(selected_zips)
    fig.add_trace(go.Choropleth(geojson=zip_code_areas,
                                locationmode="geojson-id",
                                locations=selected_areas_ids,
                                z = [1]*len(selected_areas_ids),
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
        zip_from_map = clickData['points'][0]['customdata'][0:4]
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
                  line_color="#3498DB")
    # Add the average m2 price for all of Fyn for reference
    fig.add_trace(go.Scatter(mode='lines',
                             x = m2prices_line_chart['index'],
                             y = m2prices_line_chart['fyn'],
                             name="All of Fyn",
                             marker_color='gray',
                             opacity=0.2))
    # Make the hover text look nicer
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
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
        return page0
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
    app.run_server(debug=True)
