import sys
import pandas as pd
import numpy as np
import xml.dom.minidom
from math import cos, asin, sqrt, pi

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
    r = 6371 
    p = pi / 180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))

def distance(points):
    pass

def main():
    input_gpx = sys.argv[1]
    input_csv = sys.argv[2]
    
    points = get_data(input_gpx).set_index('datetime')
    sensor_data = pd.read_csv(input_csv, parse_dates=['datetime']).set_index('datetime')
    points['Bx'] = sensor_data['Bx']
    points['By'] = sensor_data['By']

    print(points)
    dist = distance(points)
    print(f'Unfiltered distance: {dist:.2f}')

    #smoothed_points = smooth(points)
    #smoothed_dist = distance(smoothed_points)
    #print(f'Filtered distance: {smoothed_dist:.2f}')

    #output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()


