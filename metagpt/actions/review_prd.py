from metagpt.actions.action import Action
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.logs import logger

REVIEW_PRD_PROMPT = """
# Business Requirement Document
{user_requirement}

# Current Plan
{plan}

# Change log
{change_log}

# Task
As a solution architect working in Machine Learning area, review the provided plan.

Provide your suggestions in a free format, but keep it short.

Check the change log, if there is already nothing important need to change.
"""

class ReviewPRD(Action):
    async def run(self, plan, user_requirement, change_log, **kwargs) -> str:
        """
        Generate improvement suggestions for the provided business requirement document.
        :return: JSON string containing improvement suggestions.
        """
        prompt = REVIEW_PRD_PROMPT.format(user_requirement=user_requirement, plan=plan, change_log=change_log)
        # logger.info(prompt)
        response = await self.llm.aask(prompt)
        # logger.info(response)
        # suggestions = CodeParser.parse_code(block=None, text=response)
        # logger.info(suggestions)
        return response

class FeedbackHuman(Action):
    async def run(self, plan,  **kwargs) -> str:
        """
        Generate improvement suggestions for the provided business requirement document.
        :return: JSON string containing improvement suggestions.
        """
       
        print("Please review the following update and provide your feedback:")
        print(plan)

        # 从键盘获取人工反馈
        rsp = input("Enter your feedback:")

        return rsp

