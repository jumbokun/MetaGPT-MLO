from metagpt.actions.action import Action
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.logs import logger

class FeedbackHuman(Action):
    async def run(self, plan,  **kwargs) -> str:
        """
        Generate improvement suggestions for the provided context.
        """
       
        print("Please review the following update and provide your feedback:")
        print(plan)

        # 从键盘获取人工反馈
        rsp = input("Enter your feedback(N or n for no feedback): ")

        return rsp

