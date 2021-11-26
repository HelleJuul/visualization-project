import json
import pandas as pd
from dateutil.parser import parse
import plotly.express as px

# Loading the sales data
with open('fyn.json') as f:
    sales_json = json.load(f)

# Creating a pandas dataframe with only the needed attributes
ATTRIBUTES = ['tinglysningsDato', 
              'iAltKoebeSum', 
              'beboelsesAreal', 
              'kommuneNavn', 
              'postNr', 
              'latitude', 
              'longitude']

sales_list = []
for sale in sales_json:
    sale_info = []
    for attribute in ATTRIBUTES:
        sale_info.append(sale[attribute])
    sales_list.append(sale_info)

sales = pd.DataFrame(sales_list)
sales.columns = ATTRIBUTES

# Fixing data types
sales.latitude = sales.latitude.apply(float)
sales.longitude = sales.longitude.apply(float)
sales.tinglysningsDato = sales.tinglysningsDato.apply(parse)

sales.sort_values(by=['iAltKoebeSum'], ascending=True, inplace=True)

fig = px.scatter_mapbox(sales, 
                        lat='latitude', 
                        lon='longitude', 
                        color='iAltKoebeSum', 
                        template='simple_white',
                        height=700)
fig.update_layout(mapbox = {'style': 'open-street-map'})