from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2021, 7, 30),
    'owner': 'Airflow',
    'retries': 3,
    'retry_delay': timedelta(seconds = 5)
}

def on_success_dag(dict):
    print('on success')
    print(dict)

def on_failure_dag(dict):
    print('on failure')
    print(dict)

with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, catchup=True, dagrun_timeout=timedelta(seconds=60), on_success_callback=on_success_dag, on_failure_callback=on_failure_dag) as dag:
# iteration 1
# add dagrun_timeout = timedelta(seconds = 60)  - the dag succeeds
# iteration 2 - set dagrun_timeout to 20 seconds
# the dagrun timeouts
# further it is claimed dag runs wil be triggered even if tasks have depends_on_past
# it is claimed that further dag runs will be triggered even if the earlier one has failed
# it is claimed that the dagrun_timeout parameter is enforced if number of active dag runs is equal to max active runs per dag
# all of the three were found to not work
# if there is depends_on_past and the earlier task failed without marking that as a success or clearing that life does not go ahead
# next iteration - add dag success, failure callbacks
# next iteration - add retries and retry_delay to default_args
# next iteration - add on_success_task and on_failure_task callbacks for tasks
# next iteration - add execution_timeout for task

    # Task 1
    # t1 = BashOperator(task_id='t1', bash_command="sleep 10;echo 'alerts first task'", depends_on_past=True)
    t1 = BashOperator(task_id='t1', bash_command="exit 1")
    
    # Task 2
    t2 = BashOperator(task_id='t2', bash_command="echo 'second task'")

    t1 >> t2