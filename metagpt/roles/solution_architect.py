from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, model_validator

from metagpt.actions.add_requirement import UserRequirement
from metagpt.actions.di.ask_review import ReviewConst
from metagpt.actions.di.execute_nb_code import ExecuteNbCode
from metagpt.actions.di.write_analysis_code import CheckData, WriteAnalysisCode
from metagpt.logs import logger
from metagpt.prompts.di.write_analysis_code import DATA_INFO
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser

from metagpt.const import REQUIREMENT_FILENAME
from metagpt.utils.file_repository import FileRepository
from metagpt.utils.git_repository import GitRepository
from metagpt.utils.project_repo import ProjectRepo
from pathlib import Path
import shutil

from metagpt.actions.write_prd_MLOps import WritePRD
from metagpt.actions.dispatch_job import DispatchJob  
from metagpt.actions.prepare_documents import PrepareDocuments

class SolutionArchitect(Role):
    name: str = "SolutionArchtect"
    profile: str = "SolutionArchtect"
    goal: str = "Designs system architecture, evaluates technical feasibility, and ensures seamless integration of all system components"
    scrum_profile: str = "Scrum Master"
    MLOps_profile: str = "Solution Architect"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    react_mode: Literal["plan_and_act", "react"] = "react"
    max_react_loop: int = 10  # used for react mode
    user_requirement: str = "Nothing"

    @property
    def working_memory(self):
        return self.rc.working_memory
    @property
    def config(self):
        return self.context.config
    def init_repo(self):
        """在 SolutionArchitect 中初始化项目文件夹和 Git 环境"""
        # 初始化项目路径
        if not self.config.project_path:
            name = self.config.project_name or FileRepository.new_filename()
            path = Path(self.config.workspace.path) / name
        else:
            path = Path(self.config.project_path)
        
        # 如果项目路径已存在且不是增量构建，则删除旧的路径
        if path.exists() and not self.config.inc:
            shutil.rmtree(path)
        
        # 设置项目路径到 config
        self.config.project_path = path
        
        # 初始化 Git 仓库
        self.context.git_repo = GitRepository(local_path=path, auto_init=True)
        self.context.repo = ProjectRepo(self.context.git_repo)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([DispatchJob])
        self._watch([UserRequirement, WritePRD])

    # async def _observe(self, ignore_memory=False) -> int:
    #     """Deal with news"""
    #     return await super()._observe(ignore_memory)

    def _get_agents(self):
        agents = ["DataEngineer", "MLEngineer", "DevOpsEngineer", "DataScientist", "MLEngineer"]
        return agents

    # def visualize_tasks(self, tasks, output_file):
    #     dot = graphviz.Digraph(comment="Task Dependency Graph")

    #     for task in tasks:
    #         task_id = task["task_id"]
    #         task_description = task["task_description"]
            
    #         # 添加节点
    #         dot.node(task_id, label=f"{task_id}\n{task_description}")

    #         # 添加依赖关系
    #         for dep in task.get("dependencies", []):
    #             dot.edge(dep, task_id)

    #     # 保存为文件
    #     dot.render(output_file, format='png')
    #     logger.info(f"Task dependency graph saved to {output_file}.png")
        
    async def _think(self) -> bool:
        """Decide self.rc.todo in think"""
        news = self.rc.news[-1]
        logger.info(f"{self.name} got news, thingking. News from {news.cause_by}, news be like: {news.content[-20:-1]}")

        if news.cause_by == self.rc.watch[0]:
            self.working_memory.add(news)
            # logger.info(f"Get users requirement: {news}")
            self.user_requirement = news
            return False
        
        if news.cause_by == self.rc.watch[1]: 
            self.working_memory.add(news)
            logger.info(f"Stakeholder tasks and MLOps phases received: {news.content}")
            stakeholder_output = json.loads(CodeParser.parse_code(block=None, text=news.content))
            self.core_tasks = stakeholder_output["core_tasks"]
            self.mlops_phases = stakeholder_output["mlops_phases"]  # 可用于后续进一步分析
            
            # 准备执行任务分配
            self.rc.todo = DispatchJob
            return True
        return False

    async def _act(self) -> Message:
        if self.rc.todo == DispatchJob:
            stakeholder_tasks = [task['task'] for task in self.core_tasks] 
            agents = self._get_agents() 

            self.init_repo()
            user_needs = self.get_memories()[0].content  # 获取用户需求

            # 调用 LLM 生成任务分配
            tasks = await DispatchJob().run(stakeholder_tasks=stakeholder_tasks, user_needs=user_needs, agents=agents)
            logger.info(f"Tasks generated: {tasks}")

            # 将任务保存为文件
            tasks_file = Path(self.config.project_path) / "generated_tasks.json"
            with open(tasks_file, "w") as f:
                json.dump(tasks, f, indent=4)

            msg = Message(content=str(tasks), role="solution_architect", cause_by=self.rc.todo)
            return msg