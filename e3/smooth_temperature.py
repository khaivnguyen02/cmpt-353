import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from pykalman import KalmanFilter

file_name = sys.argv[1]
cpu_data = pd.read_csv(file_name)

cpu_data['timestamp'] = pd.to_datetime(cpu_data['timestamp'])

plt.figure(figsize=(12, 4))
plt.plot(cpu_data['timestamp'], cpu_data['temperature'], 'b.', alpha=0.5)

# LOESS Smoothing
loess_smoothed = lowess(cpu_data['temperature'], cpu_data['timestamp'], frac=.025)
plt.plot(cpu_data['timestamp'], loess_smoothed[:, 1], 'r-')


# Kalman Smoothing
kalman_data = cpu_data[['temperature', 'cpu_percent', 'sys_load_1', 'fan_rpm']]

initial_state = kalman_data.iloc[0]
observation_covariance = np.diag([1, .005, 1, 100]) ** 2 # TODO: shouldn't be zero
transition_covariance = np.diag([.25, .0001, .25, 10]) ** 2 # TODO: shouldn't be zero
transition = [[0.98, 0.5, 0.2, -0.001],
             [0.1, 0.4, 2.1, 0],
             [0, 0, 0.98, 0],
             [0, 0, 0, 1]]

kf = KalmanFilter(initial_state_mean=initial_state,
                  initial_state_covariance=observation_covariance,
                  observation_covariance=observation_covariance,
                  transition_covariance=transition_covariance,
                  transition_matrices=transition)
kalman_smoothed, state_cov = kf.smooth(kalman_data)
plt.plot(cpu_data['timestamp'], kalman_smoothed[:, 0], 'g-')

plt.legend(['Data Points', 'Loess Smoothed', 'Kalman Smoothed'])
# plt.show() # maybe easier for testing
plt.savefig('cpu.svg')