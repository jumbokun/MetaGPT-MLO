from metagpt.actions.action import Action
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.logs import logger

REVIEW_PRD_PROMPT = """
# current conversation 
{context}

# Task
You are a senior {role}, who {profile}

Provide your opinion on the current conversation in a free format, but keep it as short as possible.
"""

class ProvideFeedback(Action):
    async def run(self, context, profile, role, **kwargs) -> str:
        """
        Generate .
        :return: JSON string containing improvement suggestions.
        """
        prompt = REVIEW_PRD_PROMPT.format(context=context, profile=profile, role=role)
        response = await self.llm.aask(prompt)
        return response

