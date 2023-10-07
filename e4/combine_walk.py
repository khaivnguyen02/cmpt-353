import os
import pathlib
import sys
import numpy as np
import pandas as pd
import xml.dom.minidom


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation, parse
    xmlns = 'http://www.topografix.com/GPX/1/0'

    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.10f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.10f' % (pt['lon']))
        time = doc.createElement('time')
        time.appendChild(doc.createTextNode(
            pt['datetime'].strftime("%Y-%m-%dT%H:%M:%SZ")))
        trkpt.appendChild(time)
        trkseg.appendChild(trkpt)

    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)

    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)

    doc.documentElement.setAttribute('xmlns', xmlns)

    with open(output_filename, 'w') as fh:
        fh.write(doc.toprettyxml(indent='  '))


def get_data(input_gpx):
    input_gpx = str(input_gpx.resolve())
    gpx_dom = xml.dom.minidom.parse(input_gpx)

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


def main():
    input_directory = pathlib.Path(sys.argv[1])
    output_directory = pathlib.Path(sys.argv[2])

    accl = pd.read_json(input_directory / 'accl.ndjson.gz',
                        lines=True, convert_dates=['timestamp'])[['timestamp', 'x']]
    gps = get_data(input_directory / 'gopro.gpx')
    phone = pd.read_csv(
        input_directory / 'phone.csv.gz')[['time', 'gFx', 'Bx', 'By']]

    best_offset = None
    best_correlation = -1.0

    # Find the best offset
    for offset in np.linspace(-5.0, 5.0, 101):
        first_time = accl['timestamp'].min()
        phone['timestamp'] = first_time + \
            pd.to_timedelta(phone['time'] + offset, unit='sec')

        # Round timestamps to the nearest 4 seconds
        accl['timestamp'] = accl['timestamp'].round('4s')
        phone['timestamp'] = phone['timestamp'].round('4s')

        # Group and average the data
        accl_grouped = accl.groupby('timestamp').mean().reset_index()
        phone_grouped = phone.groupby('timestamp').mean().reset_index()

        # Calculate cross-correlation between 'gFx' and 'x'
        cross_corr = (phone_grouped['gFx'] * accl_grouped['x']).sum()

        # Check if this offset has a higher correlation
        if cross_corr > best_correlation:
            best_correlation = cross_corr
            best_offset = offset

    # TODO: create "combined" as described in the exercise
    first_time = accl['timestamp'].min()
    phone['timestamp'] = first_time + \
        pd.to_timedelta(phone['time'] + best_offset, unit='sec')

    # Round timestamps to the nearest 4 seconds
    gps['datetime'] = gps['datetime'].round('4s')
    phone['timestamp'] = phone['timestamp'].round('4s')

    # Group and average the data
    gps_grouped = gps.groupby('datetime').mean().reset_index()
    phone_grouped = phone.groupby('timestamp').mean().reset_index()

    phone_grouped = phone_grouped.rename(columns={'timestamp': 'datetime'})
    combined = pd.merge(gps_grouped, phone_grouped, on='datetime', how='inner')

    print(f'Best time offset: {best_offset:.1f}')
    os.makedirs(output_directory, exist_ok=True)
    output_gpx(combined[['datetime', 'lat', 'lon']],
               output_directory / 'walk.gpx')
    combined[['datetime', 'Bx', 'By']].to_csv(
        output_directory / 'walk.csv', index=False)


main()
