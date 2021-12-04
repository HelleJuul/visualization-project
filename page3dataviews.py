import json
import pandas as pd
from dateutil.parser import parse
import plotly.express as px
import numpy as np

# Loading the sales data
with open('fyn.json') as f:
    sales_json = json.load(f)

with open('m2prices_for_line_chart.csv') as f:
    m2prices = pd.read_csv(f)


# Creating a pandas dataframe with only the needed attributes
ATTRIBUTES = ['tinglysningsDato', 
              'iAltKoebeSum', 
              'beboelsesAreal', 
              'antBadevaerelser',
              'antVaerelser',
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
sales.tinglysningsDato = sales.tinglysningsDato.apply(parse)

months = m2prices["index"]
number_of_sales = pd.DataFrame(np.array(months, dtype="str"), columns=["month"])
for zipcode in sales.postNr.unique():
    relevant_sales = sales[sales["postNr"]==zipcode]
    num_sales = []
    for month in months:
        y,m = month.split("-")
        y,m = int(y), int(m)
        num = sum(map(lambda d: d.year == y and d.month == m, relevant_sales["tinglysningsDato"]))
        num_sales.append(num)
    number_of_sales[str(zipcode)] = np.array(num_sales)

number_of_sales.rename(columns={"iAltKoebeSum":"Sales Price", "tinglysningsDato":"Registration Date", "beboelsesAreal":"Living Area",
               "antVaerelser":"Number of Bedrooms", "antBadevaerelser":"Number of Bathrooms", "postNr":"Zip Code" },
              inplace=True)
number_of_sales.to_csv("sales_volume_by_zip.csv")

# # Fixing data types
# sales.latitude = sales.latitude.apply(float)
# sales.longitude = sales.longitude.apply(float)
# 

# sales.sort_values(by=['iAltKoebeSum'], ascending=True, inplace=True)

# fig = px.scatter_mapbox(sales, 
#                         lat='latitude', 
#                         lon='longitude', 
#                         color='iAltKoebeSum', 
#                         template='simple_white',
#                         height=700)


# fig.update_layout(mapbox = {'style': 'open-street-map'})
#%%
p3view = sales[["tinglysningsDato","iAltKoebeSum", "beboelsesAreal", "antVaerelser", "antBadevaerelser"  , "postNr"] ]
p3view["antBadevaerelser"] = p3view["antBadevaerelser"].fillna("unknown")
p3view["antVaerelser"] = p3view["antVaerelser"].astype("str").fillna("unknown")

p3view.dropna(subset=["iAltKoebeSum"], inplace=True)
p3view = p3view[p3view["iAltKoebeSum"] != 0]
p3view.rename(columns={"iAltKoebeSum":"Sales Price", "tinglysningsDato":"Registration Date", "beboelsesAreal":"Living Area",
               "antVaerelser":"Number of Bedrooms", "antBadevaerelser":"Number of Bathrooms", "postNr":"Zip Code" },
              inplace=True)
p3view.to_csv("p3view.csv")
