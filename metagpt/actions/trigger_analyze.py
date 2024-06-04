
from typing import Optional

import pydantic
from pydantic import model_validator

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message

TRIGGER_ANALYZE = """### Requirements
1. Please read the Project Information, and combine the knowledge of machine learning operations to determine whether the scheduler should adopt which strategy from "trigger when new data available", "event-based" or "periodical".
2. You should write down the reason of your analyze as plain text step by step for other teammates, please remember it is for professionals to read.

You should answer like belows
---
## Trigger Type:
Determine the trigger type from 3 given stragegies. The output should only contain the name of given strategy without double quote.
## Reasons:
Please write down the reason of your choice step by step.
---
You should fill in trigger type and reasons, and finally return all content between the --- segment line.
"""

TRIGGER_ANALYZE_PROMPT = """
### Project Information
{CONTEXT}
"""

class TRIGGER_ANALYZE(Action):
    name: str = ""
    background: Optional[str] = None
    result: str = ""

    async def run(self, context: list[Message], system_text=TRIGGER_ANALYZE) -> str:

        query = context[-1].content
        # logger.debug(query)
        rsp = await self.search_engine.run(query)
        self.result = rsp
        if not rsp:
            logger.error("empty rsp...")
            return ""
        # logger.info(rsp)
        system_prompt = [system_text]
        prompt = system_text.format(
            CONTEXT=self.background,
        )
        result = await self._aask(prompt, system_prompt)
        logger.debug(prompt)
        logger.debug(result)
        return result
