from getting_matrices import getdata
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def func(x, a, b):
    return a * np.log(x) + b

def extract_upper_triangle(df):
    return df.where(np.triu(np.ones(df.shape, dtype=bool), k=1))

def group_data(geo_distances, ling_distances, num_intervals=20):
    """Bins data and calculate mean and standard deviation of binned groups."""
    df = pd.DataFrame({'geo': geo_distances, 'ling': ling_distances})
    df['geo_interval'] = pd.cut(df['geo'], bins=num_intervals)
    grouped = df.groupby('geo_interval').agg({
        'geo': 'mean',
        'ling': ['mean', 'std']
    }).reset_index()
    grouped.columns = ['interval', 'geo_mean', 'ling_mean', 'ling_std']
    return grouped

def refined_distances(geographic_distance, linguistic_distance):
    """Prepares the two matrices for plotting."""
    geo_distances = extract_upper_triangle(geographic_distance).stack().values
    non_zero_geo_distances = geo_distances[geo_distances != 0]
    ling_distances = extract_upper_triangle(linguistic_distance).stack().values
    ling_distances = ling_distances[ling_distances !=0]
    return geo_distances, non_zero_geo_distances, ling_distances

def scatterplot(geographic_distance, linguistic_distance):
    """Returns a bivariate distribution between datapoints in the two matrices."""
    _, non_zero_geo_distances, ling_distances = refined_distances(geographic_distance, linguistic_distance)
    plt.figure(figsize=(8, 6))
    plt.scatter(non_zero_geo_distances, ling_distances, label='Data points')
    plt.xlabel('Geographic Distance')
    plt.ylabel('Linguistic Distance')
    plt.title('Relationship between Geographic and Linguistic Distance')
    plt.legend()
    plt.grid(True)
    plt.savefig("Bivariate_relationship")  
    plt.show()
    print("Saved scatterplot to file successfully")

def trendplot(geographic_distance, linguistic_distance):
    """Returns a trend graph of linear relationship between distances."""
    geo_distances, non_zero_geo_distances, ling_distances = refined_distances(geographic_distance, linguistic_distance)
    popt, pcov = curve_fit(func, non_zero_geo_distances, ling_distances)
    x_fit = np.linspace(min(non_zero_geo_distances), max(non_zero_geo_distances), 100)
    y_fit = func(x_fit, *popt)
    grouped_data = group_data(non_zero_geo_distances, ling_distances)

    plt.figure(figsize=(10, 7))
    plt.scatter(non_zero_geo_distances, ling_distances, alpha=0.3, label='Data points')
    plt.errorbar(grouped_data['geo_mean'], grouped_data['ling_mean'], 
                 yerr=grouped_data['ling_std'], fmt='o-', color='red', 
                 ecolor='lightcoral', capsize=5, label='Trend (mean with std dev)')
    plt.plot(x_fit, y_fit, 'g--', label="Fitted curve")
    plt.xlabel('Geographic Distance')
    plt.ylabel('Linguistic Distance')
    plt.title('Relationship between Geographic and Linguistic Distance')
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.savefig("Trendplot")  
    plt.show()
    print("Saved trend plot to file successfully")

def segment_data(geo_distances, ling_distances, num_segments=5):
    "returns a segmented data for analysis"

    df = pd.DataFrame({'geo': geo_distances, 'ling': ling_distances})
    df = df.sort_values('geo')
    # segment_size = len(df) // num_segments
    df['segment'] = pd.cut(df.index, bins=num_segments, labels=range(num_segments))
    return df

def segmented_trendplot(geographic_distance, linguistic_distance, num_segments=5):
    "returns a segmented plot for analysis"
    _, non_zero_geo_distances, ling_distances = refined_distances(geographic_distance, linguistic_distance)

    df = segment_data(non_zero_geo_distances, ling_distances, num_segments)

    plt.figure(figsize=(12, 8))
    plt.scatter(df['geo'], df['ling'], alpha=0.3, label='Data points')

    colors = plt.cm.rainbow(np.linspace(0, 1, num_segments))
    for segment in range(num_segments):
        segmented_data = df[df['segment'] == segment]
        
        # popt, _ = curve_fit(func, segmented_data['geo'], segmented_data['ling'])
        # x_fit = np.linspace(segmented_data['geo'].min(), segmented_data['geo'].max(), 100)
        # y_fit = func(x_fit, *popt)
        
        # plt.plot(x_fit, y_fit, '--', color=colors[segment], 
        #             label=f"Segment {segment+1} fit")
        
        grouped = group_data(segmented_data['geo'], segmented_data['ling'], num_intervals=5)
        plt.errorbar(grouped['geo_mean'], grouped['ling_mean'], 
                        yerr=grouped['ling_std'], fmt='o-', color=colors[segment], 
                        ecolor='lightgray', capsize=5, 
                        label=f'Segment {segment+1} trend')

    plt.xlabel('Geographic Distance')
    plt.ylabel('Linguistic Distance')
    plt.title('Segmented Relationship between Geographic and Linguistic Distance')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("Segmented_Trendplot")
    plt.show()
    print("Saved segmented trend plot to file successfully")

def getgraphs():
    _, geographic_distance, linguistic_distance = getdata()
    scatterplot(geographic_distance, linguistic_distance)
    trendplot(geographic_distance, linguistic_distance)
    segmented_trendplot(geographic_distance, linguistic_distance)

if __name__ == "__main__":
    getgraphs()

