import re

from pydantic import Field

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import RunCodeContext, RunCodeResult
from metagpt.utils.common import CodeParser

PROMPT_TEMPLATE = """
NOTICE
1. Role: You are a DevOps Engineer;
2. Task: You need to create a model registry which stores the versioned model (checkpoint file) and the performance of it. In order to do that, you are allowed to use not only git but also other solutions you know.
The message is as follows:
# Legacy Code
```python
{code}
```
---
# Unit Test Code
```python
{test_code}
```
---
# Console logs
```text
{logs}
```
---
Now you should start rewriting the code:
## file name of the code to rewrite: Write code with triple quote. Do your best to implement THIS IN ONLY ONE FILE.
"""


class DebugError(Action):
    i_context: RunCodeContext = Field(default_factory=RunCodeContext)

    async def run(self, *args, **kwargs) -> str:
        output_doc = await self.repo.test_outputs.get(filename=self.i_context.output_filename)
        if not output_doc:
            return ""
        output_detail = RunCodeResult.loads(output_doc.content)
        pattern = r"Ran (\d+) tests in ([\d.]+)s\n\nOK"
        matches = re.search(pattern, output_detail.stderr)
        if matches:
            return ""

        logger.info(f"Debug and rewrite {self.i_context.test_filename}")
        code_doc = await self.repo.with_src_path(self.context.src_workspace).srcs.get(
            filename=self.i_context.code_filename
        )
        if not code_doc:
            return ""
        test_doc = await self.repo.tests.get(filename=self.i_context.test_filename)
        if not test_doc:
            return ""
        prompt = PROMPT_TEMPLATE.format(code=code_doc.content, test_code=test_doc.content, logs=output_detail.stderr)

        rsp = await self._aask(prompt)
        code = CodeParser.parse_code(block="", text=rsp)

        return code
