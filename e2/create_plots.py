import sys
import pandas as pd
import matplotlib.pyplot as plt

filename1 = sys.argv[1]
filename2 = sys.argv[2]

df1 = pd.read_csv(filename1, sep=' ', header=None, index_col=1,
        names=['lang', 'page', 'views', 'bytes'])
df2 = pd.read_csv(filename2, sep=' ', header=None, index_col=1,
        names=['lang', 'page', 'views', 'bytes'])

plt.figure(figsize=(10, 5)) 
# Plot 1: Distribution of Views
sorted_df1 = df1.sort_values(by='views', ascending=False)
plt.subplot(1, 2, 1) # subplots in 1 row, 2 columns, select the first
plt.plot(sorted_df1['views'].values)

plt.title('Popularity Distribution')
plt.xlabel('Rank')
plt.ylabel('Views')

# Plot 2: Hourly Views
df1['views_from_df2'] = df2['views']
plt.subplot(1, 2, 2)
plt.plot(df1['views'], df1['views_from_df2'], 'b.')
plt.xscale('log')
plt.yscale('log')

plt.title('Hourly Correlation')
plt.xlabel('Hour 1 Views')
plt.ylabel('Hour 2 Views')

plt.savefig('wikipedia.png')