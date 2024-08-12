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
class SoftwareEngineer(Role):
    name: str = "Software Engineer"
    profile: str = "Implements software solutions, integrates models into systems, and ensures code quality and system reliability."
    scrum_profile: str = "Developper"
    MLOps_profile: str = "Software Engineer"
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
        self._watch([GenerateInitSprintPlan]) 


    @property
    def working_memory(self):
        return self.rc.working_memory
    
    async def _observe(self, ignore_memory=False) -> int:
        """Deal with news"""
        # short memo: you could select n.cause_by from news such that determine what action caused this
        # Read unprocessed messages from the msg buffer.
        news = []
        if self.recovered:
            news = [self.latest_observed_msg] if self.latest_observed_msg else []
        if not news:
            news = self.rc.msg_buffer.pop_all()
        # Store the read messages in your own memory to prevent duplicate processing.
        old_messages = [] if ignore_memory else self.rc.memory.get()
        self.rc.memory.add_batch(news)
        # Filter out messages of interest.
        self.rc.news = [
            n for n in news if (n.cause_by in self.rc.watch or self.name in n.send_to) and n not in old_messages
        ]
        self.latest_observed_msg = self.rc.news[-1] if self.rc.news else None  # record the latest observed msg

        # Design Rules:
        # If you need to further categorize Message objects, you can do so using the Message.set_meta function.
        # msg_buffer is a receiving buffer, avoid adding message data and operations to msg_buffer.
        news_text = [f"{i.role}: {i.content[:20]}..." for i in self.rc.news]
        if news_text:
            logger.debug(f"{self._setting} observed: {news_text}")
        return len(self.rc.news)


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
    
    
