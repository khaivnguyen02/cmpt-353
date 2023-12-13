import re
import string
from pyspark.sql.functions import split, explode, lower, count
from pyspark.sql import SparkSession
import sys
assert sys.version_info >= (3.8)
# regex that matches spaces and/or punctuation
wordbreak = r'[%s\s]+' % (re.escape(string.punctuation),)


def main(in_directory, out_directory):
    # 1. Read lines from the files with spark.read.text
    df = spark.read.text(in_directory)

    # 2. Split the lines into words with the regex. Use the split and explode functions. Normalize all of the strings to lower-case.
    df = df.select(split(df.value, wordbreak).alias('split'))
    df = df.select(explode(df.split).alias('exploded'))
    df = df.select(lower(df.exploded).alias('word'))

    # 3. Count the number of times each word occurs
    df = df.groupBy('word').agg(count(df.word).alias('count'))

    # 4. Sort by decreasing count (frequent words first) and alphabetically if there's a tie
    df = df.orderBy(['count', 'word'], ascending=[False, True])

    # 5. Remove empty strings from the output
    df = df.filter(df.word != '')

    # 6. Write results as CSV files with the word in the first column, and count in the second
    df.write.csv(out_directory, mode='overwrite')


if __name__ == '__main__':
    in_directory = sys.argv[1]
    out_directory = sys.argv[2]
    spark = SparkSession.builder.appName(
        'Word Count').getOrCreate()
    assert spark.version >= '3.2'  # make sure we have Spark 3.2+
    spark.sparkContext.setLogLevel('WARN')

    main(in_directory, out_directory)
