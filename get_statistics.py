import numpy as np
import pandas as pd
from sklearn.manifold import MDS
from sklearn.metrics import euclidean_distances
from scipy.stats import ttest_rel, pearsonr, kendalltau, spearmanr
from scipy.stats import skew, kurtosis
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from scipy.stats import chi2_contingency
from datasets import GetDatasets

datasets=GetDatasets()
linguistic_distance_matrix=datasets.linguistic_distance_matrix
geographic_distance_matrix=datasets.geographic_distance_matrix
geographic_distance_matrix_haversine=datasets.geographic_distance_matrix_haversine
geographic_distance_matrix_euclidean=datasets.geographic_distance_matrix_euclidean
geographic_distance_matrix=datasets.geographic_distance_matrix
sorted_ling=datasets.sorted_ling
sorted_geog=datasets.sorted_geog
data_for_regression=datasets.data_for_regression
cluster_tui=datasets.lang_cluster_tui_individual


class GetStatistics:

    def __init__(self, geographic_distance_matrix=geographic_distance_matrix,
                geographic_distance_matrix_haversine=geographic_distance_matrix_haversine,
                 geographic_distance_matrix_euclidean=geographic_distance_matrix_euclidean,
                 linguistic_distance_matrix=linguistic_distance_matrix,
                sorted_ling=sorted_ling, sorted_geog=sorted_geog, 
                 data_for_regression=data_for_regression, cluster_tui=cluster_tui):
        
        self.geographic_distance_matrix = geographic_distance_matrix
        self.geographic_distance_matrix_haversine = geographic_distance_matrix_haversine
        self.geographic_distance_matrix_euclidean=geographic_distance_matrix_euclidean
        self.linguistic_distance_matrix=linguistic_distance_matrix
        self.sorted_ling=sorted_ling
        self.sorted_geog=sorted_geog
        self.data_for_regression=data_for_regression
        self.cluster_tui=cluster_tui

    def get_basic_descriptive_stats(self):
        "returns descriptive statistics of both linguistic and geographic distances"
        print("Descriptive statistics of linguistic distance matrix\n")
        print(self.linguistic_distance_matrix.describe())
        print(f"{'*'*20}")
        print("Descriptive statistics of geographic distance matrix\n")
        print(self.geographic_distance_matrix.describe())
        #skew and kurtosis
        ling_distance_matrix = self.linguistic_distance_matrix  
        ling_upper_triangle_values = ling_distance_matrix.values[np.triu_indices_from(ling_distance_matrix, k=1)]
        ling_skewness = skew(ling_upper_triangle_values)
        ling_kurtosis_value = kurtosis(ling_upper_triangle_values)
        geog_distance_matrix=self.geographic_distance_matrix
        geog_upper_triangle_values = geog_distance_matrix.values[np.triu_indices_from(geog_distance_matrix, k=1)]
        geog_skewness = skew(geog_upper_triangle_values)
        geog_kurtosis_value = kurtosis(geog_upper_triangle_values)
        
        print("\n")
        print("Skew and Kurtosis in distance matrices")
        print("*"*20)
        print(f" Linguistic matrix Skewness: {ling_skewness}, Kurtosis {ling_kurtosis_value}")
        print(f" Geographic matrix Skewness: {geog_skewness}, Kurtosis {geog_kurtosis_value}")
        print("*"*20)


    def compare_geographical_distances(self):
        "Prints the mean absolute error, root mean squared error, and Pearson correlation."
        mae = np.mean(np.abs(self.geographic_distance_matrix_haversine - self.geographic_distance_matrix_euclidean))
        rmse = np.sqrt(np.mean((self.geographic_distance_matrix_haversine - self.geographic_distance_matrix_euclidean) ** 2))
        correlation = np.corrcoef(self.geographic_distance_matrix_haversine.values.flatten(), 
                                  self.geographic_distance_matrix_euclidean.values.flatten())[0, 1]
        
        print("Comparing haversine geographic distance and Euclidean geographic distance")
        print(f"Mean Absolute Error: {mae}")
        print(f"Root Mean Squared Error: {rmse}")
        print(f"Pearson's Correlation: {correlation}")
        print(f"{'*'*20}\n{'*'*20}")

    def calculate_kruskalstress_global(self, matrix):
        "Calculates Kruskal's global stress for the entire distance matrix."
        matrix=np.array(matrix)
        
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=42)
        embedding = mds.fit_transform(matrix)
        
        lower_dim_distances = euclidean_distances(embedding)
        
        numerator = np.sum((matrix - lower_dim_distances) ** 2)
        denominator = np.sum(matrix ** 2)
        global_stress = np.sqrt(numerator / denominator)
        
        return global_stress

    def get_kruskal_global(self):
        "Prints the global Kruskal's stress values for linguistic and geographic distance matrices."
        linguistic_stress_global = self.calculate_kruskalstress_global(self.linguistic_distance_matrix)
        geographic_stress_global = self.calculate_kruskalstress_global(self.geographic_distance_matrix)
        
        print("Global Kruskal's stress values:")
        print(f"Global Kruskal's stress for linguistic distance matrix: {linguistic_stress_global}")
        print(f"Global Kruskal's stress for geographic distance matrix: {geographic_stress_global}")
        print(f"{'*'*20}\n{'*'*20}")

    def matrices_differences(self):
        "Returns statistics that illustrate differences between linguistic and geographic distance matrices."
        linguistic_matrix = self.linguistic_distance_matrix.values
        geographic_matrix = self.geographic_distance_matrix.values
        differences = np.abs(linguistic_matrix - geographic_matrix)

        average_difference = np.mean(differences)

        t_statistic, p_value = ttest_rel(linguistic_matrix.flatten(), geographic_matrix.flatten())
        
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)  
        cohen_d = mean_diff / std_diff

        print("Statistical tests to show differences between linguistic and geographic distance matrices")
        print(f"Average difference: {average_difference}")
        print(f"Paired t-test statistic: {t_statistic}")
        print(f"P-value: {p_value}")
        print(f"Cohen's d: {cohen_d}")
        print(f"{'*'*20}\n{'*'*20}")

    def mantel_test(self, dist_matrix1, dist_matrix2, n_permutations=999):
        "Performs Mantel's test and returns the correlation and p-value."
        triu_indices = np.triu_indices_from(dist_matrix1, k=1)
        dist1_flat = dist_matrix1[triu_indices]
        dist2_flat = dist_matrix2[triu_indices]
        
        obs_corr, _ = pearsonr(dist1_flat, dist2_flat)
        
        permuted_corrs = []
        for _ in range(n_permutations):
            permuted_dist2 = np.random.permutation(dist2_flat)
            perm_corr, _ = pearsonr(dist1_flat, permuted_dist2)
            permuted_corrs.append(perm_corr)
        
        p_value = np.mean(np.abs(permuted_corrs) >= np.abs(obs_corr))
        return obs_corr, p_value

    def matrices_correlations(self):
        "Returns and prints differences between correlations of linguistic and geographic distance matrices."
        linguistic_matrix = self.linguistic_distance_matrix.values
        geographic_matrix = self.geographic_distance_matrix.values
        correlation_coefficient = np.corrcoef(linguistic_matrix.flatten(), 
                                              geographic_matrix.flatten())[0, 1]

        corr, p_value = self.mantel_test(linguistic_matrix, geographic_matrix)
        print("Mantel's test showing differences between linguistic and geographic distance matrices")
        print(f'Correlation: {corr}, p-value: {p_value}')
        print(f"Pearson correlation coefficient between the two matrices: {correlation_coefficient}")

    def get_threshold_corr_scores(self):
        "returns threshold combinations and coefficients obtained"
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
        
        top_5_results = results[:20]
        print("Combinations of different thresholds and coefficients obtained")
        print("Top 20 threshold combinations:")
        for i, (corr, geo_thresh, ling_thresh) in enumerate(top_5_results, 1):
            print(f"{i}: Correlation: {corr:.4f}, Geo Threshold: {geo_thresh:.2f}, Ling Threshold: {ling_thresh:.2f}")
        print("*"*20)

    def get_tau(self):
        "Computes Kendall's tau correlation"
        direct_cluster_1_langs=self.sorted_ling[self.sorted_ling["Cluster"]==1]["Language"].values
        direct_cluster_2_langs=self.sorted_ling[self.sorted_ling["Cluster"]==2]["Language"].values
        direct_cluster_3_langs=self.sorted_ling[self.sorted_ling["Cluster"]==3]["Language"].values
        direct_cluster_4_langs=self.sorted_ling[self.sorted_ling["Cluster"]==4]["Language"].values
        
        geog_cluster_1_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_1_langs]
        geog_cluster_2_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_2_langs]
        geog_cluster_3_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_3_langs]
        geog_cluster_4_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_4_langs]
        
        ling=[direct_cluster_1_langs, direct_cluster_2_langs, direct_cluster_3_langs, direct_cluster_4_langs]
        geog=[geog_cluster_1_langs, geog_cluster_2_langs, geog_cluster_3_langs, geog_cluster_4_langs]
        
        tau_list=[]
        cluster=0
        print("\nKendall's Tau correlation between linguistic cluster internal order and geographic cluster internal order")
        for li, ge in zip(ling,geog):
            tau, _ = kendalltau(li, ge)
            cluster +=1 
            tau_list.append(tau)
            print(f"Cluster: {cluster}\nTau: {tau:.2f}")

    def get_tau_tui(self):
        "Computes Kendall's tau correlation and topological uniformity index."
        direct_cluster_1_langs=self.sorted_ling[self.sorted_ling["Cluster"]==1]["Language"].values
        direct_cluster_2_langs=self.sorted_ling[self.sorted_ling["Cluster"]==2]["Language"].values
        direct_cluster_3_langs=self.sorted_ling[self.sorted_ling["Cluster"]==3]["Language"].values
        direct_cluster_4_langs=self.sorted_ling[self.sorted_ling["Cluster"]==4]["Language"].values
        
        geog_cluster_1_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_1_langs]
        geog_cluster_2_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_2_langs]
        geog_cluster_3_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_3_langs]
        geog_cluster_4_langs=[x for x in self.sorted_geog["Language"].values if x in direct_cluster_4_langs]
        
        ling=[direct_cluster_1_langs, direct_cluster_2_langs, direct_cluster_3_langs, direct_cluster_4_langs]
        geog=[geog_cluster_1_langs, geog_cluster_2_langs, geog_cluster_3_langs, geog_cluster_4_langs]
        
        tau_list=[]
        cluster=0
        for li, ge in zip(ling,geog):
            tau, _ = kendalltau(li, ge)
            rho, _ = spearmanr(li, ge)
        
            cluster +=1 
            tau, rho
            tau_list.append(tau)
        
        #get group TUI
        tui_data=self.cluster_tui()
        tui_data["averaged_lang_tui"]=tui_data["language_tui"]/tui_data["Total"]
        group_tui=tui_data.groupby("Cluster").sum().reset_index()[["Cluster", "averaged_lang_tui"]]
        group_tui["group_tui"]=group_tui["averaged_lang_tui"]
        group_tui.drop("averaged_lang_tui", axis=1, inplace=True)
        print("Group TUI scores:")
        cluster=1
        for num in group_tui["group_tui"]:
            print(f"cluster={cluster}, TUI={num:.2f}")
            cluster +=1
        print("*"*20)

        tui=group_tui["group_tui"].values
        tui_tau = pd.DataFrame({"tui": tui, "tau": tau_list})

        print("Kendall's Tau correlation between linguistic clusters and geographic distance-induced clusters")
        print("Correlation between TUI and TAU")
        print(tui_tau.corr())

    def model_fit_and_coefficients(self, X, y):
        "fits a model and conducts a hosmer_lemmeshow test on model"
        model = make_pipeline(StandardScaler(), LogisticRegression(solver='lbfgs', max_iter=200))
        model.fit(X, y)
        
        pred_probs = model.predict_proba(X)
        
        num_groups = 10
        chi2_stats = []
        p_values = []
        
        def hosmer_lemeshow_test(y_true, y_probs, num_groups):
            "conducts a hosmer_lemmeshow test on model"
            df = pd.DataFrame({'true': y_true, 'prob': y_probs})
            df['group'] = pd.qcut(df['prob'], q=num_groups, labels=False, duplicates='drop')
            
            observed = df.groupby('group')['true'].agg(['sum', 'count'])
            expected = df.groupby('group')['prob'].mean() * observed['count']
            
            if (observed['count'] == 0).any():
                raise ValueError("One or more groups have zero counts. Adjust the number of groups.")
            
            contingency_table = np.array([
                [observed['sum'].values[i], observed['count'].values[i] - observed['sum'].values[i]]
                for i in range(len(observed))
            ])
            
            chi2_stat, p_value, _, _ = chi2_contingency(contingency_table, correction=False)
            
            return chi2_stat, p_value
        
        for i, class_probs in enumerate(pred_probs.T):
            y_binary = (y == i).astype(int)
            try:
                chi2_stat, p_value = hosmer_lemeshow_test(y_binary, class_probs, num_groups)
                chi2_stats.append(chi2_stat)
                p_values.append(p_value)
            except ValueError as e:
                print(f"Class {i} Error: {e}")
        coef = model.named_steps['logisticregression'].coef_
        intercept = model.named_steps['logisticregression'].intercept_
    
        return chi2_stats, p_values, coef, intercept

    def get_coefficients_chi2_stat_pvalue_hosmer_lemeshow(self):
        "returns cofficients, chi2 statistic and p_value of hosmer-lemmeshow test"
        
        df_1 = self.data_for_regression
        X_1 = df_1[['ling_dist']]
        y_1 = df_1['cluster']
        chi_1, p_values_1, coef_1, intercept_1 = self.model_fit_and_coefficients(X_1, y_1)
        
        X_2 = df_1[['geog_dist']]
        y_2 = df_1['cluster']
        chi_2, p_values_2, coef_2, intercept_2 = self.model_fit_and_coefficients(X_2, y_2)
        
        X_3 = df_1[['language_tui']]
        y_3 = df_1['cluster']
        chi_3, p_values_3, coef_3, intercept_3 = self.model_fit_and_coefficients(X_3, y_3)
        
        X_4 = df_1[['ling_dist', 'geog_dist']]
        y_4 = df_1['cluster']
        chi_4, p_values_4, coef_4, intercept_4 = self.model_fit_and_coefficients(X_4, y_4)
        
        X_5 = df_1[['geog_dist', 'language_tui']]
        y_5 = df_1['cluster']
        chi_5, p_values_5, coef_5, intercept_5 = self.model_fit_and_coefficients(X_5, y_5)
        
        X_6 = df_1[['ling_dist', 'geog_dist', 'language_tui']]
        y_6 = df_1['cluster']
        chi_6, p_values_6, coef_6, intercept_6 = self.model_fit_and_coefficients(X_6, y_6)
        
        coefficient_list = [coef_1, coef_2, coef_3, coef_4, coef_5, coef_6]
        chi_pvalue_tuple=[(chi_1, p_values_1), (chi_2,p_values_2), (chi_3,p_values_3), 
                          (chi_4,p_values_4), (chi_5,p_values_5),(chi_6,p_values_6)]
        
        return coefficient_list,chi_pvalue_tuple

    def print_coefficients(self):
        "prints coefficients after logistic regression"
        print("Chi2 statistic, p-values for Hosmer-Lemeshow, and coefficients")
        coefficient_list, chi_pvalue_tuple=self.get_coefficients_chi2_stat_pvalue_hosmer_lemeshow()
        for idx, coef in enumerate(coefficient_list):
            print(f"Model {idx + 1} Coefficients:")
            for i, class_coef in enumerate(coef):
                print(f"Class {i} Coefficients: {class_coef}")
            print("*" * 40)


def run_stats():
    get_stats = GetStatistics()
    get_stats.compare_geographical_distances()
    get_stats.get_basic_descriptive_stats()
    get_stats.matrices_differences()
    get_stats.get_kruskal_global()
    get_stats.matrices_correlations()
    get_stats.get_threshold_corr_scores()
    get_stats.get_tau()
    get_stats.get_tau_tui()
    get_stats.print_coefficients()
    # print(get_stats.sorted_ling)

if __name__ == "__main__":
    run_stats()
