from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc

from app import app
from pages import m2prices, totalsales, salesprices_and_overview

# Setting the main layout with a fixed navbar at the top
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Img(src="assets/house_blue.png", height="40px")),
                    dbc.Col(dbc.NavbarBrand("Sold House Prices on Fyn", className="ms-2", href="/")),
                ],
                align="center",
                className="g-0",
            ),
            dbc.NavItem(dbc.NavLink("Search in House Sales", href="/", active='exact')),
            dbc.NavItem(dbc.NavLink("Average Price per m2", href="/page-1", active='exact')),
            dbc.NavItem(dbc.NavLink("Number of Houses Sold", href="/page-2", active='exact')),
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
    ],
    fluid=True,
)


@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname")
    )
def render_page_content(pathname):
    if pathname == "/":
        return salesprices_and_overview.page
    elif pathname == "/page-1":
        return m2prices.page1
    elif pathname == "/page-2":
        return totalsales.page0
    # If the user tries to reach a different page, return a 404 message
    else:
        return html.H1("404: Not found", className="text-danger")


if __name__ == "__main__":
    app.run_server(debug=False)