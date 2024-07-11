from typing import Optional

import pydantic
from pydantic import model_validator

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.schema import Message

READ_TRAINNING_CODE = """### Requirements
1. Please read the given Code, and combine the knowledge of machine learning operations to determine how should we design the model registry. Consider the following aspects: Initialize the Registry, Register a Model, Version Control, Store Model Artifacts, Tags and Labels. 
2. You should write down the reason of your analyze as plain text step by step for other teammates, please remember it is for professionals to read.

You should answer like belows
---
## Model Registry:
You are a decision maker, so please answer with clear instructions, not just provides options. 
Determine how the programmer should write the Model Registry, while consider using MLFlow as solutions. Please give very clear instructions like how to deliver the model to the model registry, not just overviews.
## Reasons:
Please write down the reason of your choice step by step.
---
You should fill in Model Registry and reasons, and finally return all content between the --- segment line.
"""

READ_TRAINNING_CODE_PROMPT = """
### Code
{CONTEXT}
"""

class READ_TRAINNING_CODE(Action):
    name: str = ""
    background: Optional[str] = None
    result: str = ""

    async def run(self, context: list[Message], system_text=READ_TRAINNING_CODE) -> str:

        code = context[-1].content

        system_prompt = [system_text]
        prompt = READ_TRAINNING_CODE_PROMPT.format(
            CONTEXT=self.code,
        )
        result = await self._aask(prompt, system_prompt)
        logger.debug(prompt)
        logger.debug(result)
        return result
