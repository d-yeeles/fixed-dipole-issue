import pandas as pd
import numpy as np

thunderstorm_df = pd.read_csv('thunderstorm_results_gaussian.csv')
ground_truth_df = pd.read_csv('ground_truth_gaussian.csv')

radius = 500

def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

correct = []
false_positives = []
false_negatives = []

for frame in ground_truth_df['frame'].unique():
    gt_points = ground_truth_df[ground_truth_df['frame'] == frame].copy()
    ts_points = thunderstorm_df[thunderstorm_df['frame'] == frame].copy()

    matched_estimates = set()
    matched_gt = set()

    # Find nearest estimated point for each ground truth point
    for _, gt_row in gt_points.iterrows():
        distances = ts_points.apply(lambda row: calculate_distance(gt_row['x_tru'], gt_row['y_tru'], row['x [nm]'], row['y [nm]']), axis=1)
        nearby_estimates = distances[distances <= radius]

        # If there are points within the radius, first find the nearest one
        if len(nearby_estimates) > 0:
            closest_estimate_idx = nearby_estimates.idxmin()
            closest_estimate = ts_points.loc[closest_estimate_idx]

            # Mark that as 'correct'
            correct_row = closest_estimate.copy()
            correct_row['az_tru'] = gt_row['az_tru']
            correct_row['inc_tru'] = gt_row['inc_tru']
            correct.append(correct_row)
            matched_estimates.add(closest_estimate_idx)
            matched_gt.add(gt_row.name) # Save the corresponding frame (so we know inc/az that worked/fialed)

            # Any additional estimates within the radius are false positives
            for idx in nearby_estimates.index:
                if idx != closest_estimate_idx:
                    false_positives_row = ts_points.loc[idx].copy()
                    false_positives_row['az_tru'] = gt_row['az_tru']
                    false_positives_row['inc_tru'] = gt_row['inc_tru']
                    false_positives.append(false_positives_row)

        # If there are no points within radius, mark as false negative
        if len(nearby_estimates) == 0:
            false_negatives_row = gt_row.copy()
            false_negatives_row['az_tru'] = gt_row['az_tru']
            false_negatives_row['inc_tru'] = gt_row['inc_tru']
            false_negatives.append(false_negatives_row)

    # Any remaining estimates (i.e. outside radius) are false positives
    for idx, ts_row in ts_points.iterrows():
        if idx not in matched_estimates:
            false_positives_row = ts_row.copy()
            false_positives_row['az_tru'] = np.nan
            false_positives_row['inc_tru'] = np.nan
            false_positives.append(false_positives_row)

pd.DataFrame(correct).to_csv('correct_gaussian.csv', index=False)
pd.DataFrame(false_positives).to_csv('false_positives_gaussian.csv', index=False)
pd.DataFrame(false_negatives).to_csv('false_negatives_gaussian.csv', index=False)





thunderstorm_df = pd.read_csv('thunderstorm_results_hinterer.csv')
ground_truth_df = pd.read_csv('ground_truth_hinterer.csv')

correct = []
false_positives = []
false_negatives = []

