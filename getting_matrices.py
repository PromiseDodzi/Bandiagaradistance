import numpy as np
import pandas as pd

from fuzzywuzzy import fuzz
from sklearn.preprocessing import MinMaxScaler

from lingpy import *

from preparelanguagedata import fullAlign


def get_correct_name(linguistic_distance, geographic_data, threshold=70):
    "harmonizes the names of languages accross datasets"
   
    for i, row in geographic_data.iterrows():
        for name in linguistic_distance.columns:
            if "Najamba" in row['glottolog_name']:
                geographic_data.at[i, "glottolog_name"]="BonduSoNajamba"
            elif "Yorno" in row['glottolog_name']:
                geographic_data.at[i, "glottolog_name"]="YornoSo"
            elif fuzz.partial_ratio(row['glottolog_name'], name) >= threshold:
                geographic_data.at[i, 'glottolog_name'] = name
                break 
    
    return geographic_data

def dropdog(name):
    "returns clean language names"
    if "Dogon" in name:
        name=name.replace("Dogon", "").strip()
        return name.replace(" ", "")
    else:
        return name.replace(" ", "")
    
#cordinates data
def cleancoordinates(link):
    "returns a cleaned cordinates dataframe"
    coordinates=pd.read_csv(link)
    coordinates=coordinates[coordinates["family"]=="Dogon"]
    coordinates=coordinates[["latitude", "longitude", "glottolog_name"]]
    coordinates["glottolog_name"] = coordinates["glottolog_name"].apply(dropdog)
    to_keep=list(set(coordinates['glottolog_name'].unique())-set(['Nanga','Guru(Mali)', 'IbiSo', 'Ampari']))
    coordinates = coordinates[coordinates['glottolog_name'].isin(to_keep)]
    coordinates=coordinates.drop([169, 175,178,182])
    return coordinates

def cleanlanguagematrix():
    "returns a cleaned linguistic distance matrix"
    #read language distance matrix and clean it
    fullAlign()
    language_matrix=pd.read_csv("linguistic_distance.tsv", sep="\t")
    language_matrix.set_index('Unnamed: 0', inplace=True)
    to_drop=['DogulDomKundialang', 'JamsayGourou', 'JamsayMondoro']
    language_matrix=language_matrix.drop (to_drop, axis=1)
    language_matrix=language_matrix.drop (to_drop, axis=0)
    return language_matrix
    
def getdistancematrix(coordinates):
    "returns a geographical distance matrix"

    def haversine(lat1, lon1, lat2, lon2):
        "uses haersine method to calculate geographical distance between cordinates"
        R = 6371  # Earth radius in kilometers
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        
        a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c

    languages = coordinates['glottolog_name'].tolist()
    num_languages = len(languages)
    distance_matrix = np.zeros((num_languages, num_languages))

    for i in range(num_languages):
        lat1, lon1 = coordinates.iloc[i]['latitude'], coordinates.iloc[i]['longitude']
        for j in range(i + 1, num_languages):
            lat2, lon2 = coordinates.iloc[j]['latitude'], coordinates.iloc[j]['longitude']
            distance = haversine(lat1, lon1, lat2, lon2)
            distance_matrix[i, j] = distance
            distance_matrix[j, i] = distance  

    distance_df = pd.DataFrame(distance_matrix, index=languages, columns=languages)
    return distance_df

def normalizematrix(geographical_distance):
    "normalizes the geographical distance matrix"
    scaler = MinMaxScaler()
    array = geographical_distance.to_numpy()
    normalized_array = scaler.fit_transform(array)
    normalized_distance_matrix = pd.DataFrame(normalized_array, columns=geographical_distance.columns, index=geographical_distance.index)
    return normalized_distance_matrix


def getdata(geodata="Geodata.csv"):
    coordinates=cleancoordinates(geodata)
    linguistic_distance=cleanlanguagematrix()
    coordinates=get_correct_name(linguistic_distance,coordinates)
    geographical_distance=normalizematrix(getdistancematrix(coordinates))
    return coordinates, geographical_distance, linguistic_distance







