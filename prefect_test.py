import json
from prefect import flow, task
from pathlib import Path

# 加载生成的任务
def load_tasks(project_path):
    task_file = Path(project_path) / "generated_tasks.json"
    with open("C:\\Users\\Jumbo\\Desktop\\MetaGPT-MLO\\workspace\\20240910172755\\generated_tasks.json", 'r') as file:
        tasks = json.load(file)
    return tasks

# 创建一个任务来执行生成的代码任务
@task
def run_task(task):
    task_id = task['task_id']
    description = task['task_description']
    assigned_agent = task['assigned_agent']
    file_instructions = task['file']
    
    print(f"Running {task_id}: {description}")
    print(f"Assigned to {assigned_agent}")
    print(f"Task details: {file_instructions}")
    
    # 模拟任务的执行
    # 这里你可以根据实际情况调用其他的模块或执行任务
    return f"Task {task_id} completed."

# 定义 Prefect 的 Flow
@flow
def workflow(project_path):
    tasks = load_tasks(project_path)
    
    # 按顺序执行每个任务
    for task in tasks:
        run_task(task)

if __name__ == "__main__":
    project_path = r"C:\Users\Jumbo\Desktop\MetaGPT-MLO\workspace\20240910172755"
    workflow(project_path)
