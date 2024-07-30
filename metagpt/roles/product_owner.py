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
```
"""

REVIEW_THINK_PROMPT = """
# Report
{Report}
# Context
{context}

Output a json following the format:
```json
{{
    "thoughts": str = "Thoughts on current situation, reflect on how you should proceed to fulfill the user requirement",
    "state": bool = "Decide whether you need to take more actions to complete the user requirement. Return true if you think so. Return false if you think the requirement has been completely fulfilled."
}}
```
"""

class StakeHolder(Role):
    name: str = "David"
    profile: str = "StakeHolder"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    tools: list[str] = []  # Use special symbol ["<all>"] to indicate use of all registered tools
    tool_recommender: ToolRecommender = None
    react_mode: Literal["plan_and_act", "react"] = "plan_and_act"
    max_react_loop: int = 10  # used for react mode
    stage = 'init'

    @model_validator(mode="after")
    def set_plan_and_tool(self) -> "Interpreter":
        self._set_react_mode(react_mode=self.react_mode, max_react_loop=self.max_react_loop, auto_run=self.auto_run)
        self.use_plan = (
            self.react_mode == "plan_and_act"
        )  # create a flag for convenience, overwrite any passed-in value
        if self.tools and not self.tool_recommender:
            self.tool_recommender = BM25ToolRecommender(tools=self.tools)
        self.set_actions([WriteAnalysisCode])
        self._set_state(0)
        return self

    @property
    def working_memory(self):
        return self.rc.working_memory

    async def _think(self) -> bool:
        """Useful in 'react' mode. Use LLM to decide whether and what to do next."""
        if self.stage == 'init':
            
        user_requirement = self.get_memories()[0].content
        print(self.get_memories())
        context = self.working_memory.get()
        print(context)
        if not context:
            # just started the run, we need action certainly
            self.working_memory.add(self.get_memories()[0])  # add user requirement to working memory
            self._set_state(0)
            return True

        prompt = REACT_THINK_PROMPT.format(user_requirement=user_requirement, context=context)
        rsp = await self.llm.aask(prompt)
        rsp_dict = json.loads(CodeParser.parse_code(block=None, text=rsp))
        self.working_memory.add(Message(content=rsp_dict["thoughts"], role="assistant"))
        need_action = rsp_dict["state"]
        self._set_state(0) if need_action else self._set_state(-1)

        return need_action

    async def _act(self) -> Message:
        """Useful in 'react' mode. Return a Message conforming to Role._act interface."""
        code, _, _ = await self._write_and_exec_code()
        return Message(content=code, role="assistant", cause_by=WriteAnalysisCode)

    async def _plan_and_act(self) -> Message:
        try:
            rsp = await super()._plan_and_act()
            await self.execute_code.terminate()
            return rsp
        except Exception as e:
            await self.execute_code.terminate()
            raise e

    async def _act_on_task(self, current_task: Task) -> TaskResult:
        """Useful in 'plan_and_act' mode. Wrap the output in a TaskResult for review and confirmation."""
        code, result, is_success = await self._write_and_exec_code()
        task_result = TaskResult(code=code, result=result, is_success=is_success)
        return task_result
    