for frame in ground_truth_df['frame'].unique():
    gt_points = ground_truth_df[ground_truth_df['frame'] == frame].copy()
    ts_points = thunderstorm_df[thunderstorm_df['frame'] == frame].copy()

    matched_estimates = set()
    matched_gt = set()

    # Find nearest estimated point for each ground truth point
    for _, gt_row in gt_points.iterrows():
        distances = ts_points.apply(lambda row: calculate_distance(gt_row['x_tru'], gt_row['y_tru'], row['x [nm]'], row['y [nm]']), axis=1)
        nearby_estimates = distances[distances <= radius]

        # If there are points within the radius, first find the nearest one
        if len(nearby_estimates) > 0:
            closest_estimate_idx = nearby_estimates.idxmin()
            closest_estimate = ts_points.loc[closest_estimate_idx]

            # Mark that as 'correct'
            correct_row = closest_estimate.copy()
            correct_row['az_tru'] = gt_row['az_tru']
            correct_row['inc_tru'] = gt_row['inc_tru']
            correct.append(correct_row)
            matched_estimates.add(closest_estimate_idx)
            matched_gt.add(gt_row.name) # Save the corresponding frame (so we know inc/az that worked/fialed)

            # Any additional estimates within the radius are false positives
            for idx in nearby_estimates.index:
                if idx != closest_estimate_idx:
                    false_positives_row = ts_points.loc[idx].copy()
                    false_positives_row['az_tru'] = gt_row['az_tru']
                    false_positives_row['inc_tru'] = gt_row['inc_tru']
                    false_positives.append(false_positives_row)

        # If there are no points within radius, mark as false negative
        if len(nearby_estimates) == 0:
            false_negatives_row = gt_row.copy()
            false_negatives_row['az_tru'] = gt_row['az_tru']
            false_negatives_row['inc_tru'] = gt_row['inc_tru']
            false_negatives.append(false_negatives_row)

    # Any remaining estimates (i.e. outside radius) are false positives
    for idx, ts_row in ts_points.iterrows():
        if idx not in matched_estimates:
            false_positives_row = ts_row.copy()
            false_positives_row['az_tru'] = np.nan
            false_positives_row['inc_tru'] = np.nan
            false_positives.append(false_positives_row)

pd.DataFrame(correct).to_csv('correct_hinterer.csv', index=False)
pd.DataFrame(false_positives).to_csv('false_positives_hinterer.csv', index=False)
pd.DataFrame(false_negatives).to_csv('false_negatives_hinterer.csv', index=False)






# --------------------------------------





import matplotlib.pyplot as plt

def safe_read_csv(file):
    try:
        df = pd.read_csv(file)
        if df.empty:
            print(f"Warning: {file} is empty.")
        return df
    except pd.errors.EmptyDataError:
        print(f"Warning: {file} is empty or missing.")
        return pd.DataFrame()  # Return an empty DataFrame to prevent errors

# Read the data
ground_truth_df = safe_read_csv('ground_truth_gaussian.csv')
correct_df = safe_read_csv('correct_gaussian.csv')
false_positives_df = safe_read_csv('false_positives_gaussian.csv')
false_negatives_df = safe_read_csv('false_negatives_gaussian.csv')

# Convert radians to degrees (only if the columns exist)
for df in [ground_truth_df, correct_df, false_positives_df, false_negatives_df]:
    if 'inc_tru' in df.columns and not df.empty:
        df['inc_tru'] *= 180 / np.pi

# Define the azimuth bins (0 to 359, in steps of 10)
inc_bins = ground_truth_df['inc_tru'].unique()
#az_bins = ground_truth_df['az_tru'].unique()

# Count occurrences of azimuth values in each bin for each category
dataset_counts_inc = []
for i, dataset in enumerate([correct_df, false_positives_df, false_negatives_df]):
    if dataset.empty:
        dataset_counts_inc.append(np.zeros(len(inc_bins) - 1))  # Return zeros if the DataFrame is empty
    else:
        counts, _ = np.histogram(dataset['inc_tru'], bins=inc_bins, range=(0, 90))
        dataset_counts_inc.append(counts)

correct_counts_inc = dataset_counts_inc[0]
false_positives_counts_inc = dataset_counts_inc[1]
false_negatives_counts_inc = dataset_counts_inc[2]

# Total counts per bin (sum of all categories for that bin)
total_counts_inc = correct_counts_inc + false_positives_counts_inc + false_negatives_counts_inc

# Normalize the counts so that the sum of each bin is 1
correct_proportions_inc = (correct_counts_inc / total_counts_inc)*100
false_positives_proportions_inc = (false_positives_counts_inc / total_counts_inc)*100
false_negatives_proportions_inc = (false_negatives_counts_inc / total_counts_inc)*100



