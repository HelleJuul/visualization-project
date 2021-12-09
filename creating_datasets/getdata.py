import requests
import pandas as pd
import json
import numpy as np
url = 'http://journalistbot.dk/api/bolighandler/fyn'

# response = requests.get(url)

# # If the response was successful, no Exception will be raised
# data = json.loads(response.text)

# df = pd.DataFrame([x for x in data])
# print(len(df.columns))
# clean_df = df.drop(['news_id','BBRNummer','BFENummer','ejendomsvaerdiSamlet','etage','handelKategori','overtagelsesDato','skoedeTekst','suppl_opvarmningtype','tinglysningsDato','ydervaegtype','datoLoebenr','created_at','updated_at'],axis=1)



def getCleanOptions(inputArr):
    optionList = inputArr.unique()
    optionList = np.delete(optionList, np.where(optionList == 0))
    return np.sort(optionList)

def castColumnAsInt(inputCol):
    inputCol.fillna(0)
    inputCol.replace({"": "0"}, inplace=True)
    inputCol.replace({np.nan: "0"}, inplace=True)
    resultCol = pd.to_numeric(inputCol, downcast='signed')
    return resultCol

# Dataset for page 2 with individual sales data
with open('housesales.csv', 'r') as f:
    housesales = pd.read_csv(f)
    housesales['opfoerelse'] = castColumnAsInt(housesales['opfoerelse'])
    housesales['antBadevaerelser'].replace({"0": "1",np.nan:"1"}, inplace=True)
    housesales['antBadevaerelser'] = castColumnAsInt(housesales['antBadevaerelser'])
    housesales['antVaerelser'] = castColumnAsInt(housesales['antVaerelser'])
    housesales['beboelsesAreal'] = castColumnAsInt(housesales['beboelsesAreal'])

#options for design elements
opfoerelseOptions = getCleanOptions(housesales['opfoerelse'])
antBadevaerelserOptions = getCleanOptions(housesales['antBadevaerelser'])
antVaerelserOptions = getCleanOptions(housesales['antVaerelser'])
boligTypeOptions = getCleanOptions(housesales['boligTypeTekst'])

#print(type(housesales['opfoerelse'][9]))
# print(type(housesales['antBadevaerelser'][9]))
# print(type(housesales['antVaerelser'][9]))

dick = housesales['antBadevaerelser'][(housesales['antBadevaerelser'] >= 1)]
# print(opfoerelseOptions)
print(housesales['antBadevaerelser'])
#print(housesales['beboelsesAreal'][5])
# print(boligTypeOptions)