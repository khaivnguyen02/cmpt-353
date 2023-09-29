import sys
import pandas as pd
import numpy as np
import xml.dom.minidom
from pykalman import KalmanFilter

def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.7f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.7f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')

def get_data(gpx_file_path):
    gpx_dom = xml.dom.minidom.parse(gpx_file_path)
   
    trkpts = gpx_dom.getElementsByTagName('trkpt')
    
    for trkpt in trkpts:
        latitudes = [float(trkpt.getAttribute('lat')) for trkpt in trkpts]
        longtitudes = [float(trkpt.getAttribute('lon')) for trkpt in trkpts]
        timestamps = [
            trkpt.getElementsByTagName('time')[0].firstChild.nodeValue
            if trkpt.getElementsByTagName('time') else np.nan
            for trkpt in trkpts
            ]
        
    data = {
        'datetime': timestamps,
        'lat': latitudes,
        'lon': longtitudes
    }
        
    df = pd.DataFrame(data)

    df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        
    return df

# Reference: https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000 # metres
    p = np.pi / 180
    a = 0.5 - np.cos((lat2-lat1)*p)/2 + np.cos(lat1*p) * np.cos(lat2*p) * (1-np.cos((lon2-lon1)*p))/2
    return 2 * r * np.arcsin(np.sqrt(a))

def distance(points):
    return haversine(points['lat'].shift(1), points['lon'].shift(1), points['lat'], points['lon']).sum()

def smooth(points):
    initial_state = points.iloc[0]
    observation_covariance = np.diag([10**-5, 10**-5, 1, 1]) ** 2
    transition_covariance = np.diag([10**-5, 10**-5, 0.75, 0.75]) ** 2
    transition = [[1, 0, (5*10**-7), (33*10**-7)],
                  [0, 1, (-48*10**-7), (9*10**-7)],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]]
    
    kf = KalmanFilter(initial_state_mean=initial_state,
                      initial_state_covariance=observation_covariance,
                      observation_covariance=observation_covariance,
                      transition_covariance=transition_covariance,
                      transition_matrices=transition)
    
    kalman_smoothed, _ = kf.smooth(points)
    kalman_smoothed = pd.DataFrame(kalman_smoothed)
    kalman_smoothed = kalman_smoothed.rename(columns={0: 'lat', 1: 'lon', 2: 'Bx', 3: 'By'})
    
    return kalman_smoothed

def main():
    input_gpx = sys.argv[1]
    input_csv = sys.argv[2]
    
    points = get_data(input_gpx).set_index('datetime')
    sensor_data = pd.read_csv(input_csv, parse_dates=['datetime']).set_index('datetime')
    points['Bx'] = sensor_data['Bx']
    points['By'] = sensor_data['By']

    dist = distance(points)
    print(f'Unfiltered distance: {dist:.2f}')

    smoothed_points = smooth(points)
    smoothed_dist = distance(smoothed_points)
    print(f'Filtered distance: {smoothed_dist:.2f}')

    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()