correct_proportions_inc_gaussian = correct_proportions_inc
false_positives_proportions_inc_gaussian = false_positives_proportions_inc
false_negatives_proportions_inc_gaussian = false_negatives_proportions_inc








# Read the data
ground_truth_df = safe_read_csv('ground_truth_hinterer.csv')
correct_df = safe_read_csv('correct_hinterer.csv')
false_positives_df = safe_read_csv('false_positives_hinterer.csv')
false_negatives_df = safe_read_csv('false_negatives_hinterer.csv')

# Convert radians to degrees (only if the columns exist)
for df in [ground_truth_df, correct_df, false_positives_df, false_negatives_df]:
    if 'inc_tru' in df.columns and not df.empty:
        df['inc_tru'] *= 180 / np.pi

# Define the azimuth bins (0 to 359, in steps of 10)
inc_bins = ground_truth_df['inc_tru'].unique()
#az_bins = ground_truth_df['az_tru'].unique()

# Count occurrences of azimuth values in each bin for each category
dataset_counts_inc = []
for i, dataset in enumerate([correct_df, false_positives_df, false_negatives_df]):
    if dataset.empty:
        dataset_counts_inc.append(np.zeros(len(inc_bins) - 1))  # Return zeros if the DataFrame is empty
    else:
        counts, _ = np.histogram(dataset['inc_tru'], bins=inc_bins, range=(0, 90))
        dataset_counts_inc.append(counts)

correct_counts_inc = dataset_counts_inc[0]
false_positives_counts_inc = dataset_counts_inc[1]
false_negatives_counts_inc = dataset_counts_inc[2]

# Total counts per bin (sum of all categories for that bin)
total_counts_inc = correct_counts_inc + false_positives_counts_inc + false_negatives_counts_inc

# Normalize the counts so that the sum of each bin is 1
correct_proportions_inc = (correct_counts_inc / total_counts_inc)*100
false_positives_proportions_inc = (false_positives_counts_inc / total_counts_inc)*100
false_negatives_proportions_inc = (false_negatives_counts_inc / total_counts_inc)*100



correct_proportions_inc_hinterer = correct_proportions_inc
false_positives_proportions_inc_hinterer = false_positives_proportions_inc
false_negatives_proportions_inc_hinterer = false_negatives_proportions_inc













# Plot the results
bar_width_inc = 1

fig, axs = plt.subplots(2, 1, figsize=(9, 10))

axs[0].bar(inc_bins[:-1], correct_proportions_inc_gaussian, width=bar_width_inc, align='edge', label='Correct')
axs[0].bar(inc_bins[:-1], false_positives_proportions_inc_gaussian, width=bar_width_inc, align='edge', bottom=correct_proportions_inc_gaussian, label='False Positives')
axs[0].bar(inc_bins[:-1], false_negatives_proportions_inc_gaussian, width=bar_width_inc, align='edge', bottom=correct_proportions_inc_gaussian + false_positives_proportions_inc_gaussian, label='False Negatives')
axs[0].set_xlabel('θ, °')
axs[0].set_ylabel('Proportion, %')
axs[0].set_title('Gaussian')
axs[0].legend(loc='lower right')

axs[1].bar(inc_bins[:-1], correct_proportions_inc_hinterer, width=bar_width_inc, align='edge', label='Correct')
axs[1].bar(inc_bins[:-1], false_positives_proportions_inc_hinterer, width=bar_width_inc, align='edge', bottom=correct_proportions_inc_hinterer, label='False Positives')
axs[1].bar(inc_bins[:-1], false_negatives_proportions_inc_hinterer, width=bar_width_inc, align='edge', bottom=correct_proportions_inc_hinterer + false_positives_proportions_inc_hinterer, label='False Negatives')
axs[1].set_xlabel('θ, °')
axs[1].set_ylabel('Proportion, %')
axs[1].set_title('Hinterer')
axs[1].legend(loc='lower right')

#plt.show()
plt.savefig(f"accuracy_results.png", dpi=300)
plt.close()

