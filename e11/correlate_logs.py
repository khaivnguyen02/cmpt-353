import sys
assert sys.version_info >= (3, 8) # make sure we have Python 3.8+
from pyspark.sql import SparkSession, functions, types, Row
import re
import math

line_re = re.compile(r"^(\S+) - - \[\S+ [+-]\d+\] \"[A-Z]+ \S+ HTTP/\d\.\d\" \d+ (\d+)$")


def line_to_row(line):
    """
    Take a logfile line and return a Row object with hostname and bytes transferred.
    Return None if regex doesn't match.
    """
    m = line_re.match(line)
    if m:
        return Row(hostname=m.group(1), bytes_transferred=m.group(2))
    else:
        return None


def not_none(row):
    """
    Is this None? Hint: .filter() with it.
    """
    return row is not None


def create_row_rdd(in_directory):
    log_lines = spark.sparkContext.textFile(in_directory)
    
    # return an RDD of Row() objects
    return log_lines.map(line_to_row).filter(not_none)


def main(in_directory):
    # 1. Get the data out of the files into a DataFrame where you have the hostname and number of bytes for each request
    logs = spark.createDataFrame(create_row_rdd(in_directory))

    # 2. Group by hostname; get the number of requests and sum of bytes transferred, to form a data point
    data_points = logs.groupBy('hostname').agg(
        functions.count('*').alias('x'),
        functions.sum('bytes_transferred').alias('y')
    )

    # 3. Produce six values: 1, x, x^2, y, y^2, xy. 
    # Add these to get the six sums
    six_values = data_points.select(
        functions.lit(1).alias('1s'),
        data_points['x'],
        (data_points['x'] ** 2).alias('x^2'),
        data_points['y'],
        (data_points['y'] ** 2).alias('y^2'),
        (data_points['x'] * data_points['y']).alias('xy')
    )

    six_sums = six_values.groupBy().agg(
        functions.sum('1s').alias('n'),
        functions.sum('x').alias('x'),
        functions.sum('x^2').alias('x^2'),
        functions.sum('y').alias('y'),
        functions.sum('y^2').alias('y^2'),
        functions.sum('xy').alias('xy')
    )

    # 4. Calculate the final value of r
    six_floats = six_sums.rdd.first()
    numerator = six_floats['n']*six_floats['xy'] - six_floats['x'] * six_floats['y']
    denominator = math.sqrt((six_floats['n']*six_floats['x^2']) - (six_floats['x'] ** 2)) * math.sqrt((six_floats['n']*six_floats['y^2']) - (six_floats['y'] ** 2))

    r = numerator / denominator
    print(f"r = {r}\nr^2 = {r*r}")
    # Built-in function should get the same results.
    # print(data_points.corr('x', 'y'))


if __name__=='__main__':
    in_directory = sys.argv[1]
    spark = SparkSession.builder.appName('correlate logs').getOrCreate()
    assert spark.version >= '3.2' # make sure we have Spark 3.2+
    spark.sparkContext.setLogLevel('WARN')

    main(in_directory)
