import json
import pandas as pd
from dateutil.parser import parse
import plotly.express as px
import numpy as np
import re

# Loading the sales data
with open('fyn.json') as f:
    sales_json = json.load(f)

with open('m2prices_for_line_chart.csv') as f:
    m2prices = pd.read_csv(f)


# Creating a pandas dataframe with only the needed attributes
ATTRIBUTES = ['tinglysningsDato', 
              'iAltKoebeSum', 
              'beboelsesAreal', 
              'content',
              'boligTypeTekst',
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
               "antVaerelser":"Number of Bedrooms", "antBadevaerelser":"Number of Bathrooms","grundAreal":"Ground Area" , "postNr":"Zip Code" },
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
p3view = sales[["tinglysningsDato","iAltKoebeSum", "beboelsesAreal", "antVaerelser", "antBadevaerelser"  , "postNr", "content","boligTypeTekst"] ]
p3view["antBadevaerelser"] = p3view["antBadevaerelser"].fillna("unknown")
p3view["antVaerelser"] = p3view["antVaerelser"].replace("","unknown")

p3view.dropna(subset=["iAltKoebeSum"], inplace=True)
p3view = p3view[p3view["iAltKoebeSum"] != 0]
  # match = re.search(r"Grunden, som ejendommen ligger på, er [\d]+ kvadratmeter", s)
    # match = re.search(r"Grunden, som ejendommen|Ejendommen ligger på en grund|Ejendommen ligger på et grundstykke|Grunden udgør et areal ", s)

p3view = p3view[p3view["content"] != ""]

patterns = [
    r"Grunden, som ejendommen ligger på, er [\d]+ kvadratmeter",
    r"Ejendommen udgør i alt et areal på [\d]+ kvadratmeter",
    r"Ejendommen ligger på en grund, der er [\d]+ kvadratmeter",
    r"Ejendommen ligger på et grundstykke, der er [\d]+ kvadratmeter",
    r"Grunden udgør et areal på [\d]+ kvadratmeter"
        ]

pattern = "|".join(patterns)

#798
# 1551
# 3191
# 5400
# 8836
# 8837
# 8838
# 8839

groundarea =  []
for i,tup in enumerate(zip(p3view["content"],p3view['boligTypeTekst'])):
    s,t = tup
    match = re.search(pattern, s)
    if t == "Ejerlejlighed":
        groundarea.append(0)
    elif match:
        clean = re.sub(r"[^\d]","", match.group())
        groundarea.append(int(clean))
    else:
        print(i)
        # groundarea.append(1)
    # else:
        # groundarea.append(-1)

p3view["Ground Area"] = np.array(groundarea)
p3view.rename(columns={"iAltKoebeSum":"Sales Price", "tinglysningsDato":"Registration Date", "beboelsesAreal":"Living Area",
               "antVaerelser":"Number of Bedrooms", "antBadevaerelser":"Number of Bathrooms", "postNr":"Zip Code", "boligTypeTekst":"Type"},
              inplace=True)
p3view.to_csv("p3view.csv")


#%% 