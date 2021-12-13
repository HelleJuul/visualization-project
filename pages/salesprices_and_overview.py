from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc

import pandas as pd
import json

import plotly.express as px
import plotly.graph_objects as go

from dateutil.parser import parse

from app import app

#
#   Load data
#

sales = pd.read_csv("data/sales.csv")
# Change to datetime format
sales["datetimes"] = sales.salesDate.apply(parse)


#
#   Filters
#

months = ["2019-07", "2019-08", "2019-09", "2019-10", "2019-11", "2019-12", 
          "2020-01", "2020-02", "2020-03", "2020-04", "2020-05", "2020-06",
          "2020-07", "2020-08", "2020-09", "2020-10", "2020-11", "2020-12",
          "2021-01", "2021-02", "2021-03", "2021-04", "2021-05", "2021-06",
          "2021-07", "2021-08", "2021-09", "2021-10", "2021-11"]

# marks for time slider in filter
marks = {i: {'label': ""} for i in range(0, len(months))}
for i in range(0, len(months), 6):
    marks[i] = {'label': months[i]}

filters = [
    dbc.Row(
    [
        dbc.Col(
        [
            dbc.Label("Type", style={"margin-bottom": 0}),
            dbc.Checklist(
                id="type-choice",
                options=[
                    {"label": "House", "value": "House"},
                    {"label": "Apartment", "value": "Apartment"},
                    {"label": "Cottage", "value": "Cottage"},
                ],
                value = ["House", "Apartment", "Cottage"],
                inline=True),
        ], style={'margin-bottom': '10px'}
        ),
        dbc.Col(),
        dbc.Col(),
    ]
    ),
    dbc.Row([
        dbc.Col(
        [
            dbc.Label("Sales Price", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("0 kr.",
                          id="price-slider-min",
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("10,000,000 kr. +", 
                         id="price-slider-max",
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="price-slider", 
            min=0, 
            max=10_000_000, 
            value=[0, 10_000_000],
            step= 500_000,
            allowCross=False,
            tooltip={"placement": "bottom"}),
        ], style={'margin-bottom': '10px'}
        ), 
        dbc.Col(
        [ 
            dbc.Label("House Size", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("0 m2",
                          id="house-size-slider-min",
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("250 m2 +",
                         id="house-size-slider-max", 
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="house-size-slider", 
            min=0, 
            max=250, 
            value=[0, 250],
            step= 10,
            allowCross=False,
            tooltip={"placement": "bottom"}),
        ], style={'margin-bottom': '10px'}
        ), 
        dbc.Col(
        [
            dbc.Label("Build Year", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("1900 or before",
                          id="build-year-slider-min", 
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("2021",
                         id="build-year-slider-max",
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="build-year-slider", 
            min=1900, 
            max=2021, 
            value=[1900, 2021],
            step= 10,
            allowCross=False,
            tooltip={"placement": "bottom"}) 
        ], style={'margin-bottom': '10px'}
        )
    ]
    ),
    dbc.Row([
        dbc.Col(
        [
            dbc.Label("Time of Sale", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("2019 - 07",
                          id="time-slider-min",
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("2021 - 11", 
                         id="time-slider-max",
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="time-slider", 
            min=0, 
            max=len(months) - 1, 
            value=[0, len(months) - 1],
            step= 1,
            allowCross=False,
            marks = marks),
        ]
        ), 
        dbc.Col(
        [ 
            dbc.Label("Lot Size", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("0 m2",
                          id="lot-size-slider-min",
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("10,000 m2 +",
                         id="lot-size-slider-max", 
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="lot-size-slider", 
            min=0, 
            max=10_000, 
            value=[0, 10_000],
            step= 500,
            allowCross=False,
            tooltip={"placement": "bottom"},)
        ]
        ), 
        dbc.Col(
        [
            dbc.Label("Number of Rooms", style={"margin-bottom": 0}),
            html.Div(
                [html.Div("0",
                          id="room-slider-min",
                          style={"display": "inline-block", "width": "50%", "text-align": "left", "opacity": "50%"}),
                html.Div("9 +",
                         id="room-slider-max",
                         style={"display": "inline-block", "width": "50%", "text-align": "right", "opacity": "50%"})]
                ),
            dcc.RangeSlider(id="room-slider", 
            min=0, 
            max=9, 
            value=[0, 9],
            step= 1,
            allowCross=False,
            tooltip={"placement": "bottom"}), 
        ]
        )
    ]
    ),
]

#
#   Info table for selected house
#

row0 = html.Tr([    html.Th("Address", style={"width":150}),    html.Td("", id="table-address")])
row1 = html.Tr([    html.Th("Type"),                            html.Td("", id="table-type")])
row2 = html.Tr([    html.Th("Price"),                           html.Td("", id="table-price")])
row3 = html.Tr([    html.Th("Date of Sale"),                    html.Td("", id="table-date")])
row4 = html.Tr([    html.Th("Price per m2"),                    html.Td("", id="table-m2price")])
row5 = html.Tr([    html.Th("House Size"),                      html.Td("", id="table-house-size")])
row6 = html.Tr([    html.Th("Lot Size"),                        html.Td("", id="table-lot-size")])
row7 = html.Tr([    html.Th("Number of Rooms"),                 html.Td("", id="table-rooms")])
row8 = html.Tr([    html.Th("Build Year"),                      html.Td("", id="table-buildYear")])

table_body = [html.Tbody([row0, row1, row2, row3, row4, row5, row6, row7, row8])]

info_card = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Info", className="card-title", id="info-card-title"),
            html.H6("Choose House on Map", className="card-subtitle", id="info-card-subtitle", style={'color': 'red'}),
            html.Div(dbc.Table(table_body, bordered=True), className="card-text", id="info-card-text"
            ),
        ]
    ),
)

#
#   Tabs for statistics
#
stat_card = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Sales Prices", tab_id="tab-1"),
                    dbc.Tab(label="Number of Sales", tab_id="tab-2"),
                    dbc.Tab(label="Price per m2", tab_id="tab-3"),
                ],
                id="card-tabs",
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.P(id="card-content", className="card-text")),
    ]
)

@app.callback(
    Output("card-content", "children"), 
    Input("card-tabs", "active_tab")
)
def tab_content(active_tab):
    content = ""
    if active_tab == "tab-1":
        content = dcc.Graph(id="price-hist-fig")
    elif active_tab == "tab-2":
        content = dcc.Graph(id="number-of-sales-fig")
    elif active_tab == "tab-3":
        content = dcc.Graph(id="m2prices-fig")
    return content


#
#   Page layout
#

page = html.Div(
    [
        html.Div(
            [
                html.H2("Search in House Sales"),
                dbc.Card(dbc.CardBody(filters)),
                html.Div(id='result-count', 
                         style={'font-size': '14px','font-weight':'bold','margin-bottom':'10px', 'color': "succes"})
            ]
        ),
        html.Div(
            [
                dcc.Graph(id="map-fig"),
            ],
            style={'width': '60%', 'display': 'inline-block', 'vertical-align':'top', "padding-top": 30}
        ),
        html.Div(
            [ 
                html.H4("Overview of Search Result"),
                stat_card,
                html.Br(),
                info_card
            ],
            style={'width': '40%', 'display': 'inline-block', 'vertical-align':'top'}
        ),
        dcc.Store(id="filtered-data")
    ]
)

#
#   6 callbacks for updating displays with chosen filter values
#


@app.callback(
    Output("price-slider-min", "children"),
    Output("price-slider-max", "children"),
    Input("price-slider", "value")
)
def update_chosen_price_range_display(price_range):
    min_price = '{:,}'.format(price_range[0]) + " kr."
    max_price = '{:,}'.format(price_range[1]) + " kr."
    if price_range[1] == 10_000_000:
        max_price = max_price + " +"
    return min_price, max_price


@app.callback(
    Output("room-slider-min", "children"),
    Output("room-slider-max", "children"),
    Input("room-slider", "value")
)
def update_chosen_room_range_display(room_range):
    min_room = room_range[0]
    max_room = room_range[1]
    if max_room == 9:
        max_room = str(max_room) + "+"
    return min_room, max_room


@app.callback(
    Output("house-size-slider-min", "children"),
    Output("house-size-slider-max", "children"),
    Input("house-size-slider", "value")
)
def update_chosen_house_size_range_display(size_range):
    min_size= str(size_range[0]) + " m2"
    max_size = str(size_range[1]) + " m2"
    if max_size == "250 m2":
        max_size = max_size + "+"
    return min_size, max_size


@app.callback(
    Output("lot-size-slider-min", "children"),
    Output("lot-size-slider-max", "children"),
    Input("lot-size-slider", "value")
)
def update_chosen_lot_size_range_display(size_range):
    min_size= str(size_range[0]) + " m2"
    max_size = '{:,}'.format(size_range[1]) + " m2"
    if max_size == "10,000 m2":
        max_size = max_size + "+"
    return min_size, max_size


@app.callback(
    Output("build-year-slider-min", "children"),
    Output("build-year-slider-max", "children"),
    Input("build-year-slider", "value")
)
def update_chosen_build_year_size_range_display(year_range):
    min_year = str(year_range[0])
    max_year = str(year_range[1])
    if min_year == "1900":
        min_year = min_year + " or before"
    if max_year == "2020":
        max_year = "2021"
    return min_year, max_year


@app.callback(
    Output("time-slider-min", "children"),
    Output("time-slider-max", "children"),
    Input("time-slider", "value")
)
def update_chosen_sales_time_range_display(time_range):
    min_time = months[int(time_range[0])]
    max_time = months[int(time_range[1])]
    return min_time, max_time


#
#   Other callbacks
#


@app.callback(
    Output("filtered-data", "data"),
    Input("price-slider", "value"),
    Input("time-slider", "value"),
    Input("house-size-slider", "value"),
    Input("lot-size-slider", "value"),
    Input("room-slider", "value"),
    Input("build-year-slider", "value"),
    Input("type-choice", "value"),
    Input("map-fig", 'relayoutData')
)
def apply_filters(price_range, time_range, house_size_range, lot_size_range, 
                  room_range, build_year_range, type_choices, zoom_range):
    df = sales
    
    # Filter on type of house
    df = df[df['type'].isin(type_choices)]
    
    # Filter on price
    if price_range[1] == 10_000_000:
        df = df[df.price >= price_range[0]]
    else:
        df = df[df.price.between(*price_range)]
    
    # Filter on time of sale
    min_time = months[int(time_range[0])]
    max_time = months[int(time_range[1])]
    df = df[df['datetimes'].between(min_time, max_time)]

    # Filter on house size
    if house_size_range[1] == 250:
        df = df[df['size'] >= house_size_range[0]]
    else:
        df = df[df['size'].between(*house_size_range)]
    
    # Filter on lot size
    if lot_size_range[1] == 10_000:
        df = df[df.lotSize >= lot_size_range[0]]
    else:
        df = df[df.lotSize.between(*lot_size_range)]
    
    # Filter on number of rooms
    if room_range[0] == 0 and room_range[1]==9:
        df = df    
    elif room_range[1] == 9:
        df = df[df.rooms >= room_range[0]]
    else:
        df = df[df.rooms.between(*room_range)]
    
    # Filter on year build
    if build_year_range[0] == 1900 and build_year_range[1] != 2020:
        df = df[df.buildYear <= build_year_range[1]]
    elif build_year_range[1] == 2020 and build_year_range[0] != 1900:
        df = df[df.buildYear >= build_year_range[0]]
    else:
        df = df[df.buildYear.between(*build_year_range)]
    
    if zoom_range and "mapbox._derived" in zoom_range:
        
        min_longitude = zoom_range["mapbox._derived"]['coordinates'][0][0]
        max_longitude = zoom_range["mapbox._derived"]['coordinates'][1][0]
        
        min_latitude = zoom_range["mapbox._derived"]['coordinates'][2][1]
        max_latitude = zoom_range["mapbox._derived"]['coordinates'][0][1]

        df = df[df.latitude.between(min_latitude, max_latitude)]
        df = df[df.longitude.between(min_longitude, max_longitude)]
        
    return df.to_json()


@app.callback(
    Output("map-fig", "figure"),
    Input("filtered-data", "data"),
    Input("map-fig", "clickData")
)
def update_map(data, clickData):
    df = pd.read_json(data)
    fig = px.scatter_mapbox(df, 
                            lat="latitude", 
                            lon="longitude", 
                            color="price",
                            height=840,
                            zoom=8.3,
                            center=dict(lat=55.18,lon=10.3),
                            hover_data=['salesDate', 'rooms', 'lotSize','buildYear', 'm2price', 'size', 'type'],
                            labels={"price": "Price in DKK"},
                            template="simple_white",
                            range_color=[0, 10_000_000],
                            )
    fig.update_traces(hovertemplate='<b>%{text}</b><br>Price %{marker.color: ,} kr.',
                      text=df.address)
    fig.update_layout(mapbox_style="open-street-map")
    # Move colorbar to the left
    fig.update_layout(coloraxis_colorbar_x=-0.25)
    # Change ticks on colorbar away from 3M to 3,000,000
    fig.update_coloraxes(colorbar_tickformat=',')
    # Making markers bigger
    fig.update_traces(marker={'size': 8})
    # Prevent zoom reset when selecting house on map
    fig.update_layout(uirevision="static")
    fig.update_layout(margin={'l': 0, 'r': 30, 't': 5, 'b': 30})
    # Coloring the selected house red on the map
    if clickData:
        fig.add_trace(go.Scattermapbox(lat=[clickData['points'][0]['lat']], 
                                    lon=[clickData['points'][0]['lon']], 
                                    mode='markers', 
                                    marker=go.scattermapbox.Marker(color='red', size=12),
                                    hovertemplate="<b>Selected</b><extra></extra>",
                                    showlegend=False,))
    return fig


@app.callback(
    Output("price-hist-fig", "figure"),
    Input("filtered-data", "data"),
    Input("map-fig", "clickData")
)
def update_histogram(data, clickData):
    filtered_data = pd.read_json(data)
    fig = px.histogram(filtered_data, 
                        x='price',
                        template="simple_white",
                        height=250,
                        labels={'price': "Price in DKK"})
    fig.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
    fig.update_yaxes({'title': {'text': 'Count'}})
    if clickData:
        x = clickData['points'][0]['marker.color']
        fig.add_vline(x=x, 
                    line_width=4, 
                    line_dash="dash", 
                    line_color="red", 
                    opacity=0.8)
    return fig


@app.callback(
    Output("m2prices-fig", "figure"),
    Input("filtered-data", "data"),
    Input("map-fig", "clickData")
)
def update_histogram_m2_prices(data, clickData):
    filtered_data = pd.read_json(data)
    fig = px.histogram(filtered_data, 
                        x='m2price',
                        template="simple_white",
                        height=250,
                        labels={'m2price': "Price per m2 in DKK"})
    fig.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
    fig.update_yaxes({'title': {'text': 'Count'}})
    if clickData:
        x = clickData['points'][0]['customdata'][4]
        fig.add_vline(x=x, 
                  line_width=4, 
                  line_dash="dash", 
                  line_color="red",
                  opacity=0.8)
    return fig


@app.callback(
    Output("number-of-sales-fig", "figure"),
    Input("filtered-data", "data"),
    Input("map-fig", "clickData")
)
def update_histogram_number_of_sales(data, clickData):
    filtered_data = pd.read_json(data) 
    x = filtered_data.salesDate
    y = [1] * len(x)
    fig = px.histogram(x=x, 
                        y=y,
                        template="simple_white",
                        height=250,
                        labels={'x': "Time of Sale"})
    fig.update_traces(xbins=dict(
                        start='2019-07-01',
                        end='2021-11-31',
                        size='M1'))
    fig.update_layout(margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
    fig.update_yaxes({'title': {'text': 'Count'}})
    if clickData:
        x = clickData['points'][0]['customdata'][0]
        fig.add_vline(x=x, 
                    line_width=4, 
                    line_dash="dash", 
                    line_color="red", 
                    opacity=0.8)
    return fig



@app.callback(
    Output("table-address", "children"),
    Output("table-type", "children"),
    Output("table-price", "children"),
    Output("table-date", "children"),
    Output("table-m2price", "children"),
    Output("table-house-size", "children"),
    Output("table-lot-size", "children"),
    Output("table-rooms", "children"),
    Output("table-buildYear", "children"),
    Input("map-fig", "clickData")
)
def update_info_card(clickData):
    address = ""
    house_type = ""
    price = ""
    salesDate = ""
    m2price = ""
    house_size = ""
    lot_size = ""
    rooms = ""
    buildYear = ""
    
    if clickData:
        house_type = clickData['points'][0]['customdata'][6]
        rooms = clickData['points'][0]['customdata'][1]
        lot_size = '{:,}'.format(clickData['points'][0]['customdata'][2]) + " m2"
        buildYear = clickData['points'][0]['customdata'][3]
        m2price = "{:,.2f}".format(clickData['points'][0]['customdata'][4]) + " kr."
        house_size = str(clickData['points'][0]['customdata'][5]) + " m2"
        address = clickData['points'][0]['text']
        price = '{:,}'.format(clickData['points'][0]['marker.color']) + " kr."
        salesDate = clickData['points'][0]['customdata'][0]
        if type(salesDate) is str:
            salesDate = salesDate[0:10]

    return address, house_type, price, salesDate, m2price, house_size, lot_size, rooms, buildYear


@app.callback(
    Output("info-card-title", "children"),
    Output("info-card-subtitle", "children"),
    Input("map-fig", "clickData")
)
def update_info_card_headers(clickData):
    title = "Info"
    subtitle = "Choose House on Map"
    red_dot_image = ""
    if clickData:
        subtitle = ""
        address = clickData['points'][0]['text']
        street, city = address.split(",")
        red_dot_image = html.Img(src="assets/red_dot.png", height=24, style={"padding-right": 10, "padding-bottom": 4})
        title = [red_dot_image, street]
    return title, subtitle



@app.callback(
    Output('result-count', 'children'),
    Input('filtered-data', 'data'),
)
def update_num_results(data):
    filtered_data = pd.read_json(data)
    return f"Your search gave {len(filtered_data)} results"