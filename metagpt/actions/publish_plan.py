from metagpt.actions.action import Action
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.logs import logger


class PublishPlan(Action):
    """
    abstract class for publish sprint plans
    """

