import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys, os, glob
sns.set(style="ticks")

__author__ = 'Nichole Wespe'

'''
This program is for analyzing and visualizing the HU survival data from spot dilution assays. It uses results files
generated by the ImageJ macro program batch_survival_strain.py, which uses analyze_pixels.ijm. This program uses the
area calculated to compute end/start ratios and determine the maximum dilution at which the spot dilution pixel ratio
is >=0.5. This program also creates graphs displaying this information grouped by media condition.

The required input is an input directory containing results.csv files and an output directory.
'''

#def main():

input_dir = sys.argv[1]
output_dir = sys.argv[2]
pattern = os.path.join(input_dir, '*_results.csv')
print pattern
file_list = glob.glob(pattern)
print 'Found ' + str(len(file_list)) + ' files to analyze'

# initialize all_summary dataframe
all_summary = pd.DataFrame()

for strain_file in file_list:

    # read in data
    data = pd.read_csv(strain_file, converters = {'Date': lambda x: str(x), 'Strain': lambda x: str(x)})
    strain, other = os.path.basename(strain_file).split('_')
    print 'Now analyzing strain ' + str(strain)

    # match start and end data, compute ratio
    data['Strain'] = strain
    start = data[(data.Time == 'start')]
    end = data[(data.Time == 'end')]
    results = pd.merge(start, end, how='left', on=('Date', 'Well', 'Strain', 'Condition', 'Dilution'), sort=False,
                       suffixes=['_start', '_end'])
    results = results[['Date', 'Well', 'Strain', 'Condition', 'Dilution', 'Area_start', 'Area_end']]
    results['Ratio'] = results['Area_end'] / results['Area_start']
    results['Sample'] = results['Date'] + ' ' + results['Well']
    print 'Completed ratio calculations for strain ' + strain

    # find max dilution for which ratio >= 0.5
    results = results[results['Date'] != '20160614']
    # h = sns.factorplot(x='Dilution', y='Ratio', hue='Dilution', col='Condition', data=results)
    # (h.set(ylim=(-0.5, 2)))
    grouped = results.groupby('Sample', sort=False)
    max_dilutions = {}
    for name, group in grouped:
        dils = group['Dilution'].tolist()
        max_dil = 0
        for d in dils:
            ratio = group.Ratio[group.Dilution == d].iat[0]
            if ratio >= 0.5:
                max_dil = d
            else:
                break
        max_dilutions[name] = [max_dil]
    dilution_df = pd.DataFrame.from_dict(max_dilutions, orient='index')
    dilution_df.index.name = 'Sample'
    dilution_df = dilution_df.rename(columns={0: 'Max Dilution'})
    dilution_df.reset_index(level=['Sample'], inplace=True)
    info = results[['Sample', 'Date', 'Well', 'Strain', 'Condition']]
    info.drop_duplicates(inplace=True)
    max_dilution_results = pd.merge(dilution_df, info, how='inner', on=('Sample'), sort=True)

    # save max dilution results for each sample
    output_file = os.path.join(output_dir, strain + '_max_dilutions.csv')
    max_dilution_results.to_csv(output_file)

    # graph max dilution results
    g = sns.boxplot(x='Condition', y='Max Dilution', data=max_dilution_results)
    g = sns.swarmplot(x='Condition', y='Max Dilution', data=max_dilution_results, color="black")
    (g.set(ylim=(-0.5, 4.5), title=strain))
    plt.ylabel('Max Dilution with Ratio >= 0.5')
    graph_file = os.path.join(output_dir, strain + '_HU_survival.png')
    plt.savefig(graph_file, dpi=300, bbox_inches='tight')
    plt.close()
    print 'Created graph for strain ' + strain

    # summarize max dilution results and add to final summary
    max_grouped = max_dilution_results.groupby('Condition', sort=False)
    max_count = max_grouped['Max Dilution'].count()
    max_count = max_count.rename('N')
    avgs = max_grouped['Max Dilution'].agg([np.mean, np.std, np.median])
    summary = avgs.join(max_count)
    summary['Strain'] = strain
    summary = summary[['Strain', 'N', 'mean', 'std', 'median']]
    df = max_dilution_results.groupby(['Condition', 'Max Dilution']).size().reset_index(name='count')
    df = df.pivot(index='Condition', columns='Max Dilution', values='count')
    summary = summary.join(df)  # add counts of each dilution level instead of mode
    summary.reset_index(inplace=True)
    all_summary = all_summary.append(summary)

# save summary dataframe
summary_file = os.path.join(output_dir, 'HU_survival_summary.csv')
all_summary.to_csv(summary_file)


#if __name__=='__main__':
#    main()