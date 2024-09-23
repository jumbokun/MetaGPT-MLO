from __future__ import annotations
import json
from typing import Literal
from pydantic import Field, model_validator
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser

# Template for generating code
TASK_EXECUTE_PROMPT = """
# Task Description
{task_description}

# Context
You are assigned the following task: {details}
Expected output: {expected_output}

Generate Python code to accomplish the task. Provide only the code without any additional explanations.
"""

class DataEngineer(Role):
    name: str = "David"
    profile: str = "Data Engineer"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    react_mode: Literal["plan_and_act", "react"] = "plan_and_act"
    max_react_loop: int = 10

    @model_validator(mode="after")
    def set_plan_and_tool(self) -> "DataEngineer":
        self._set_react_mode(
            react_mode=self.react_mode,
            max_react_loop=self.max_react_loop,
            auto_run=self.auto_run
        )
        self.use_plan = self.react_mode == "plan_and_act"
        self.set_actions([])  # Define specific actions if needed
        self._set_state(0)
        return self

    @property
    def working_memory(self):
        return self.rc.working_memory

    async def _plan_and_act(self) -> Message:
        """Overrides the base method to ensure proper termination of actions."""
        try:
            rsp = await super()._plan_and_act()
            return rsp
        except Exception as e:
            raise e

    async def _act_on_task(self, current_task: Task) -> TaskResult:
        """Generates code for the task, saves it to a file, and executes it."""
        logger.info(f"DataEngineer is working on task: {current_task.description}")

        # Generate code for the task
        code = await self._write_code(current_task)

        # Save code to file
        file_path = current_task.kwargs.get('file_path', 'output.py')
        with open(file_path, "w") as f:
            f.write(code)
        logger.info(f"DataEngineer saved file: {file_path}")

        # Execute the file
        success = await self._execute_file(file_path)

        # Prepare task result
        task_result = TaskResult(
            code=code,
            result=f"File saved and executed: {file_path}",
            is_success=success
        )
        return task_result

    async def _write_code(self, current_task: Task) -> str:
        """Generates code based on the task using LLM."""
        prompt = TASK_EXECUTE_PROMPT.format(
            task_description=current_task.description,
            details=current_task.content,
            expected_output=current_task.kwargs.get('expected_output', '')
        )

        # Use LLM to generate code
        rsp = await self.llm.aask(prompt)
        code = CodeParser.extract_code(rsp)  # Extract code from LLM response
        return code

    async def _execute_file(self, file_path: str) -> bool:
        """Executes the generated Python file."""
        try:
            exec_globals = {}
            with open(file_path, "r") as f:
                code = f.read()
            exec(code, exec_globals)
            logger.info(f"Executed file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error executing file {file_path}: {e}")
            return False
