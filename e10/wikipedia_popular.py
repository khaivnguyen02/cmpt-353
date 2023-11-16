import sys
from pyspark.sql import SparkSession, functions, types

spark = SparkSession.builder.appName('popular wikipedia pages').getOrCreate()
spark.sparkContext.setLogLevel('WARN')

assert sys.version_info >= (3, 8) # make sure we have Python 3.8+
assert spark.version >= '3.2' # make sure we have Spark 3.2+

views_schema = types.StructType([
    types.StructField('language', types.StringType()),
    types.StructField('title', types.StringType()),
    types.StructField('requested_times', types.LongType()),
    types.StructField('returned_bytes', types.LongType())
])

def main(in_directory, out_directory):
    views = spark.read.csv(in_directory, schema=views_schema).withColumn('filename', functions.input_file_name())

if __name__=='__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    main(in_directory, out_directory)