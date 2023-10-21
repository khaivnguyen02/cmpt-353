import time
import numpy as np
import pandas as pd
from implementations import all_implementations

NUMBER_OF_SAMPLES = 50

data = pd.DataFrame(columns=['qs1', 'qs2', 'qs3', 'qs4', 'qs5', 'merge1', 'partition_sort'], index = np.arange(NUMBER_OF_SAMPLES))

for i in range(NUMBER_OF_SAMPLES):
    random_array = np.random.randint(-10000, 10000, size=10000)
    for sort in all_implementations:
        st = time.time()
        res = sort(random_array)
        en = time.time()
        data.iloc[i][sort.__name__] = en - st

data.to_csv('data.csv', index=False)