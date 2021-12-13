from dash import Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc

import pandas as pd
import json

import plotly.express as px
import plotly.graph_objects as go

from app import app

#
# Loading the data
#

# Geojson file with the shape of the zip code areas on Fyn with a unique ID pr shape 
with open('data/zip_code_areas_fyn_with_id.geojson', "r") as f:
    zip_code_areas = json.load(f)

# Dataset with the number of sales per quarter optimized for the map
with open('data/total_sales_by_quarter.csv', "r") as f:
    total_sales = pd.read_csv(f)

# Dataset with the number of sales per quarter optimized for the bar chart
with open('data/total_sales_by_quarter_for_bar.csv', "r") as f:
    total_sales_bar = pd.read_csv(f)

#
#   Helper functions
#
def translate_zips_to_ids_and_colors(zips):
    '''Return a list with the IDs corresponding to the zip codes in zips'''
    ids = []
    colors = px.colors.qualitative.Vivid    # 11 colors
    for i, zip_code in enumerate(zips):
        color_index = i % 11
        color = colors[color_index]
        zip_text = str(zip_code)
        for item in zip_code_areas['features']:
            if item['properties']['POSTNR_TXT'] == zip_text:
                ids.append((item['id'], color))
    return ids

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
                               id="rel_abs_radio"),
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
    Input("zip_dropdown_total_sales", "value"),
    Input("total_sales_bar", "clickData"),
    Input("month_slider_total_sales", "value"),
    )
def update_choropleth_with_total_sales(rel_or_abs, selected_zips, clickData, date):
    '''Create and update the choropleth map of Fyn with number of sold houses'''
    quarter = "2021-Q4"
    if rel_or_abs == "rel_num":
        color = "rel_sales"
        range_color = [0, 75]
        color_scale = "Blues"
    else:
        color = "sales"
        range_color = [0, 150]
        color_scale = "Greens"
    
    ctx = callback_context
    id_called = None
    if ctx.triggered:
        id_called = ctx.triggered[0]["prop_id"].split(".")[0]
    if id_called and id_called == "month_slider_total_sales" and date:
        quarter = quarters[date]
    if id_called and id_called == "total_sales_bar":
        quarter = clickData["points"][0]["x"]
    total_sales_selected_quarter = total_sales[total_sales.quarter_name==quarter]
    # Change the coloring according to the chosen month
    fig = px.choropleth(total_sales_selected_quarter,
                geojson=zip_code_areas, 
                color=color, 
                locations='id',
                projection="mercator",
                range_color=range_color,
                color_continuous_scale=color_scale,
                height=450,
                template='simple_white',
                labels={"sales": 'Number of Sales',
                        "rel_sales": "Sales per 1000 Residences"})
    # Zoom in on Fyn
    fig.update_geos(fitbounds="locations", visible=False)
    # Remove margins and Move colorbar to the left
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      coloraxis_colorbar_x=-0.08)
    # Make the hover data look nice
    area_zips_and_names = list(total_sales['zip_code'].apply(str) + " " + total_sales['name'].apply(str))
    fig.update_traces(hovertemplate='<b>%{customdata}</b><br>%{z}', 
                      customdata=area_zips_and_names)
    # Highlight selected zips on the map
    id_color_pairs = translate_zips_to_ids_and_colors(selected_zips)
    for ic in id_color_pairs:
        fig.add_trace(go.Choropleth(geojson=zip_code_areas,
                                    locationmode="geojson-id",
                                    locations=[ic[0]],
                                    z = [1],
                                    colorscale = [[0, 'rgba(0,0,0,0)'],[1, 'rgba(0,0,0,0)']],
                                    colorbar=None,
                                    showscale =False,
                                    marker = {"line": {"color": ic[1], "width": 3}},
                                    hoverinfo='skip'))
    return  fig


@app.callback(
    Output("total_sales_header", "children"),
    Input("total_sales_bar", "clickData"),
    Input("month_slider_total_sales", "value"),
    )
def update_title_to_match_chosen_quarter_total_sales(clickData, date):
    '''Change the title to show the chosen month and year.'''
    quarter = "2021-Q4"
    ctx = callback_context
    id_called = None
    if ctx.triggered:
        id_called = ctx.triggered[0]["prop_id"].split(".")[0]
    if id_called and id_called == "month_slider_total_sales" and date:
        quarter = quarters[date]
    if id_called and id_called == "total_sales_bar":
        quarter = clickData["points"][0]["x"]
    return quarter


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
    Input("total_sales_bar", "clickData"),
    Input("month_slider_total_sales", "value"),
    )
def update_bar_chart_with_total_sales(rel_or_abs, selected_zips, clickData, date):
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
                          'color':      'Zip Code',
                          'quarter_name':    'Quarter',
                          'sales':  'Number of Sales',
                          'rel_sales': "Sales per 1000<br>Residences"})
    # Smaller text on y-axis
    fig.update_yaxes(title_font=dict(size=10))
    # Add a rectangle to highlight the selected quarter
    quarter = "2021-Q4"
    ctx = callback_context
    id_called = None
    if ctx.triggered:
        id_called = ctx.triggered[0]["prop_id"].split(".")[0]
    if id_called and id_called == "month_slider_total_sales" and date:
        quarter = quarters[date]
    if id_called and id_called == "total_sales_bar":
        quarter = clickData["points"][0]["x"]
    fig.add_vrect(x0=quarter, x1=quarter, col=1,
              fillcolor="green", opacity=0.10, line_width=45)

    # Make hover data look nice
    fig.update_traces(hovertemplate=None)
    fig.update_layout(hovermode="x")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=20, pad=10))
    return fig


@app.callback(
    Output("month_slider_total_sales", "value"),
    Input("total_sales_bar", "clickData")
)
def update_slider_on_plot_click(clickData):
    if clickData:
        return quarters.index(clickData['points'][0]['x'])