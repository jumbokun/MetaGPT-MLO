from __future__ import annotations
import json
from typing import Literal
from pydantic import Field, model_validator
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.actions.write_code_mlops import WriteCode
import os
# Template for generating code
TASK_EXECUTE_PROMPT = """
# Task Instruction
{task_description}

# Task Type
{details}

# Context
You are assigned the following task: {details}

Generate Python code to accomplish the task. Provide only the code without any additional explanations.
"""


class DataEngineer(Role):
    # name: str = "David"
    profile: str = "Data Engineer"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = True
    react_mode: Literal["plan_and_act", "react"] = "plan_and_act"
    max_react_loop: int = 10
    def ensure_directory_exists(self, file_path):
        directory = os.path.dirname(file_path)
        logger.info(directory)
        if directory and not os.path.exists(directory):
            print('making directory %s' % directory)
            os.makedirs(directory)
    @model_validator(mode="after")
    def set_plan_and_tool(self) -> "DataEngineer":
        self._set_react_mode(
            react_mode=self.react_mode,
            max_react_loop=self.max_react_loop,
            auto_run=self.auto_run
        )
        self.use_plan = self.react_mode == "plan_and_act"
        self.set_actions([WriteCode])  # Define specific actions if needed
        self._set_state(0)
        return self

    @property
    def working_memory(self):
        return self.rc.working_memory

    async def _plan_and_act(self) -> Message:
        """first plan, then execute an action sequence, i.e. _think (of a plan) -> _act -> _act -> ... Use llm to come up with the plan dynamically."""

        goal = self.rc.memory.get()[-1].content  # retreive latest user requirement
        # print("goal: " + goal)
        await self.planner.update_plan(goal=goal)
        # print('updated plan')

        # take on tasks until all finished
        while self.planner.current_task:
            task = self.planner.current_task
            logger.info(f"ready to take on task {task}")

            # take on current task
            task_result = await self._act_on_task(task)

            # process the result, such as reviewing, confirming, plan updating
            await self.planner.process_task_result(task_result)

        rsp = self.planner.get_useful_memories()[0]  # return the completed plan as a response

        self.rc.memory.add(rsp)  # add to persistent memory

        return rsp

    async def _act_on_task(self, current_task: Task) -> TaskResult:
        """根据 agent 级别任务生成代码，保存并执行它。"""
        logger.info(f"DataEngineer is working on task: {current_task.instruction}")  # 使用 instruction 代替 task_description

        # 根据任务生成代码
        code = await self._write_code(current_task)
 
        # 保存代码到文件 
        file_path = os.path.join(self.planner.plan.project_path, current_task.file_name)
        logger.info(f"{file_path}")
        self.ensure_directory_exists(file_path)
        with open(file_path, "w") as f:
            f.write(code)
        logger.info(f"DataEngineer saved file: {file_path}")

        # 执行文件
        success = await self._execute_file(file_path)

        # 准备任务结果
        task_result = TaskResult(
            code=code,
            result=f"File saved and executed: {file_path}",
            is_success=success
        )
        return task_result


    async def _write_code(self, current_task: Task) -> str:
        """根据 agent 级别任务使用 LLM 生成代码。"""
        # prompt = TASK_EXECUTE_PROMPT.format(
        #     task_description=current_task.instruction,  # 使用 instruction 代替 task_description
        #     details=current_task.task_type,             # 使用 task_type 作为任务类型说明
        #     # expected_output=current_task.kwargs.get('expected_output', '')  # 获取期望输出
        # )

        # # 使用 LLM 生成代码
        # rsp = await self.llm.aask(prompt)
        # code = CodeParser.parse_code(block=None, text=rsp)  # 从 LLM 响应中提取代码
        todo = self.rc.todo
        plan_status = self.planner.get_plan_status() if self.use_plan else ""

        code = await todo.run(
            instruction = current_task.instruction,
            plan_status = plan_status,
            working_memory = self.working_memory.get()
            # use_reflection=use_reflection,
        )
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
