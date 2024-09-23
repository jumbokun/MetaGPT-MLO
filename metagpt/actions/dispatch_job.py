import json
from typing import List, Dict
from metagpt.actions import Action, ActionOutput
from metagpt.logs import logger

TASK_ALLOCATION_PROMPT = """
You are tasked with allocating the following tasks to specific agents according to MLOps pipelines. The detailed data and evaluation information will be given directly to agents later, so you don't have to determine it right now.

# Stakeholder Tasks:
{stakeholder_tasks}

# User Needs:
{user_needs}

# Available Agents:
{agents}

For each task, assign it to the most suitable agent and provide a detailed description of the task. Ensure that the tasks are broken down clearly and include the agent responsible. The tasks should be as detailed as possible and should cover the following aspects:

1. **Task Objective**: A clear description of what the task should achieve. (e.g., "Preprocess the dataset for model training.")
2. **File/Code Requirements**: Specify where the code should be implemented. Include details such as the directory structure, filenames, and the specific functions or classes to be implemented.
    - Example: "Create a new file named `data_preprocessing.py` under `src/data/`. Implement the function `process_data` to handle missing data and normalize the features."
3. **Implementation Details**: Explain in detail how the task should be implemented. Mention specific algorithms, methods, or libraries that should be used. Provide references to existing code, libraries, or standards when relevant.
    - Example: "Use the `pandas` library for data preprocessing and `sklearn.preprocessing.StandardScaler` for feature normalization."
4. **Expected Output**: Describe what the output should look like once the task is completed (e.g., "A cleaned and normalized dataset saved as `data/processed_data.csv`").
5. **Dependencies**: If this task depends on the completion of other tasks, list the dependencies and ensure they are executed in the correct order.
6. **Additional Notes**: Provide any other helpful information, such as references to related documentation, external APIs, or frameworks that can assist in completing the task.

The output MUST be in the following JSON format:

```json
[
    {{
        "task_id": "TASK_1",
        "task_description": "string",
        "assigned_agent": "string",
        "file": "string",
        "details": "string",
        "expected_output": "string",
        "dependencies": ["task_id_1", "task_id_2"],
        "additional_notes": "string"
    }},
    ...
]
"""

class DispatchJob(Action):
    """Generate tasks based on stakeholder tasks, user requirements, and allocate them to specific agents using LLM."""
    
    async def run(self, stakeholder_tasks: List[str], user_needs: str, agents: List[str]) -> ActionOutput:
        """
        Args:
            stakeholder_tasks (List[str]): List of tasks from the stakeholder.
            user_needs (str): Additional requirements provided by the user.
            agents (List[str]): List of agents to whom tasks will be allocated.

        Returns:
            ActionOutput: Contains the generated tasks with agent allocations.
        """
        # 准备 LLM prompt
        prompt = TASK_ALLOCATION_PROMPT.format(
            stakeholder_tasks=stakeholder_tasks,
            user_needs=user_needs,
            agents=agents
        )
        
        llm_response = await self.llm.aask(prompt)


        tasks = json.loads(llm_response)
        logger.info(f"Generated tasks with LLM: {tasks}")

        # # 保存任务为 JSON 文件
        # with open("generated_tasks_with_llm.json", "w") as task_file:
        #     json.dump(tasks, task_file, indent=4)
        #     logger.info(f"Tasks saved to {task_file}")

        return tasks