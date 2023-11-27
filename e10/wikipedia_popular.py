import sys
from pyspark.sql import SparkSession, functions, types
import re

spark = SparkSession.builder.appName('popular wikipedia pages').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 8)  # make sure we have Python 3.8+
assert spark.version >= '3.2'  # make sure we have Spark 3.2+

views_schema = types.StructType([
    types.StructField('language', types.StringType()),
    types.StructField('title', types.StringType()),
    types.StructField('requested_times', types.LongType()),
    types.StructField('returned_bytes', types.LongType())
])


def extract_hour_from_path(path):
    # Assume filenames will be in the format pagecounts-YYYYMMDD-HHMMSS*
    # Output: YYYYMMDD-HH
    pattern = r'pagecounts-(\d{8})-(\d{2}).*'

    match = re.search(pattern, path)
    if match:
        date = match.group(1)
        hour = match.group(2)
        return f"{date}-{hour}"
    else:
        return None


def main(in_directory, out_directory):
    views = spark.read.csv(in_directory, sep='', schema=views_schema).withColumn(
        'filename', functions.input_file_name())

    views = views.filter((views['language'] == 'en') &
                         (views['title'] != 'Main_Page') &
                         (~views['title'].startswith('Special:')))

    path_to_hour = functions.udf(
        extract_hour_from_path, returnType=types.StringType())

    views = views.withColumn('date_hour', path_to_hour(views.filename))

    views = views.cache()

    top_views = views.groupBy('date_hour').agg(
        functions.max('requested_times').alias('requested_times'))

    views = views.join(top_views, on=['date_hour', 'requested_times'])
    views = views.orderBy('date_hour', 'title')
    views = views.select('date_hour', 'title', 'requested_times')

    views.write.csv(out_directory, mode='overwrite')


if __name__ == '__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)
