from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, model_validator

from metagpt.actions.action import Action
from metagpt.actions.add_requirement import UserRequirement
from metagpt.actions.di.ask_review import ReviewConst
from metagpt.actions.di.execute_nb_code import ExecuteNbCode
from metagpt.actions.di.write_analysis_code import CheckData, WriteAnalysisCode
from metagpt.logs import logger
from metagpt.prompts.di.write_analysis_code import DATA_INFO
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.strategy.task_type import TaskType
from metagpt.actions.generate_init_sprint_plan import GenerateInitSprintPlan
from metagpt.actions.provide_feedback import ProvideFeedback

class MLEngineer(Role):
    name: str = "ML engineer"
    profile: str = "Integrates and manages ML infrastructure, automates workflows, and monitors models in production to ensure high availability and performance."
    scrum_profile: str = "Developper"
    MLOps_profile: str = "ML engineer"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    tools: list[str] = []  # Use special symbol ["<all>"] to indicate use of all registered tools
    react_mode: Literal["plan_and_act", "react"] = "react"
    max_react_loop: int = 10  # used for react mode

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([ProvideFeedback])
        self._watch([GenerateInitSprintPlan, ]) 


    @property
    def working_memory(self):
        return self.rc.working_memory
    
    async def _observe(self, ignore_memory=False) -> int:
        """Deal with news"""
        # short memo: you could select n.cause_by from news such that determine what action caused this
        return await super()._observe(ignore_memory)
        

    async def _think(self) -> bool:
        """Decide self.rc.todo in think"""
        news = self.rc.news[-1]
        logger.info(f"{self.name} got news, thingking. News from {news.cause_by}")
        
        # provide feedback to sprint plan
        if news.cause_by == self.rc.watch[0]:
            self.working_memory.add(news)
            self.rc.todo = ProvideFeedback
            return True
        


    async def _act(self) -> Message:
        """Once todo decided in think, act."""
        if self.rc.todo == ProvideFeedback:
            context = self.working_memory.get()
            rsp = await self.rc.todo.run(self, context=context, profile=self.profile, role=self.MLOps_profile)
            # print(rsp)
            return Message(content=rsp, role="assistant", cause_by=self.rc.todo)
    
    
