
import numpy as np
import pandas as pd
import math
from scipy.cluster.hierarchy import linkage, fcluster
from fuzzywuzzy import fuzz


class GetDatasets:

    def __init__(self, geodata="matrices/Geodata.csv",linguistic_distance="matrices/linguistic_distance_matrix.csv" ):
        self.coordinates = pd.read_csv(geodata)
        self.filtered_coordinates = self.filter_coordinates()
        self.ling_distance_matrix = pd.read_csv(linguistic_distance, index_col="Unnamed: 0")
        self.geographic_distance_matrix_haversine=self.get_geog_haversine()
        self.geographic_distance_matrix_euclidean = self.calculate_euclidean_distance() 
        self.geographic_distance_matrix = self.get_normalized_geographic()
        self.linguistic_distance_matrix = self.get_linguistic_distance()       
        self.df_only_clusters=self.get_ling_with_cluster()
        self.ling_distance_with_cluster=self.get_lang_cluster_with_cord()
        self.sorted_ling, self.sorted_geog=self.sort_clusters()
        self.individual_language_tuis=self.lang_cluster_tui_individual()
        self.data_for_regression=self.data_for_regression()

    def dropdog(self, name):
        "cleans the data by eliminating the name 'Dogon' from language names"
        if "Dogon" in name:
            name = name.replace("Dogon", "").strip().replace(" ", "")
            if name == "TiranigeDiga":
                name = "Tiranige"
        return name.replace(" ", "")

    def filter_coordinates(self):
        "prepares coordinates data for further use"
        coordinates=self.coordinates[self.coordinates["family"]=="Dogon"]
        coordinates=coordinates[["latitude", "longitude", "glottolog_name"]]
        coordinates.head()
        coordinates["glottolog_name"] = coordinates["glottolog_name"].apply(self.dropdog)
        to_keep=set(coordinates['glottolog_name'].unique())-set(['Nanga','Guru (Mali)', 'Ibi So', 'Ampari'])
        filtered_coordinates = coordinates[coordinates['glottolog_name'].isin(to_keep)]
        filtered_coordinates=filtered_coordinates.drop([169,172, 173,174,178,183])
        return filtered_coordinates

    def haversine(self, lat1, lon1, lat2, lon2):
        "calculates haversine scores"
        R = 6371 
        phi1, phi2 = np.radians(lat1), np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        
        a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        return R * c

    def get_geog_haversine(self):
        "returns geographic matrix distance calculated according to haversine formula"
        languages = self.filtered_coordinates['glottolog_name'].tolist()
        num_languages = len(languages)
        distance_matrix = np.zeros((num_languages, num_languages))
        
        for i in range(num_languages):
            lat1, lon1 = self.filtered_coordinates.iloc[i]['latitude'], self.filtered_coordinates.iloc[i]['longitude']
            for j in range(i + 1, num_languages):
                lat2, lon2 = self.filtered_coordinates.iloc[j]['latitude'], self.filtered_coordinates.iloc[j]['longitude']
                distance = self.haversine(lat1, lon1, lat2, lon2)
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance  
        
        geographic_distance_matrix_haversine = pd.DataFrame(distance_matrix, index=languages, columns=languages)
        return geographic_distance_matrix_haversine

    
    def lat_lon_to_cartesian(self, lat, lon):
        "convert radius to radians"
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        R = 6371.0
        x = R * math.cos(lat_rad) * math.cos(lon_rad)
        y = R * math.cos(lat_rad) * math.sin(lon_rad)
        z = R * math.sin(lat_rad)
        
        return x, y, z

    def normalize_matrix(self, matrix):
        "normalizes  distance matrix"
        values = matrix.values
        min_val = np.min(values[values > 0])
        max_val = np.max(values[values > 0])
        normalized_values = np.where(values == 0, 0, (values - min_val) / (max_val - min_val))
        return pd.DataFrame(normalized_values, index=matrix.index, columns=matrix.columns)

    def calculate_euclidean_distance(self):
        "calculates euclidean distances between geographical cordinates after converting radius to radians"
        languages = self.filtered_coordinates['glottolog_name'].tolist()
        num_languages = len(languages)
        distance_matrix = np.zeros((num_languages, num_languages))

        for i in range(num_languages):
            lat1, lon1 = self.filtered_coordinates.iloc[i]['latitude'], self.filtered_coordinates.iloc[i]['longitude']
            x1, y1, z1 = self.lat_lon_to_cartesian(lat1, lon1) 
            for j in range(i + 1, num_languages):
                lat2, lon2 = self.filtered_coordinates.iloc[j]['latitude'], self.filtered_coordinates.iloc[j]['longitude']
                x2, y2, z2 = self.lat_lon_to_cartesian(lat2, lon2)  
                distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
                distance_matrix[i, j] = distance
                distance_matrix[j, i] = distance  

        matrix = pd.DataFrame(distance_matrix, index=languages, columns=languages)
        return matrix

    def get_normalized_geographic(self):
        return self.normalize_matrix(self.geographic_distance_matrix_euclidean)

    def get_linguistic_distance(self):
        "returns a cleaned linguistic distance matrix"
        linguistic_distance_matrix=self.ling_distance_matrix
        rename_dict_ling={"TommoSoTongoTongo": "TommoSo",  "Najamba": "Najamba-Kindige", "JamsayDouentza": "Jamsay", "DogulDomBendiely":"DogulDom"}
        linguistic_distance_matrix=linguistic_distance_matrix.rename(columns=rename_dict_ling)
        linguistic_distance_matrix=linguistic_distance_matrix.rename(index=rename_dict_ling)
        geog_list=self.geographic_distance_matrix.columns
        ling_list=linguistic_distance_matrix.columns
        unshared=[x for x in ling_list if x not in geog_list]
        linguistic_distance_matrix = linguistic_distance_matrix.drop(unshared, axis=0).drop(unshared, axis=1)
        linguistic_distance_matrix=linguistic_distance_matrix.reindex(index=self.geographic_distance_matrix.index)
        linguistic_distance_matrix=linguistic_distance_matrix.reindex(columns=self.geographic_distance_matrix.columns)
        return linguistic_distance_matrix

    def get_ling_with_cluster(self):
        "returns languages and their clusters"
        condensed_linguistic_distance_matrix = self.linguistic_distance_matrix.values[
            np.triu_indices(len(self.linguistic_distance_matrix), 1)]
        Z = linkage(condensed_linguistic_distance_matrix, method='ward')
        num_clusters = 4
        clusters = fcluster(Z, num_clusters, criterion='maxclust')
        df_with_clusters = self.linguistic_distance_matrix.copy()
        df_with_clusters['cluster'] = clusters
        df_only_clusters = pd.DataFrame(df_with_clusters['cluster'])
        df_only_clusters.index.name = 'language'
        df_only_clusters.reset_index(inplace=True)
        return df_only_clusters

    def get_long_lat(self, df1, df2, threshold=70):
        "retrieves cordinate information"
        df2['latitude'] = None
        df2['longitude'] = None
    
        for i, row in df2.iterrows():
            for j, line in df1.iterrows():
                if fuzz.partial_ratio(row['language'], line['glottolog_name']) >= threshold:
                    df2.at[i, 'latitude'] = line['latitude']
                    df2.at[i, 'longitude'] = line['longitude']
                    break 
        return df2

    def get_lang_cluster_with_cord(self):
        return  self.get_long_lat(self.filtered_coordinates, self.df_only_clusters)

    def sort_clusters(self):
        "returns a sorted list of languages according to their order in clusters"
        mtx_1=self.linguistic_distance_matrix
        condensed_distance_matrix = mtx_1.values[np.triu_indices(len(mtx_1), 1)]
        linkage_matrix = linkage(condensed_distance_matrix, method='ward')
        
        cluster_labels = fcluster(linkage_matrix, t=4, criterion='maxclust')
        languages_order = pd.DataFrame({
            'Language': mtx_1.index,
            'Cluster': cluster_labels
        }).sort_values(by='Cluster')
        
        sorted_ling = languages_order.sort_values(by=['Cluster', 'Language'])
        
        mtx_2=self.geographic_distance_matrix
        condensed_distance_matrix_2= mtx_2.values[np.triu_indices(len(mtx_2), 1)]
        linkage_matrix_2 = linkage(condensed_distance_matrix_2, method='ward')
        
        cluster_labels = fcluster(linkage_matrix_2, t=4, criterion='maxclust')
        languages_order = pd.DataFrame({
            'Language': mtx_2.index,
            'Cluster': cluster_labels
        }).sort_values(by='Cluster')
        
        sorted_geog= languages_order.sort_values(by=['Cluster', 'Language'])
        return sorted_ling, sorted_geog


    def lang_cluster_tui_individual(self):
        """returns a dataframe with languages, clusters, cluster tui, and individual language tui"""
        lang_topo = [
            ("Penange", "E", 1, 1.0),
            ("Bunoge", "E", 1, 1.0),
            ("Mombo", "E", 1, 1.0),
            ("Tiranige", "E", 2, 0.67),
            ("DogulDom", "E", 2, 0.67),
            ("Najamba-Kindige", "B", 2, 0.67),
            ("TommoSo", "E", 3, 0.8),
            ("YornoSo", "B", 3, 0.8),
            ("DonnoSo", "B", 3, 0.8),
            ("YandaDom", "B", 3, 0.8),
            ("TebulUre", "B", 3, 0.8),
            ("PergeTegu", "E", 4, 0.83),
            ("BenTey", "B", 4, 0.83),
            ("Jamsay", "B", 4, 0.83),
            ("BankanTey", "B", 4, 0.83),
            ("ToroTegu", "B", 4, 0.83),
            ("TogoKan", "B", 4, 0.83)
        ]
        df = pd.DataFrame(lang_topo, columns=['Language', 'Topography', 'Cluster', 'cluster_tui'])
    
        def calculate_language_scores(df):
            counts = df.groupby(['Cluster', 'Topography']).size().unstack(fill_value=0)
            counts['Total'] = counts.sum(axis=1)
            df = df.merge(counts, left_on='Cluster', right_index=True, suffixes=('', '_count'))
            df['language_tui'] = df.apply(lambda row: (row['cluster_tui'] * row[row['Topography']]) / row['Total'], axis=1)
            return df
        
        df = calculate_language_scores(df)
        
        return df

    def data_for_regression(self):
        "returns dataframe with independent and dependent variables for regression analysis"
        df=self.individual_language_tuis
        df["cluster"]=df["Cluster"].apply(lambda x: x-1)
        
        ling_list=[]
        geog_list=[]
        for language1 in df["Language"]:
            for language2 in self.linguistic_distance_matrix.index: 
                if language1== language2:
                    ling_list.append(self.linguistic_distance_matrix.sum().loc[language1])
                    geog_list.append(self.geographic_distance_matrix.sum().loc[language1])
        
        df["ling_dist"]=ling_list
        df["geog_dist"]=geog_list
        df_1=df[["Language", "ling_dist","geog_dist", "language_tui", "cluster"]]
        return df_1
    
if __name__=="__main__":
    dat=GetDatasets()
    # print(dat.lang_cluster_tui_individual())
    # print((0.4/3)+(0.4/3)+(0.2/3))