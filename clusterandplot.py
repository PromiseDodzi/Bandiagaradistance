import numpy as np
import pandas as pd
from getting_matrices import getdata
from scipy.cluster.hierarchy import linkage, fcluster
from fuzzywuzzy import fuzz
import geopandas as gpd
import geoviews as gv
from shapely.geometry import Point
import holoviews as hv
import hvplot.pandas
from geoviews.tile_sources import EsriImagery

def get_long_lat(df1, df2, threshold=90):
    df2['latitude'] = None
    df2['longitude'] = None
   
    for i, row in df2.iterrows():
        for j, line in df1.iterrows():
            if fuzz.partial_ratio(row['language'], line['glottolog_name']) >= threshold:
                df2.at[i, 'latitude'] = line['latitude']
                df2.at[i, 'longitude'] = line['longitude']
                break 
    return df2

def getclusters():
    "returns a dataframe of clusters according to linguistic distance"
    coordinates, geographical_distance, linguistic_distance = getdata()
    condensed_distance_matrix_lg = linguistic_distance.to_numpy()[np.triu_indices(len(linguistic_distance), 1)]
    Z = linkage(condensed_distance_matrix_lg, method='ward')
    linkage_df = pd.DataFrame(Z, columns=['cluster1', 'cluster2', 'distance', 'sample_count'])
    max_d = 1 

    clusters = fcluster(Z, max_d, criterion='distance')
    df_with_clusters = pd.DataFrame(index=linguistic_distance.index)
    df_with_clusters['cluster'] = clusters

    df_only_clusters = pd.DataFrame(df_with_clusters['cluster'])
    df_only_clusters.index.name = 'language'
    df_only_clusters.reset_index(inplace=True)

    lang_cluster_with_cord = get_long_lat(coordinates, df_only_clusters)

    return lang_cluster_with_cord

def geoplot1(lang_cluster_with_cord, output_file="geoplot1.html"):
    "returns an interactive map of language clusters on a geographical map"
    hv.extension('bokeh')

    lang_cluster_with_cord['latitude'] = pd.to_numeric(lang_cluster_with_cord['latitude'])
    lang_cluster_with_cord['longitude'] = pd.to_numeric(lang_cluster_with_cord['longitude'])

    gdf = gpd.GeoDataFrame(
        lang_cluster_with_cord,
        geometry=gpd.points_from_xy(lang_cluster_with_cord.longitude, lang_cluster_with_cord.latitude),
        crs="EPSG:4326"
    )

    plot = gdf.hvplot(c='cluster', geo=True, hover_cols=['language'], size=15, cmap='viridis')
    plot.opts(width=700, height=500, tools=['hover'], title='Geographical Plot')

    hv.save(plot, output_file)

def geoplot2(lang_cluster_with_cord, output_file="geoplot2.html"):
     "returns an interactive map of language clusters on a physical interactive geographical map"
    gv.extension('bokeh')

    df = lang_cluster_with_cord
    df['latitude'] = pd.to_numeric(df['latitude'])
    df['longitude'] = pd.to_numeric(df['longitude'])

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    points_plot = gdf.hvplot.points(
        'longitude', 'latitude',
        c='cluster', geo=True, hover_cols=['language'], size=50, cmap='viridis'
    )

    tiles = EsriImagery()
    map_with_points = tiles * points_plot
    map_with_points.opts(title='Linguistic distance with Physical Geography', tools=['hover'])
    hv.save(map_with_points, output_file)

def get_geoplots():
    lang_cluster_with_cord = getclusters()
    geoplot1(lang_cluster_with_cord)
    geoplot2(lang_cluster_with_cord)

if __name__ == "__main__":
    get_geoplots()

