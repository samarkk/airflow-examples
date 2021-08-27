from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email import EmailOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta
import csv
import requests
import json

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email" : "admin@localhost.com",
    "retries": 1,
    "retry_delta": timedelta(minutes=5)
}

def download_fo_data():
    indata = requests.get('https://raw.githubusercontent.com/samarkk/test/master/fo01JAN2020bhav.csv')
    file_save_location = '/tmp/fo_from_rest.csv'
    # file to write to
    with open(file_save_location, mode='a') as ftwto:
        for x in  indata.iter_lines():
            str_to_write = str(x)[2: len(str(x)) -2] + '\n'
            ftwto.write(str_to_write)


def _get_message() -> str:
    return 'hi from wah bhaiye of forex data pipeline'

with DAG("fo_data_pipeline", start_date=datetime(2021,1,1), schedule_interval="@daily", default_args=default_args, catchup=False) as  dag:

    fo_data_available = HttpSensor(
        task_id = 'fo_data_available',
        http_conn_id = 'http-foconn',
        endpoint="fo01JAN2020bhav.csv",
        response_check=lambda response: "INSTRUMENT" in response.text,
        poke_interval=5,
        timeout=20
    )

    download_fo_data = PythonOperator(
        task_id = 'download_fo_data',
        python_callable = download_fo_data
    )

    add_fo_data_to_hdfs = BashOperator(
        task_id = 'add_fo_data_to_hdfs',
        bash_command='''
        hdfs dfs -mkdir /fodata
        hdfs dfs -put -f /tmp/fo_from_rest.csv /fodata
        '''
    )

    upload_file_to_kafka = BashOperator(
        task_id='upload_file_to_kafka',
        bash_command='''
        python /home/samar/airflow-examples/scripts/ProducerFileClient.py localhost:9092 nsefo-airflow /mnt/d/tmp/fo_from_rest.csv
        '''
    )
    
    creating_fodata_table = HiveOperator(
        task_id="creating_fodata_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE TABLE IF NOT EXISTS fodata_table(
                symbol STRING,
                expiry_dt STRING,
                totoi INT,
                totval DOUBLE
                )
            STORED AS PARQUET
        """
    )

    process_fo_data = SparkSubmitOperator(
        task_id = 'process_fo_data',
        application = '/home/samar/airflow-examples/scripts/spark_fo_data_processing.py',
        conn_id = 'spark_conn',
        verbose = False
    )

    fo_data_available >> download_fo_data >> upload_file_to_kafka
    upload_file_to_kafka >> creating_fodata_table >> process_fo_data