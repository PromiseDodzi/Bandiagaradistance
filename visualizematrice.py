from getting_matrices import getdata

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import folium

def getheatmap(geographic_mtx, linguistic_matx):
    "returns heatmaps of the two distance matrixes"

    plt.figure(figsize=(15, 6))

    plt.subplot(1, 2, 1)
    sns.heatmap(geographic_mtx, annot=False, cmap='viridis')
    plt.title('Geographic Distance Matrix')

    plt.subplot(1, 2, 2)
    sns.heatmap(pd.DataFrame(linguistic_matx), annot=False, cmap='viridis')
    plt.title('Linguistic Distance Matrix')

    plt.tight_layout()

    return plt.savefig("Heatmap of geographic and linguistic distance matrix")


def getgeomap(coordinates):
    "gets geomap of languages and their location on map"
    map_center = [coordinates['latitude'].mean(), coordinates['longitude'].mean()]
    language_map = folium.Map(location=map_center, zoom_start=2)

    for _, row in coordinates.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=row['glottolog_name'],  
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(language_map)

        folium.map.Marker(
            [row['latitude'], row['longitude']],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 12px; color: blue;">{row["glottolog_name"]}</div>'
            )
        ).add_to(language_map)

    return language_map.save('language_map.html')

def getdescriptivemaps(geographic_matx,linguistic_matx):
    ling_describe=pd.DataFrame(linguistic_matx.describe())
    geog_describe=pd.DataFrame(geographic_matx.describe())
    ling_describe.plot(kind= "bar", legend=False)
    plt.savefig("ling_description")

    geog_describe.plot(kind= "bar", legend=False)
    plt.savefig("geo_description")


def getmaps():
    coordinates, geographic_mtx, linguistic_matx=getdata()
    ("printing graphs to file")
    getheatmap(geographic_mtx,linguistic_matx)
    getgeomap(coordinates)
    getdescriptivemaps(geographic_mtx,linguistic_matx)
    
getmaps()
    
if __name__ == "__main__":
    getmaps()







