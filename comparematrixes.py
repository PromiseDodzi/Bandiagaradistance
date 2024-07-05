from getting_matrices import getdata
from scipy.stats import ttest_rel
import pandas as pd
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.stats import pearsonr

def mantel_test(X, Y, perms=1000, method='pearson'):
    X = pdist(X)
    Y = pdist(Y)
    corr, _ = pearsonr(X, Y)
    pvalue = 1
    for _ in range(perms):
        Y_perm = np.random.permutation(Y)
        corr_perm, _ = pearsonr(X, Y_perm)
        pvalue += (corr_perm >= corr)
    return corr, pvalue / (perms + 1)

def getcohend(geographic_matx, linguistic_matx):
    differences = linguistic_matx.values.flatten() - geographic_matx.values.flatten()
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)  
    cohen_d = mean_diff / std_diff
    return cohen_d

def descriptivestat():
    "returns descriptive statistics of the comparison of both matrices"
    _, geographic_matx, linguistic_matx = getdata()
    differences = np.abs(linguistic_matx.values - geographic_matx.values)
    average_difference = np.mean(differences)
    correlation_coefficient = np.corrcoef(linguistic_matx.values.flatten(), geographic_matx.values.flatten())[0, 1]
    t_statistic, p_value = ttest_rel(linguistic_matx.values.flatten(), geographic_matx.values.flatten())
    cohen_d = getcohend(geographic_matx, linguistic_matx)
    mantel_statistic, mantel_p_value = mantel_test(linguistic_matx.values, geographic_matx.values)

    results = pd.DataFrame({
        'Average Difference': [average_difference],
        'Correlation Coefficient': [correlation_coefficient],
        'Paired t-test Statistic': [t_statistic],
        'P-value (t-test)': [p_value],
        'Mantel Statistic': [mantel_statistic],
        'P-value (Mantel test)': [mantel_p_value],
        "Cohen's d": [cohen_d]
    })

    ling_describe=pd.DataFrame(linguistic_matx.describe())
    geog_describe=pd.DataFrame(geographic_matx.describe())

    print("Comparative and individual matrice statistics written to file")
    return results.to_csv("statistical_tests.csv", index=False), ling_describe.to_csv("linguistic_matrix_description.csv"), geog_describe.to_csv("geographic_matrix_description.csv")

if __name__ == "__main__":
    descriptivestat()

