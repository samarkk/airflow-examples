from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

default_args = {
    'start_date': datetime(2021, 7, 1),
    'owner': 'Airflow'
}

with DAG(dag_id="a_my_first_dag", schedule_interval="0 0 * * *",default_args=default_args) as dag:
    # task 1
    bash_task_1 = BashOperator(task_id="bash_task_1", bash_command="echo 'first task from my_first_dag'")

    #task 2
    bash_task_2 = BashOperator(task_id="bash_task_2",bash_command="echo 'second task from my_first_dag'")

    bash_task_1 >> bash_task_2
