import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv('data.csv')

    anova = stats.f_oneway(df['qs1'], df['qs2'], df['qs3'], df['qs4'], df['qs5'], df['merge1'], df['partition_sort'])
    print(anova.pvalue)

    df_melt = pd.melt(df)
    posthoc = pairwise_tukeyhsd(
        df_melt['value'], df_melt['variable'],
        alpha=0.5
    )
    print(posthoc)
    fig = posthoc.plot_simultaneous()
    plt.show()

    print("Raking of the sorting implementations by speed:")
    print(df.describe().loc['mean'].sort_values())

    plt.show()

if __name__ == '__main__':
    main()