from dash import Input, Output, State, dcc, html, callback_context
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd

import plotly.express as px

from app import app
from pages.m2prices import dropdown_options


p3view = pd.read_csv("data/p3view.csv")
sales_volume = pd.read_csv("data/sales_volume_by_zip.csv")
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


