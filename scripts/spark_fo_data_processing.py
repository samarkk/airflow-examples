from pyspark.sql import SparkSession
from pyspark.sql.functions import*

spark = SparkSession \
    .builder \
    .appName('Forex processing') \
    .config('hive.metastore.uris', 'thrift://localhost:9083') \
    .enableHiveSupport().getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.shuffle.partitions", 2)

file_location = "hdfs://localhost:8020/fodata"

cmdf = spark.read \
    .option('inferSchema', True) \
    .option('header', True) \
    .csv(file_location)

cmdf_grouped = cmdf \
    .groupBy("symbol", "expiry_dt") \
        .agg(sum(col("open_int")).alias("totoi"), sum(col("val_inlakh")).alias("totval"))

cmdf_grouped.createOrReplaceTempView("cmdtbl")

spark.sql("insert into fodata_table select * from cmdtbl")

        