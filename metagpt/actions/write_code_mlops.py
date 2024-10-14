
from metagpt.actions import Action

import json

from metagpt.actions import Action
from metagpt.prompts.mlops.write_code import (
    CHECK_DATA_PROMPT,
    DEBUG_REFLECTION_EXAMPLE,
    INTERPRETER_SYSTEM_MSG,
    REFLECTION_PROMPT,
    REFLECTION_SYSTEM_MSG,
    STRUCTUAL_PROMPT,
)
from metagpt.schema import Message, Plan
from metagpt.utils.common import CodeParser, remove_comments

class WriteCode(Action):
    async def _debug_with_reflection(self, context: list[Message], working_memory: list[Message]):
        """基于反思机制调试代码"""
        reflection_prompt = REFLECTION_PROMPT.format(
            debug_example=DEBUG_REFLECTION_EXAMPLE,
            context=context,
            previous_impl=working_memory,
        )

        rsp = await self._aask(reflection_prompt, system_msgs=[REFLECTION_SYSTEM_MSG])
        print(rsp)
        reflection = json.loads(CodeParser.parse_code(block=None, text=rsp))

        return reflection["improved_impl"]

    async def run(
        self,
        instruction: str,
        plan_status: str = "",
        working_memory: list[Message] = None,
        use_reflection: bool = False,
        **kwargs,
    ) -> str:
        """生成代码"""
        # 使用 STRUCTUAL_PROMPT 来生成代码
        structual_prompt = STRUCTUAL_PROMPT.format(
            user_requirement=instruction,
            plan_status=plan_status,
        )

        working_memory = working_memory or []
        context = self.llm.format_msg([Message(content=structual_prompt, role="user")] + working_memory)

        # 使用 LLM 来生成代码，或调用反思机制进行调试
        if use_reflection:
            code = await self._debug_with_reflection(context=context, working_memory=working_memory)
        else:
            rsp = await self.llm.aask(context, system_msgs=[INTERPRETER_SYSTEM_MSG], **kwargs)
            code = CodeParser.parse_code(block=None, text=rsp)

        return code

    async def _check_data(self, plan: Plan):
        """检查已完成任务中的数据"""
        finished_tasks = plan.get_finished_tasks()
        code_written = [task.code for task in finished_tasks if task.code]
        code_written = "\n\n".join(code_written)

        check_data_prompt = CHECK_DATA_PROMPT.format(code_written=code_written)
        rsp = await self._aask(check_data_prompt)
        code = CodeParser.parse_code(block=None, text=rsp)

        return code