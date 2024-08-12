from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, model_validator

from metagpt.actions.di.ask_review import ReviewConst
from metagpt.actions.di.execute_nb_code import ExecuteNbCode
from metagpt.actions.di.write_analysis_code import CheckData, WriteAnalysisCode
from metagpt.logs import logger
from metagpt.prompts.di.write_analysis_code import DATA_INFO
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.strategy.task_type import TaskType
from metagpt.tools.tool_recommend import BM25ToolRecommender, ToolRecommender
from metagpt.utils.common import CodeParser

REACT_THINK_PROMPT = """
# User Requirement
{user_requirement}
# Context
{context}

Output a json following the format:
```json
{{
    "thoughts": str = "Thoughts on current situation, reflect on how you should proceed to fulfill the user requirement",
    "state": bool = "Decide whether you need to take more actions to complete the user requirement. Return true if you think so. Return false if you think the requirement has been completely fulfilled."
}}
"""

class RequirementEngineer(Role):
    name: str = "RequirementEngineer"
    profile: str = "Responsible for interpreting user requirements and generating subtasks."
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    tools: list[str] = []  # Use special symbol ["<all>"] to indicate use of all registered tools
    tool_recommender: ToolRecommender = None
    react_mode: Literal["plan_and_act", "react"] = "plan_and_act"
    max_react_loop: int = 5  # used for react mode


    @model_validator(mode="after")
    def set_plan_and_tool(self):
        print('set_plan_and_tool!')
        self._set_react_mode(react_mode=self.react_mode, max_react_loop=self.max_react_loop, auto_run=self.auto_run)
        self.use_plan = (
            self.react_mode == "plan_and_act"
        )  # create a flag for convenience, overwrite any passed-in value
        # if self.tools and not self.tool_recommender:
        #     self.tool_recommender = BM25ToolRecommender(tools=self.tools)
        self.set_actions([WriteAnalysisCode])
        self._set_state(0)
        print('end of set_plan_and_tool')
        return self

    @property
    def working_memory(self):
        return self.rc.working_memory

    async def _think(self) -> bool:
        """Useful in 'react' mode. Use LLM to decide whether and what to do next."""
        print('thinking')
        user_requirement = self.get_memories()[0].content
        logger.debug(self.get_memories())
        context = self.working_memory.get()
        logger.debug(context)
        if not context:
            # just started the run, we need action certainly
            self.working_memory.add(self.get_memories()[0])  # add user requirement to working memory
            self._set_state(0)
            return True

        prompt = REACT_THINK_PROMPT.format(user_requirement=user_requirement, context=context)
        rsp = await self.llm.aask(prompt)
        logger.debug(rsp)
        rsp_dict = json.loads(CodeParser.parse_code(block=None, text=rsp))
        self.working_memory.add(Message(content=rsp_dict["thoughts"], role="assistant"))
        need_action = rsp_dict["state"]
        self._set_state(0) if need_action else self._set_state(-1)
        print("need action: " + need_action)
        return need_action

    
    # Override
    async def _plan_and_act(self) -> Message:
        # try:
        #     print('plan invoked')
        #     rsp = await super()._plan_and_act()
        #     await self.execute_code.terminate()
        #     return rsp
        # except Exception as e:
        #     await self.execute_code.terminate()
        #     raise e
        
        """first plan, then execute an action sequence, i.e. _think (of a plan) -> _act -> _act -> ... Use llm to come up with the plan dynamically."""

        # create initial plan and update it until confirmation
        # testing
        goal = self.rc.memory.get()[-1].content  # retreive latest user requirement
        print(goal)
        await self.planner.update_plan(goal=goal)
        print('updated plan')

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