from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np

import plotly.express as px

from app import app
from pages.m2prices import dropdown_options


# Helpers:

def getCleanOptions(inputArr):
    optionList = inputArr.unique()
    optionList = np.delete(optionList, np.where(optionList == 0))
    return np.sort(optionList)


def castColumnAsInt(inputCol):
    inputCol.fillna(0)
    inputCol.replace({"": "0", np.nan: "0"}, inplace=True)
    resultCol = pd.to_numeric(inputCol, downcast='signed')
    return resultCol


# Dataset for page 2 with individual sales data
with open('data/housesales.csv', 'r') as f:
    housesales = pd.read_csv(f)
    housesales['opfoerelse'] = castColumnAsInt(housesales['opfoerelse'])
    housesales['antBadevaerelser'].replace(
        {"0": "1", np.nan: "1"}, inplace=True)
    housesales['antBadevaerelser'] = castColumnAsInt(
        housesales['antBadevaerelser'])
    housesales['antVaerelser'] = castColumnAsInt(housesales['antVaerelser'])
    housesales['beboelsesAreal'] = castColumnAsInt(
        housesales['beboelsesAreal'])

# options for design elements
opfoerelseOptions = getCleanOptions(housesales['opfoerelse'])
antBadevaerelserOptions = getCleanOptions(housesales['antBadevaerelser'])
antVaerelserOptions = getCleanOptions(housesales['antVaerelser'])
boligTypeOptions = getCleanOptions(housesales['boligTypeTekst'])

#print(housesales['antBadevaerelser'][10000])
#print(type(housesales['antBadevaerelser'][10000]))

# design
page2 = dbc.Container(
    [
        html.H1(id="house_sales_header",
                children="Search in house sales"),
        html.Div(children=[
            html.Div(children=[
                html.Div("Choose Zip Code Areas", className="form-label"),
                dcc.Dropdown(
                    options=dropdown_options,
                    value='',
                    id='page2_zip_dropdown'
                ),
                html.Div("Choose date interval", className="form-label"),
                dcc.DatePickerRange(
                    start_date="2021-01-01",
                    end_date="2022-01-01",
                    start_date_placeholder_text="Start Period",
                    end_date_placeholder_text="End Period",
                    calendar_orientation='vertical',
                    id='page2_datepicker'
                ),
                html.Div("Choose minimum sales price", className="form-label"),
                dcc.Dropdown(
                    options=[
                        {'label': '1.000.000', 'value': 1000000},
                        {'label': '2.000.000', 'value': 2000000},
                        {'label': '3.000.000', 'value': 3000000},
                        {'label': '4.000.000', 'value': 4000000},
                        {'label': '5.000.000', 'value': 5000000},
                        {'label': '6.000.000', 'value': 6000000},
                        {'label': '7.000.000', 'value': 7000000},
                        {'label': '8.000.000', 'value': 8000000},
                    ],
                    value=0,
                    id='page2_price_dropdown'
                ),
            ], style={'width': '47%', 'display': 'inline-block'}),
            html.Div(children=[
                html.Div("Choose type", className="form-label"),
                dcc.Dropdown(
                    options=[{'label': x, 'value': x}
                             for x in boligTypeOptions],
                    value='Alle',
                    id='type_dropdown'
                ),
                html.Div("Minimum size of living area",
                         className="form-label"),
                dcc.Slider(
                    id='sqrmeters_slider',
                    min=10,
                    max=300,
                    step=10,
                    tooltip={"placement": "bottom", "always_visible": True},
                    value=130
                ),
                html.Div("Choose year build", className="form-label"),
                dcc.RangeSlider(
                    id='yearbuild_slider',
                    min=1700,
                    max=2021,
                    step=10,
                    allowCross=False,
                    tooltip={"placement": "bottom", "always_visible": True},
                    value=[1900, 2101]
                ),
                html.Div("Minimum number of rooms", className="form-label"),
                dcc.Slider(
                    id='rooms_slider',
                    min=1,
                    max=10,
                    step=1,
                    value=4,
                    tooltip={"placement": "bottom", "always_visible": True},

                )
                
            ], style={'width': '47%', 'display': 'inline-block'}),


        ], style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),
        html.Div(id='filterBadgesDiv', style={'margin-bottom': '10px'}),
        html.Div(id='numResultsDiv', style={'font-size': '14px','font-weight':'bold','margin-bottom':'10px'}),
        dcc.Graph(id='indicator-graphic'),
        dcc.Store(id='searchData')
    ],
    style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'},

)

