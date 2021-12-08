import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import json
import pandas as pd
import numpy as np


### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

###         I N I T I A L I Z I N G    T H E   A P P                                                ###

### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ### -o-o- ###

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True) 
server = app.server
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
            dbc.NavItem(dbc.NavLink("Area Information", href="/page-3", active='exact')),
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
    fig.update_traces(hovertemplate='<b>%{customdata}</b><br>%{z:.2f} kr.', 
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

p3view = pd.read_csv("p3view.csv")
sales_volume = pd.read_csv("sales_volume_by_zip.csv")
violin_fig = px.histogram(p3view[p3view["Zip Code"]==5000], x="Sales Price")
violin_fig.update_layout(title={"text":"Sales Price Distribution",  "x":0.5})
bar_chart = px.bar(sales_volume, x="month", y="5000", labels={"month":"Month", "5000":"Number of Sales"})
bar_chart.update_layout(title={"text":"Number of Sales per Month",  "x":0.5})

page3 = [
        html.H2(style={"text-align":"center"},children=["Area Information"]),
        html.Div(style = {"margin":"0 40% 0 40%"}, 
            children=[
                dcc.Dropdown(id="zip_dropdown_page3",
                                 options=dropdown_options,
                                 value=5000,
                                 placeholder="choose zip code",
                                 multi=False),
                html.Br(),
                html.Div(style={"margin":"0 25%", "display":"block"}, children=[
                dbc.Button("Filter Results", id="open-button-offcanvas-page-3",
                           n_clicks=0,),
                ]),

        ]),
        html.Br(),
        html.Div(style={},
            children = [
            # html.H4("Sales Information", style={"padding":"10px auto"}),
            html.Div(style = {"display":"inline-block", "width":"50%", "text-align":"center"},
                    children=[
                        dcc.Loading(type="circle",
                            children=[
                            dcc.Graph(id="total-sales-zipcode", style={"padding":"0 auto"}, figure=bar_chart),
                        ]),
            ]),
            html.Div(style = {"display":"inline-block", "width":"50%"},
                    children=[
                        dcc.Loading(type="circle",
                            children=[
                                dcc.Graph(id="violin-sales-zipcode", style={"padding":"0 auto"}, figure=violin_fig),
                        ]),
            ]),
        ]),
        
        ### info toast
        html.Div(style={"display":"inline-bock", "width":"20%","top":"10%","left":"10%", "position":"absolute"},
                 children=[dbc.Toast(id="filters-used-infobox", style={"opacity":"0"},dismissable=True, header="Applied filters")]),
        
        dbc.Offcanvas(id = "offcanvas-page-3",
                      title="Filter Options",
                      is_open = False,
                      placement = "end",
                      autofocus = True,
                      scrollable = True,
                      style = {"width":"30%"},
                      children=[                              
                              dbc.Switch(id="switch-price-filter",label="filter on price", style={"margin":"0 10%", "display":"inline-block", "width":"50%"}),
                              html.Div(id="price-filter-container", style={"margin":"10px 5%", "opacity":"50%"},
                                    children = [
                                    html.P("Price in DKK", style={"text-align":"center"}),
                                    html.Div(id="price-slider-info",style={"margin":"10px 5%"} ),
                                    dcc.RangeSlider(id="price-slider-p3",min=0, max=2000,step=1000, tooltip={"placement": "bottom"}),
                                    ]
                              ),
                              html.Br(),
                              dbc.Switch(id="switch-area-filter",label="filter by living area", style={"margin":"0 10%", "display":"inline-block", "width":"50%"}),
                              html.Div(id="area-filter-container", style={"margin":"10px 5%", "opacity":"50%"},
                                    children = [
                                        html.P("Living area (m2)", style={"text-align":"center"}),
                                        html.Div(id="area-slider-info", style={"margin":"10px 5%"}),
                                        dcc.RangeSlider(id="area-slider-p3",min=0, max=100, step=1, tooltip={"placement": "bottom"}),
                                        html.P("Ground area (m2)", style={"text-align":"center"}),
                                        html.Div(id="groundarea-slider-info", style={"margin":"10px 5%"}),
                                        dcc.RangeSlider(id="groundarea-slider-p3",min=0, max=100, step=1, tooltip={"placement": "bottom"}),
                                        ]
                              ),
                              html.Br(),
                              dbc.Switch(id="switch-rooms-filter",label="filter by rooms", style={"margin":"0 10%", "display":"inline-block", "width":"50%"}),
                              html.Div(id="rooms-filter-container", style={"margin":"10px 5%", "opacity":"50%"},
                                    children = [
                                        html.Div( style={"text-align":"left", "display":"inline-block", "width":"50%" },
                                                 children=[html.P("Number of bathrooms", style={"margin":"0 10%"}),]
                                        ),
                                        html.Div(style={"display":"inline-block", "width":"50%"},
                                            children=[
                                                dcc.Input(id="input-min-bathrooms",type="number", style={"width":"50px"}),
                                                html.P(" to ", style={"display":"inline-block", "margin":"0 5%"}),
                                                dcc.Input(id="input-max-bathrooms",type="number",style={"width":"50px"}),
                                        ]),
                                        html.Br(),
                                        html.Br(),
                                        html.Div( style={"text-align":"left", "display":"inline-block", "width":"50%" },
                                                 children=[html.P("Number of bedrooms", style={"margin":"0 10%"}),]
                                        ),
                                        html.Div(style={"display":"inline-block", "width":"50%"},
                                            children=[
                                                dcc.Input(id="input-min-bedrooms",type="number", style={"width":"50px"}),
                                                html.P(" to ", style={"display":"inline-block", "margin":"0 5%"}),
                                                dcc.Input(id="input-max-bedrooms",type="number",style={"width":"50px"}),
                                        ]),
                                        dcc.Checklist(id="room-check-unknown", options=[{"label":"  include unknown number of rooms", "value":"include"}],
                                                       value = ["include"], style={"margin":"20px 5%"}),
                                        ]
                              ),
                              html.Br(),
                              html.Br(),
                              html.Div(style={"margin":"0 40%"}, children = [
                                  dbc.Button("Apply",id="button-apply-filters", class_name="btn-success", style={"width":"80%"}),
                                  ]
                                  ),
                          ],
        ),

        

         ]

@app.callback(
    Output("offcanvas-page-3", "is_open"),
    Input("open-button-offcanvas-page-3", "n_clicks"),
    [State("offcanvas-page-3", "is_open")]
    )
def open_and_close_off_canvas_p3(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@app.callback(
        Output("price-filter-container","style"),
        Output("price-slider-p3","disabled"),
        Input("switch-price-filter","value"),
        State("switch-price-filter","value")
    )
def activate_filtering_on_price(switch_on, state):
    if state:
        return  {"margin":"10px 5%", "opacity":"100%"}, False
    else:
        return {"margin":"10px 5%", "opacity":"50%"}, True
        
@app.callback(
        Output("area-filter-container","style"),
        Output("area-slider-p3","disabled"),
        Output("groundarea-slider-p3","disabled"),
        Input("switch-area-filter","value"),
        State("switch-area-filter","value")
    )
def activate_filtering_on_area(switch_on, state):
    if state:
        return  {"margin":"10px 5%", "opacity":"100%"}, False, False
    else:
        return {"margin":"10px 5%", "opacity":"50%"}, True, True

@app.callback(
        Output("rooms-filter-container","style"),
        Output("input-min-bathrooms","disabled"),
        Output("input-max-bathrooms","disabled"),
        Output("input-min-bedrooms","disabled"),
        Output("input-max-bedrooms","disabled"),
        Output("room-check-unknown","disabled"),
        Input("switch-rooms-filter","value"),
        State("switch-rooms-filter","value")
    )
def activate_filtering_on_rooms(switch_on, state):
    if state:
        return  {"margin":"10px 5%", "opacity":"100%"}, False, False, False, False, False
    else:
        return {"margin":"10px 5%", "opacity":"50%"}, True, True, True, True, True
    
@app.callback(
    Output("violin-sales-zipcode", "figure"),
    Output("total-sales-zipcode", "figure"),
    Input("zip_dropdown_page3","value"),
    Input("button-apply-filters","n_clicks"),
    State("zip_dropdown_page3", "value"),
    State("switch-area-filter","value"),
    State("area-slider-p3", "value"),
    State("groundarea-slider-p3", "value"),
    State("switch-price-filter","value"),
    State("price-slider-p3", "value"),
    State("switch-rooms-filter","value"),
    State("input-min-bathrooms", "value"),
    State("input-max-bathrooms", "value"),
    State("input-min-bedrooms", "value"),
    State("input-max-bedrooms", "value"),
    State("room-check-unknown","value"),
    State("violin-sales-zipcode", "figure"),
    State("total-sales-zipcode", "figure"),
    )
def update_p3_sales_plots(selected_zip, nclicks, zip_current, filter_area, area_lim, garea_lim, filter_price, price_lim, filter_rooms, min_bath, max_bath, min_bed, max_bed, incl_unknown, curr_viol, curr_bar):
    """
        Update sales information plots w. filtering
        Note: Essentially unreadable code -- sry
    """
    
    violin_fig, bar_chart = curr_viol, curr_bar
    
    ctx = callback_context
    id_called = None
    if ctx.triggered:
        id_called = ctx.triggered[0]["prop_id"].split(".")[0]    
    
    if id_called and "zip_dropdown" in id_called and selected_zip:
        violin_fig = px.histogram(p3view[p3view["Zip Code"]==selected_zip], x="Sales Price")
        violin_fig.update_layout(title={"text":"Sales Price Distribution",  "x":0.5})
        bar_chart = px.bar(sales_volume, x="month", y=str(selected_zip), labels={"month":"Month",str(selected_zip):"Number of Sales"} )
        bar_chart.update_layout(title={"text":"Number of Sales per Month",  "x":0.5})
    elif id_called and "button-apply-filters" in id_called:

        relevant_sales = p3view[p3view["Zip Code"] == zip_current]
        if filter_area:
            min_area, max_area = min(area_lim), max(area_lim)
            min_garea, max_garea = min(garea_lim), max(garea_lim)
            relevant_sales = relevant_sales[(relevant_sales["Living Area"] >= min_area) & (relevant_sales["Living Area"] <= max_area)]
            relevant_sales = relevant_sales[(relevant_sales["Ground Area"] >= min_garea) & (relevant_sales["Ground Area"] <= max_garea)]
        
        if filter_price:
            relevant_sales = relevant_sales[(relevant_sales["Sales Price"] >= price_lim[0]) & (relevant_sales["Sales Price"] <= price_lim[1])]
        
        if incl_unknown and filter_rooms:
            unknown_rooms = relevant_sales[(relevant_sales["Number of Bathrooms"] == "unknown") | (relevant_sales["Number of Bedrooms"] == "unknown")]
        
        if filter_rooms:
            min_bath, max_bath, min_bed, max_bed = str(min_bath), str(max_bath), str(min_bed), str(max_bed)
            relevant_sales = relevant_sales[(relevant_sales["Number of Bathrooms"] >= min_bath) & (relevant_sales["Number of Bathrooms"] <= max_bath)]
            relevant_sales = relevant_sales[(relevant_sales["Number of Bedrooms"] >= min_bed) & (relevant_sales["Number of Bedrooms"] <= max_bed)]
            if incl_unknown:
                relevant_sales = pd.concat([relevant_sales, unknown_rooms])
        
        violin_fig = px.histogram(relevant_sales, x="Sales Price")
        violin_fig.update_layout(title={"text":"Sales Price Distribution",  "x":0.5})
        filtered_count = []
        for month in sales_volume["month"]:
            map_func = lambda x: x[1]["Zip Code"] == zip_current and (month in x[1]["Registration Date"])
            filtered_count.append(sum(map(map_func, relevant_sales.iterrows())))
        filtered_volume = pd.DataFrame(sales_volume["month"].copy(), columns=["month"])
        filtered_volume["Number of Sales"] = np.array(filtered_count)
        bar_chart = px.bar(filtered_volume, x="month", y="Number of Sales", labels={"month":"Month",str(selected_zip):"Number of Sales"} )
        bar_chart.update_layout(title={"text":"Number of Sales per Month",  "x":0.5})
    return violin_fig, bar_chart

@app.callback(
        Output("price-slider-p3", "max"),
        Output("price-slider-p3", "min"),
        Output("price-slider-p3", "value"),
        Input("zip_dropdown_page3", "value"),
        State("price-slider-p3", "max"),
        State("price-slider-p3", "min"),
        State("price-slider-p3", "value"),
    )
def update_filter_price_options(selected_zip, curr_max, curr_min, curr_val):
    if selected_zip:
        relevant_sales = p3view[p3view["Zip Code"] == selected_zip]
        max_price = relevant_sales["Sales Price"].max()
        min_price = relevant_sales["Sales Price"].min()
        return max_price, min_price, [min_price, max_price]
    return  curr_max, curr_min, curr_val
    
@app.callback(
        Output("price-slider-info","children"),
        Input("price-slider-p3", "value")
    )
def update_filter_price_info(slider_values):
    info = [ html.B("Min. price: {:3,d}".format(slider_values[0])), html.Br(),html.B("Max. price: {:3,d}".format(slider_values[1])) ]
    return info


@app.callback(
        Output("area-slider-p3", "max"),
        Output("area-slider-p3", "min"),
        Output("area-slider-p3", "value"),
        Input("zip_dropdown_page3", "value"),
        State("area-slider-p3", "max"),
        State("area-slider-p3", "min"),
        State("area-slider-p3", "value"),
    )
def update_filter_area_options(selected_zip, curr_max, curr_min, curr_val):
    if selected_zip:
        relevant_sales = p3view[p3view["Zip Code"] == selected_zip]
        max_area = relevant_sales["Living Area"].max()
        min_area = relevant_sales["Living Area"].min()
        return max_area, min_area,  [max_area, min_area]
    return curr_max, curr_min, curr_val

@app.callback(
        Output("groundarea-slider-p3", "max"),
        Output("groundarea-slider-p3", "min"),
        Output("groundarea-slider-p3", "value"),
        Input("zip_dropdown_page3", "value"),
        State("groundarea-slider-p3", "max"),
        State("groundarea-slider-p3", "min"),
        State("groundarea-slider-p3", "value"),
    )
def update_filter_groundarea_options(selected_zip, curr_max, curr_min, curr_val):
    if selected_zip:
        relevant_sales = p3view[p3view["Zip Code"] == selected_zip]
        max_area = relevant_sales["Ground Area"].max()
        min_area = relevant_sales["Ground Area"].min()
        return max_area, min_area,  [max_area, min_area]
    return curr_max, curr_min, curr_val

@app.callback(
        Output("area-slider-info","children"),
        Output("groundarea-slider-info","children"),
        Input("area-slider-p3", "value"),
        Input("groundarea-slider-p3", "value")
    )
def update_filter_area_info(area_values, ground_values):
    max_area = max(area_values)
    min_area = min(area_values)
    max_garea = max(ground_values)
    min_garea = min(ground_values)
    style= {"width":"50%", "display":"inline-block","padding":"0 5%", "text-align":"center"}
    info_area = [html.Div(children=[html.B(f"Min. living area:     {min_area}")],style=style), html.Div(children=[html.B(f"Max. living area:     {max_area}")],style=style) ]
    info_garea = [html.Div(children=[html.B(f"Min. ground area:     {min_garea}")],style=style), html.Div(children=[html.B(f"Max. ground area:     {max_garea}")],style=style) ]
    return info_area, info_garea


@app.callback(
        Output("input-min-bathrooms", "min"),
        Output("input-max-bathrooms", "max"),
        Output("input-min-bathrooms", "value"),
        Output("input-max-bathrooms", "value"),
        Input("zip_dropdown_page3", "value"),
        State("input-min-bathrooms", "min"),
        State("input-max-bathrooms", "max"),
    )
def update_filter_bathroom_options_zip(selected_zip, curr_min, curr_max):
    if selected_zip:
        relevant_sales = p3view[p3view["Zip Code"] == selected_zip]
        # ugly!
        val = relevant_sales["Number of Bathrooms"].unique()
        val = val[ val != "unknown"  ]
        max_num = val.max()
        min_num = val.min()
        return min_num, max_num, min_num, max_num
    return curr_min, curr_max, curr_min, curr_max

@app.callback(
        Output("input-min-bathrooms", "max"),
        Input("input-max-bathrooms", "value"),
        )
def max_input_min_bathrooms(max_min):
    return max_min

@app.callback(
        Output("input-max-bathrooms", "min"),
        Input("input-min-bathrooms", "value"),
        )
def min_input_max_bathrooms(min_max):
    return min_max

@app.callback(
        Output("input-min-bedrooms", "min"),
        Output("input-max-bedrooms", "max"),
        Output("input-min-bedrooms", "value"),
        Output("input-max-bedrooms", "value"),
        Input("zip_dropdown_page3", "value"),
        State("input-min-bedrooms", "min"),
        State("input-max-bedrooms", "max"),
    )
def update_filter_bedrooms_options_zip(selected_zip, curr_min, curr_max):
    if selected_zip:
        relevant_sales = p3view[p3view["Zip Code"] == selected_zip]
        val = relevant_sales["Number of Bedrooms"].unique()
        val = val[ val != "unknown"]
        max_num = val.max()
        min_num = val.min()
        return min_num, max_num, min_num, max_num
    return curr_min, curr_max, curr_min, curr_max

@app.callback(
        Output("input-min-bedrooms", "max"),
        Input("input-max-bedrooms", "value"),
        )
def max_input_min_bedrooms(max_min):
    return max_min

@app.callback(
        Output("input-max-bedrooms", "min"),
        Input("input-min-bedrooms", "value"),
        )
def min_input_max_bedrooms(min_max):
    return min_max

@app.callback(
    Output("filters-used-infobox","style"),
    Output("filters-used-infobox", "children"),
    Input("button-apply-filters","n_clicks"),
    State("switch-area-filter","value"),
    State("area-slider-p3", "value"),
    State("groundarea-slider-p3", "value"),
    State("switch-price-filter","value"),
    State("price-slider-p3", "value"),
    State("switch-rooms-filter","value"),
    State("input-min-bathrooms", "value"),
    State("input-max-bathrooms", "value"),
    State("input-min-bedrooms", "value"),
    State("input-max-bedrooms", "value"),
    State("room-check-unknown","value"),
    )
def update_filters_infobox(n_clicks, filter_area, area_lim, garea_lim, filter_price, price_lim, filter_rooms, min_bath, max_bath, min_bed, max_bed, incl_unknown):
    if n_clicks and (filter_area or filter_price or filter_rooms):
        children = []
        if filter_price:
            min_price = min(price_lim)
            max_price = max(price_lim)
            children.append(html.Div(children=[html.B("Price: "), html.Span(" {:3,d} to {:3,d} DKK".format(min_price, max_price)) ]))

        if filter_area:
            min_area, max_area = min(area_lim), max(area_lim)
            min_garea, max_garea = min(garea_lim), max(garea_lim)
            children.append(html.Div(children=[ html.B("Living Area: "), html.Span(f" {min_area} m2 to {max_area} m2") ]))
            children.append(html.Div(children=[ html.B("Ground Area: "), html.Span(f" {min_garea} m2 to {max_garea} m2") ]))
        
        if filter_rooms:
            children.append(html.Div(children=[html.B("Num. Bathrooms: "), html.Span(f" {min_bath} to {max_bath}")]))
            children.append(html.Div(children=[html.B("Num. Bedrooms: "), html.Span(f" {min_bed} to {max_bed}")]))     
            if incl_unknown:
                children.append(html.I("* Includes results w. unknown number of rooms"))
            else:
                children.append(html.I("* Does not include results w. unknown number of rooms"))
        return {"opacity":"1"}, children
    return {"opacity":"0"}, []



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
