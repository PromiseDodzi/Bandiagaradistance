import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
import geopandas as gpd
import hvplot.pandas
import geoviews as gv
from geoviews.tile_sources import EsriImagery
from bokeh.resources import INLINE
from shapely.geometry import Point
import holoviews as hv
from holoviews import opts
from scipy.stats import kendalltau, spearmanr
from datasets import GetDatasets
from get_statistics import GetStatistics

datasets=GetDatasets()
stats=GetStatistics()
linguistic_distance_matrix=datasets.linguistic_distance_matrix
geographic_distance_matrix_euclidean=datasets.geographic_distance_matrix_euclidean
geographic_distance_matrix=datasets.geographic_distance_matrix
lang_cluster_with_cord=datasets.ling_distance_with_cluster 
sorted_ling=datasets.sorted_ling
sorted_geog=datasets.sorted_geog


class Getillustrations:

    def __init__(self, linguistic_distance_matrix=linguistic_distance_matrix, 
                 geographic_distance_matrix=geographic_distance_matrix, 
                 geographic_distance_matrix_euclidean=geographic_distance_matrix_euclidean, 
                 lang_cluster_with_cord=lang_cluster_with_cord,
                 sorted_ling=sorted_ling, sorted_geog=sorted_geog,
                cof=stats.get_coefficients_chi2_stat_pvalue_hosmer_lemeshow()):
        
        self.linguistic_distance_matrix=linguistic_distance_matrix
        self.geographic_distance_matrix=geographic_distance_matrix
        self.geographic_distance_matrix_euclidean=geographic_distance_matrix_euclidean
        self.lang_cluster_with_cord=lang_cluster_with_cord
        self.sorted_ling=sorted_ling
        self.sorted_geog=sorted_geog
        self.get_coefficients_chi2_stat_pvalue_hosmer_lemeshow=cof

    def get_heatmaps(self):
        "returns heatmaps of the different matrices under study"
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        sns.heatmap(self.linguistic_distance_matrix, ax=axes[0], cmap="coolwarm")
        axes[0].set_title('Linguistic distance matrix')
        sns.heatmap(self.geographic_distance_matrix, ax=axes[1], cmap="coolwarm")
        axes[1].set_title('Geographic distance matrix')
        plt.tight_layout()
        plt.savefig("illustrations/heatmaps_of_matrices")

    def plot_kde(self):
        """returns kde plots of the linguistic and geographic distance matrices"""
        upper_triangle_values1 = self.linguistic_distance_matrix.values[np.triu_indices_from(self.linguistic_distance_matrix.values, k=1)]
        upper_triangle_values2 = self.geographic_distance_matrix.values[np.triu_indices_from(self.geographic_distance_matrix.values, k=1)]
        
        fig, axs = plt.subplots(1, 2, figsize=(14, 6))
        
        sns.kdeplot(upper_triangle_values1, fill=True, ax=axs[0], color='blue')
        axs[0].set_title('KDE for Linguistic distance matrix')
        axs[0].set_xlabel('Distance')
        axs[0].set_ylabel('Density')
        
        sns.kdeplot(upper_triangle_values2, fill=True, ax=axs[1], color='red')
        axs[1].set_title('KDE for Geographic distance matrix')
        axs[1].set_xlabel('Distance')
        axs[1].set_ylabel('Density')
        
        plt.tight_layout()
    
        plt.savefig("illustrations/kde_distributions")
        plt.show()

    
    def principal_coordinates_plot(self):
        "returns a 2-d representation of the data in both linguistic and geographic matrices"
        distance_matrix_linguistic = self.linguistic_distance_matrix.values
        n = distance_matrix_linguistic.shape[0]
        H = np.eye(n) - np.ones((n, n)) / n
        B_linguistic = -0.5 * H @ (distance_matrix_linguistic ** 2) @ H
        eigenvalues_linguistic, eigenvectors_linguistic = np.linalg.eigh(B_linguistic)
        indices_linguistic = np.argsort(eigenvalues_linguistic)[::-1]
        eigenvalues_linguistic = eigenvalues_linguistic[indices_linguistic]
        eigenvectors_linguistic = eigenvectors_linguistic[:, indices_linguistic]
        top_eigenvalues_linguistic = eigenvalues_linguistic[:2]
        top_eigenvectors_linguistic = eigenvectors_linguistic[:, :2]
        coordinates_linguistic = top_eigenvectors_linguistic * np.sqrt(top_eigenvalues_linguistic)
        
        distance_matrix_geographic = self.geographic_distance_matrix.values
        B_geographic = -0.5 * H @ (distance_matrix_geographic ** 2) @ H
        eigenvalues_geographic, eigenvectors_geographic = np.linalg.eigh(B_geographic)
        indices_geographic = np.argsort(eigenvalues_geographic)[::-1]
        eigenvalues_geographic = eigenvalues_geographic[indices_geographic]
        eigenvectors_geographic = eigenvectors_geographic[:, indices_geographic]
        top_eigenvalues_geographic = eigenvalues_geographic[:2]
        top_eigenvectors_geographic = eigenvectors_geographic[:, :2]
        coordinates_geographic = top_eigenvectors_geographic * np.sqrt(top_eigenvalues_geographic)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        axes[0].scatter(coordinates_linguistic[:, 0], coordinates_linguistic[:, 1], s=100)
        for i, label in enumerate(self.linguistic_distance_matrix.index):
            axes[0].text(coordinates_linguistic[i, 0], coordinates_linguistic[i, 1], label, fontsize=12)
        axes[0].set_xlabel('PCoA Dimension 1')
        axes[0].set_ylabel('PCoA Dimension 2')
        axes[0].set_title('Principal Coordinates Analysis of linguistic distance')
        axes[0].grid(True)
        
        axes[1].scatter(coordinates_geographic[:, 0], coordinates_geographic[:, 1], s=100)
        for i, label in enumerate(self.geographic_distance_matrix.index):
            axes[1].text(coordinates_geographic[i, 0], coordinates_geographic[i, 1], label, fontsize=12)
        axes[1].set_xlabel('PCoA Dimension 1')
        axes[1].set_ylabel('PCoA Dimension 2')
        axes[1].set_title('Principal Coordinates Analysis of geographic distance')
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig("illustrations/pcoa.png")   


    def extract_upper_triangle(self, df):
        return df.where(np.triu(np.ones(df.shape, dtype=np.bool_), k=1))

    def plot_bivariate(self):
        """returns a scatterplot of the bivariate relationship between linguistic and geographic distance matrices"""
        ling=self.linguistic_distance_matrix.values
        geog=self.geographic_distance_matrix.values
        ling_distances =  ling[np.triu_indices_from(ling, k=1)]
        geog_distances = geog[np.triu_indices_from(geog, k=1)]
        plt.figure(figsize=(8, 6))
        plt.scatter(geog_distances, ling_distances, label='Data points')
        plt.xlabel('Geographic Distance')
        plt.ylabel('Linguistic Distance')
        plt.title('Relationship between geographic and linguistic distance')
        plt.legend()
        plt.grid(True)
        plt.savefig("illustrations/ling_and_direct.png")

    def threshold_corr_plot(self):
        "returns a 3-d plot of different thresholds and correlations"
        distance_matrix1 = self.linguistic_distance_matrix
        distance_matrix2 = self.geographic_distance_matrix
        ling_distances = distance_matrix1.values[np.triu_indices(len(distance_matrix1), 1)]
        geo_distances = distance_matrix2.values[np.triu_indices(len(distance_matrix2), 1)]
        
        results = []
        for geo_threshold in np.arange(0, 1, 0.1):
            for ling_threshold in np.arange(0, 1, 0.1):
                mask = (geo_distances > geo_threshold) & (ling_distances > ling_threshold)
                filtered_geo_distances = geo_distances[mask]
                filtered_ling_distances = ling_distances[mask]
                if len(filtered_geo_distances) > 1:
                    correlation_coefficient = np.corrcoef(filtered_ling_distances, filtered_geo_distances)[0, 1]
                    results.append((correlation_coefficient, geo_threshold, ling_threshold))
        results.sort(reverse=True, key=lambda x: x[0])
        
        correlations = [item[0] for item in results]
        geo_thresholds = [item[1] for item in results]
        ling_thresholds = [item[2] for item in results]
        fig = plt.figure(figsize=(10,7))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(geo_thresholds, ling_thresholds, correlations, c=correlations, cmap='viridis')
        colorbar = fig.colorbar(scatter, ax=ax, label='Correlation Coefficient')
        ax.set_xlabel('Geo Threshold')
        ax.set_ylabel('Ling Threshold')
        ax.set_zlabel('Correlation Coefficient')
        ax.set_title('Correlation coefficient vs threshold combinations')
        plt.savefig("illustrations/thresholds_and_correlations.png")

    def plot_dendrograms(self, labels1=None, labels2=None):
        "Plots two dendrograms side by side based on three distance matrices."
        distance_matrix1=self.linguistic_distance_matrix
        distance_matrix2=self.geographic_distance_matrix
        condensed_distance_matrix1 = distance_matrix1.values[np.triu_indices(len(distance_matrix1), 1)]
        condensed_distance_matrix2 = distance_matrix2.values[np.triu_indices(len(distance_matrix2), 1)]
        Z1 = linkage(condensed_distance_matrix1, method='ward')
        Z2 = linkage(condensed_distance_matrix2, method='ward')
        
        plt.figure(figsize=(30, 10))
        plt.subplot(1, 2, 1)
        dendrogram(Z1, labels=labels1 if labels1 is not None else distance_matrix1.index)
        plt.title('Hierarchical Clustering of linguistic distance matrix')
        plt.xlabel('Languages')
        plt.ylabel('Distance')
        plt.xticks(rotation='vertical')
        plt.subplot(1, 2, 2)
        dendrogram(Z2, labels=labels2 if labels2 is not None else distance_matrix2.index)
        plt.title('Hierarchical Clustering of geographic linguistic distance matrix')
        plt.xlabel('Languages')
        plt.ylabel('Distance')
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        plt.savefig("illustrations/clustering_matrixes.png")  

    
    def plot_difference_heatmap(self):
        """
        Returns heatmap of absolute differences between linguistic and geographic distance matrices.
        """
        ling = self.linguistic_distance_matrix
        geog = self.geographic_distance_matrix

        diff = np.abs(ling - geog)

        plt.figure(figsize=(14, 10))

        ax = sns.heatmap(diff,annot=True,fmt=".2f",cmap="coolwarm")

        plt.title('Absolute differences between linguistic and geographic distance matrices',fontsize=14)

        # Rotate and align language labels
        plt.xticks(rotation=45,ha="right",fontsize=9)
        plt.yticks(rotation=0,fontsize=9)

        # Give labels more room before saving
        plt.tight_layout()

        plt.savefig("illustrations/heatmaps_of_absolute_differences.png",dpi=300,bbox_inches="tight")


    def ling_cluster_on_geog(self):
        "returns linguistic clusters on geographical map"
        gv.extension('bokeh')  
        df = self.lang_cluster_with_cord
        gdf = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.longitude, df.latitude),crs="EPSG:4326")
        points_plot = gdf.hvplot.points('longitude', 'latitude',
                                        c='cluster', geo=True, hover_cols=['language'], size=50, cmap='viridis')
        tiles = EsriImagery()
        map_with_points = tiles * points_plot
        hvplot.save(map_with_points, 'map_with_points.html', resources=INLINE)
        map_with_points.opts(title='Linguistic distance with Physical Geography', tools=['hover'])

    
    def geo_plot_with_labels(self):
        "returns linguistic clusters on geographical map with physical geography"
        hv.extension('bokeh')
        self.lang_cluster_with_cord['latitude'] = pd.to_numeric(self.lang_cluster_with_cord['latitude'])
        self.lang_cluster_with_cord['longitude'] = pd.to_numeric(self.lang_cluster_with_cord['longitude'])
        
        gdf = gpd.GeoDataFrame(
            self.lang_cluster_with_cord,
            geometry=gpd.points_from_xy(self.lang_cluster_with_cord.longitude, self.lang_cluster_with_cord.latitude),
            crs="EPSG:4326")
        
        points = gv.Points(gdf, ['longitude', 'latitude'], ['cluster']).opts(
            size=10, color='cluster', cmap='viridis', tools=['hover'])
        text = gv.Labels(gdf, ['longitude', 'latitude'], 'language').opts(
            text_color='black', text_align='center', text_baseline='middle', text_font_size='8pt')
        
        plot = points * text
        plot.opts(
            width=700, height=500, title='Linguistic cluster plot',
            active_tools=['pan', 'wheel_zoom'])
        hv.save(plot, 'illustrations/geographical_plot_with_labels.html')
        plot  

    def plot_cluster_with_physical_geography(self):
        """
        Plot linguistic clusters using geographic distances reduced into 2D PCA space.
        Each point represents a language positioned by its geographic similarity.
        """

        # Geographic distance matrix
        distance_matrix = self.geographic_distance_matrix.values
        n = distance_matrix.shape[0]

        # Classical MDS / PCoA reduction 
        H = np.eye(n) - np.ones((n, n)) / n
        B = -0.5 * H @ (distance_matrix ** 2) @ H

        eigenvalues, eigenvectors = np.linalg.eigh(B)

        # Sort eigenvalues descending
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]

        # Keep first two dimensions
        positive = eigenvalues[:2]
        vectors = eigenvectors[:, :2]

        coordinates = vectors * np.sqrt(positive)

        # Build dataframe
        df = self.lang_cluster_with_cord.copy()

        # Match coordinate order to language order
        language_order = list(self.geographic_distance_matrix.index)

        coord_df = pd.DataFrame(coordinates,columns=["PC1", "PC2"],index=language_order)

        df = df.set_index("language")
        df = df.join(coord_df)
        df = df.reset_index()

        # Plot
        plt.figure(figsize=(10, 8))

        scatter = plt.scatter(df["PC1"],df["PC2"],c=df["cluster"],cmap="viridis",s=120,edgecolors="black")

        # Language labels
        for _, row in df.iterrows():
            plt.text(row["PC1"],row["PC2"],row["language"],fontsize=8,ha="center",va="bottom")

        plt.xlabel("Geographic PCA Dimension 1")
        plt.ylabel("Geographic PCA Dimension 2")
        plt.title("Linguistic Clusters Projected onto Geographic PCA Space")

        plt.grid(True, alpha=0.3)
        plt.colorbar(scatter, label="Linguistic Cluster")

        plt.tight_layout()
        plt.savefig("illustrations/cluster_geographic_pca.png",dpi=300)
        plt.show()
        
    def plot_tau_tui(self):
        "returns a bivariate distribution of Kendall's Tau scores and TUI scores"
        direct_cluster_1_langs = self.sorted_ling[self.sorted_ling["Cluster"]==1]["Language"].values
        direct_cluster_2_langs = self.sorted_ling[self.sorted_ling["Cluster"]==2]["Language"].values
        direct_cluster_3_langs = self.sorted_ling[self.sorted_ling["Cluster"]==3]["Language"].values
        direct_cluster_4_langs = self.sorted_ling[self.sorted_ling["Cluster"]==4]["Language"].values

        geog_cluster_1_langs = [x for x in self.sorted_geog["Language"].values if x in direct_cluster_1_langs]
        geog_cluster_2_langs = [x for x in self.sorted_geog["Language"].values if x in direct_cluster_2_langs]
        geog_cluster_3_langs = [x for x in self.sorted_geog["Language"].values if x in direct_cluster_3_langs]
        geog_cluster_4_langs = [x for x in self.sorted_geog["Language"].values if x in direct_cluster_4_langs]

        ling = [direct_cluster_1_langs, direct_cluster_2_langs, direct_cluster_3_langs, direct_cluster_4_langs]
        geog = [geog_cluster_1_langs, geog_cluster_2_langs, geog_cluster_3_langs, geog_cluster_4_langs]

        # full ordering of languages in each overall sorted list, used to derive numeric ranks
        ling_order = list(self.sorted_ling["Language"].values)
        geog_order = list(self.sorted_geog["Language"].values)

        tau_list = []
        for cluster, (li, ge) in enumerate(zip(ling, geog), start=1):
            li = list(li)
            ge = list(ge)
            common = [lang for lang in li if lang in ge]

            print(f"Cluster {cluster}: len(li)={len(li)}, len(ge)={len(ge)}, common={len(common)}")

            tau = np.nan
            if len(common) < 2:
                print(f"  -> skipping cluster {cluster}: fewer than 2 shared languages")
            else:
                # convert language names to their numeric rank position in each ordering
                li_ranks = [ling_order.index(lang) for lang in common]
                ge_ranks = [geog_order.index(lang) for lang in common]
                try:
                    tau, _ = kendalltau(li_ranks, ge_ranks)
                except Exception as e:
                    print(f"  -> kendalltau failed for cluster {cluster}: {e}")

            tau_list.append(tau)

        tui = [max(3,0)/3, max(2, 1)/3, max(4, 1)/5, max(1, 5)/6]
        tui_tau = pd.DataFrame({"tui": tui, "tau": tau_list})
        tui_tau_clean = tui_tau.dropna(subset=["tau"])

        if tui_tau_clean.empty:
            print("No valid tau values to plot — check the cluster diagnostics printed above.")
            return

        sns.scatterplot(data=tui_tau_clean, x="tui", y="tau", hue=tui_tau_clean.index+1, palette="viridis")
        plt.xlabel("Tau")
        plt.ylabel("TUI")
        plt.title("Kendall's Tau correlation and Topographical Uniformity Index")
        plt.savefig("illustrations/tau_vs_tui.png")

    def chi2_and_p_values_draw(self,ax, chi2_stats, p_values, title):
        "general plot for chi2 and p-values"
        classes = range(len(chi2_stats))
        color = 'tab:blue'
        ax.bar(classes, chi2_stats, color=color, alpha=0.7, label='Chi-squared Statistic')
        ax.set_xticks(classes)
        ax.set_xticklabels([f'Class {i}' for i in classes])
        ax.set_xlabel('Class')
        ax.set_ylabel('Chi-squared Statistic', color=color)
        ax.tick_params(axis='y', labelcolor=color)
        ax2 = ax.twinx()
        color = 'tab:red'
        ax2.plot(classes, p_values, color=color, marker='o', linestyle='--', label='p-value')
        ax2.set_ylabel('p-value', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax.set_title(title)

    
    def plot_chi2_and_pvalues(self):
        "returns a plot of chi2 statistic and p-values after Hosmer-Lemmeshow test"
        _,chi_pvalue_tuple=stats.get_coefficients_chi2_stat_pvalue_hosmer_lemeshow()
        num_rows = 3
        num_cols = 2
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(15, 18))
        self.chi2_and_p_values_draw(axs[0, 0], chi_pvalue_tuple[0][0], chi_pvalue_tuple[0][1], title="linguistic distances")
        self.chi2_and_p_values_draw(axs[0, 1], chi_pvalue_tuple[2][0], chi_pvalue_tuple[2][1], title="TUI score")
        self.chi2_and_p_values_draw(axs[1, 0], chi_pvalue_tuple[1][0], chi_pvalue_tuple[1][1], title="geographic distance")
        self.chi2_and_p_values_draw(axs[1, 1], chi_pvalue_tuple[4][0], chi_pvalue_tuple[4][1], title="geographic distance,TUI")
        self.chi2_and_p_values_draw(axs[2, 0], chi_pvalue_tuple[3][0], chi_pvalue_tuple[3][1], title="linguistic distance, geographic distance")
        self.chi2_and_p_values_draw(axs[2, 1], chi_pvalue_tuple[5][0], chi_pvalue_tuple[5][1], title="linguistic dist,geographic distance, TUI")
        fig.suptitle("Hosmer-Lemeshow Test for Each Class")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig("illustrations/Hosmer-Lemeshow_test_results")
        plt.show()

def get_plots():
    ill=Getillustrations()
    ill.plot_kde()
    ill.plot_tau_tui()
    ill.get_heatmaps()
    ill.principal_coordinates_plot()
    ill.plot_bivariate()
    ill.geo_plot_with_labels()
    ill.threshold_corr_plot()
    ill.plot_dendrograms()
    ill.plot_difference_heatmap()
    # ill.ling_cluster_on_geog()
    ill.plot_cluster_with_physical_geography()
    ill.plot_chi2_and_pvalues()
    print("All graphs outputed to illustrations folder")
if __name__== "__main__":
    get_plots()