#
#   Callbacks PAGE 2: RUNE
#
# Callback for storing data in the store.


@app.callback(
    Output('searchData', 'data'),
    Input('page2_zip_dropdown', 'value'),
    Input('page2_datepicker', 'start_date'),
    Input('page2_datepicker', 'end_date'),
    Input('page2_price_dropdown', 'value'),
    Input('type_dropdown', 'value'),
    Input('yearbuild_slider', 'value'),
    Input('rooms_slider', 'value'),
    Input('sqrmeters_slider', 'value'))
def search_data(page2_zip_dropdown, start_date, end_date, page2_price_dropdown, typeHouse, yearbuild, rooms, sqrmeters):
    search_result_housesales = housesales

    search_result_housesales = search_result_housesales[(search_result_housesales['publishDate'] > start_date) & (
        search_result_housesales['publishDate'] < end_date)]

    search_result_housesales = search_result_housesales[(search_result_housesales['opfoerelse'] > yearbuild[0]) & (
        search_result_housesales['opfoerelse'] < yearbuild[1])]

    search_result_housesales = search_result_housesales[
        search_result_housesales['beboelsesAreal'] > sqrmeters]

    search_result_housesales = search_result_housesales[
        search_result_housesales['antVaerelser'] >= rooms]

    if page2_zip_dropdown != '':
        search_result_housesales = search_result_housesales[
            search_result_housesales['postNr'] == page2_zip_dropdown]

    if page2_price_dropdown != 0:
        search_result_housesales = search_result_housesales[
            search_result_housesales['iAltKoebeSum'] > page2_price_dropdown]

    if typeHouse != "Alle":
        search_result_housesales = search_result_housesales[
            search_result_housesales['boligTypeTekst'] == typeHouse]
   
    return search_result_housesales.to_json(date_format='iso', orient='split')

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('searchData', 'data'))
def update_map(data):
    dff = pd.read_json(data, orient='split')
    #print("call")
    fig = px.scatter_mapbox(dff, lat="latitude", lon="longitude", color="iAltKoebeSum",
                            height=640, hover_name='vejNavn', hover_data=["iAltKoebeSum", "husNr", "antBadevaerelser", "antVaerelser"])
    fig.update_geos(fitbounds='locations')

    fig.update_layout(mapbox_style="open-street-map",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


@app.callback(
    Output('filterBadgesDiv', 'children'),
    Input('page2_zip_dropdown', 'value'),
    Input('page2_datepicker', 'start_date'),
    Input('page2_datepicker', 'end_date'),
    Input('page2_price_dropdown', 'value'),
    Input('type_dropdown', 'value'))
def update_div(zip, start_date, end_date, price, typeHouse):
    badges = html.Span(
        [
            dbc.Badge("Search filters: ", color="secondary", className="me-2"),
            dbc.Badge("Zipcode: " + str("All" if zip == "" else zip), color="success", className="me-1"),
            dbc.Badge("Time period: "+str(start_date)+" - "+str(end_date), color="success", className="me-1"),
            dbc.Badge("Min. price: "+str(1000000 if price == 0 else price), color="success", className="me-1"),
            dbc.Badge("Type: "+str(typeHouse), color="success", className="me-1"),
        ]
    )
    return badges


@app.callback(
    Output('numResultsDiv', 'children'),
    Input('searchData', 'data'),
)
def update_num_results(data):
    dff = pd.read_json(data, orient='split')
    return f"Your search yielded {len(dff)} results"