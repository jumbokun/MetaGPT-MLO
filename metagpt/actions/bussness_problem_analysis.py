from __future__ import annotations

import json
from pathlib import Path
from metagpt.schema import BugFixContext, Document, Documents, Message
from metagpt.actions import Action, ActionOutput
from metagpt.actions.action_node import ActionNode
from metagpt.actions.fix_bug import FixBug

from metagpt.schema import Document, Message
from metagpt.utils.common import CodeParser
from metagpt.logs import logger

from metagpt.actions.write_prd_an import (
    COMPETITIVE_QUADRANT_CHART,
    PROJECT_NAME,
    REFINED_PRD_NODE,
    WP_IS_RELATIVE_NODE,
    WP_ISSUE_TYPE_NODE,
    WRITE_PRD_NODE,
)

from metagpt.const import (
    BUGFIX_FILENAME,
    COMPETITIVE_ANALYSIS_FILE_REPO,
    REQUIREMENT_FILENAME,
)

from metagpt.utils.file_repository import FileRepository
from metagpt.utils.mermaid import mermaid_to_file


# 定义提示词
BUSINESS_PROBLEM_ANALYSIS_PROMPT = """
Please analyze the following business problem and define the goal:
User Requirement: {user_requirement}
Plan Status: {plan_status}
Business Context: {business_context}
"""

# TODO: test with gpt4
BUSINESS_PROBLEM_ANALYSIS_SYSTEM_MSG = "Analyze the given business problem and clearly define the goal."

# 定义上下文模板
CONTEXT_TEMPLATE = """
### Project Name
{project_name}

### Description
{description}

### Dataset Description
{dataset_description}

### Evaluation
{evaluation}

### Goals
{goals}
"""

# 定义新需求模板
NEW_REQ_TEMPLATE = """
### Legacy Content
{old_prd}

### New Requirements
{requirements}
"""


class BusinessProblemAnalysis(Action):
    async def run(
        self,
        user_requirement: str,
        plan_status: str = "",
        business_context: str = "",
        working_memory: list[Message] = None,
        **kwargs,
    ) -> ActionOutput | Message:
        analysis_prompt = BUSINESS_PROBLEM_ANALYSIS_PROMPT.format(
            user_requirement=user_requirement,
            plan_status=plan_status,
            business_context=business_context,
        )

        working_memory = working_memory or []
        context = self.llm.format_msg([Message(content=analysis_prompt, role="user")] + working_memory)

        # Logging the start of the business problem analysis
        logger.info(f"Starting business problem analysis for requirement: {user_requirement}")

        # LLM call
        rsp = await self.llm.aask(context, system_msgs=[BUSINESS_PROBLEM_ANALYSIS_SYSTEM_MSG], **kwargs)
        analysis_result = CodeParser.parse_code(block=None, text=rsp)

        # Logging the completion of the business problem analysis
        logger.info(f"Completed business problem analysis for requirement: {user_requirement}")

        return analysis_result


class WritePRD(Action):
    """WritePRD deal with the following situations:
    1. Bugfix: If the requirement is a bugfix, the bugfix document will be generated.
    2. New requirement: If the requirement is a new requirement, the PRD document will be generated.
    3. Requirement update: If the requirement is an update, the PRD document will be updated.
    """

    async def run(self, with_messages, *args, **kwargs) -> ActionOutput | Message:
        """Run the action."""
        req: Document = await self.repo.requirement
        docs: list[Document] = await self.repo.docs.prd.get_all()
        if not req:
            raise FileNotFoundError("No requirement document found.")

        if await self._is_bugfix(req.content):
            logger.info(f"Bugfix detected: {req.content}")
            return await self._handle_bugfix(req)
        # remove bugfix file from last round in case of conflict
        await self.repo.docs.delete(filename=BUGFIX_FILENAME)

        # if requirement is related to other documents, update them, otherwise create a new one
        if related_docs := await self.get_related_docs(req, docs):
            logger.info(f"Requirement update detected: {req.content}")
            return await self._handle_requirement_update(req, related_docs)
        else:
            logger.info(f"New requirement detected: {req.content}")
            return await self._handle_new_requirement(req)

    async def _handle_bugfix(self, req: Document) -> Message:
        # ... bugfix logic ...
        await self.repo.docs.save(filename=BUGFIX_FILENAME, content=req.content)
        await self.repo.docs.save(filename=REQUIREMENT_FILENAME, content="")
        bug_fix = BugFixContext(filename=BUGFIX_FILENAME)
        return Message(
            content=bug_fix.model_dump_json(),
            instruct_content=bug_fix,
            role="",
            cause_by=FixBug,
            sent_from=self,
            send_to="Alex",  # the name of Engineer
        )

    async def _handle_new_requirement(self, req: Document) -> ActionOutput:
        """handle new requirement"""

        # TODO: Fix message transmit
        project_name = self.project_name
        description = "Low back pain is the leading cause of disability worldwide, according to the World Health Organization..."
        dataset_description = "The goal of this competition is to identify medical conditions affecting the lumbar spine in MRI scans..."
        evaluation = "Submissions are evaluated using the average of sample weighted log losses and an any_severe_spinal prediction..."
        goals = "The challenge will focus on the classification of five lumbar spine degenerative conditions..."

        context = CONTEXT_TEMPLATE.format(
            project_name=project_name,
            description=description,
            dataset_description=dataset_description,
            evaluation=evaluation,
            goals=goals
        )

        exclude = [PROJECT_NAME.key] if project_name else []
        node = await WRITE_PRD_NODE.fill(context=context, llm=self.llm, exclude=exclude)  # schema=schema
        await self._rename_workspace(node)
        new_prd_doc = await self.repo.docs.prd.save(
            filename=FileRepository.new_filename() + ".json", content=node.instruct_content.model_dump_json()
        )
        await self._save_competitive_analysis(new_prd_doc)
        await self.repo.resources.prd.save_pdf(doc=new_prd_doc)
        return Documents.from_iterable(documents=[new_prd_doc]).to_action_output()

    async def _handle_requirement_update(self, req: Document, related_docs: list[Document]) -> ActionOutput:
        # ... requirement update logic ...
        for doc in related_docs:
            await self._update_prd(req, doc)
        return Documents.from_iterable(documents=related_docs).to_action_output()

    async def _is_bugfix(self, context: str) -> bool:
        if not self.repo.code_files_exists():
            return False
        node = await WP_ISSUE_TYPE_NODE.fill(context, self.llm)
        return node.get("issue_type") == "BUG"

    async def get_related_docs(self, req: Document, docs: list[Document]) -> list[Document]:
        """get the related documents"""
        # refine: use gather to speed up
        return [i for i in docs if await self._is_related(req, i)]

    async def _is_related(self, req: Document, old_prd: Document) -> bool:
        context = NEW_REQ_TEMPLATE.format(old_prd=old_prd.content, requirements=req.content)
        node = await WP_IS_RELATIVE_NODE.fill(context, self.llm)
        return node.get("is_relative") == "YES"

    async def _merge(self, req: Document, related_doc: Document) -> Document:
        if not self.project_name:
            self.project_name = Path(self.project_path).name
        prompt = NEW_REQ_TEMPLATE.format(requirements=req.content, old_prd=related_doc.content)
        node = await REFINED_PRD_NODE.fill(context=prompt, llm=self.llm, schema=self.prompt_schema)
        related_doc.content = node.instruct_content.model_dump_json()
        await self._rename_workspace(node)
        return related_doc

    async def _update_prd(self, req: Document, prd_doc: Document) -> Document:
        new_prd_doc: Document = await self._merge(req, prd_doc)
        await self.repo.docs.prd.save_doc(doc=new_prd_doc)
        await self._save_competitive_analysis(new_prd_doc)
        await self.repo.resources.prd.save_pdf(doc=new_prd_doc)
        return new_prd_doc

    async def _save_competitive_analysis(self, prd_doc: Document):
        m = json.loads(prd_doc.content)
        quadrant_chart = m.get(COMPETITIVE_QUADRANT_CHART.key)
        if not quadrant_chart:
            return
        pathname = self.repo.workdir / COMPETITIVE_ANALYSIS_FILE_REPO / Path(prd_doc.filename).stem
        pathname.parent.mkdir(parents=True, exist_ok=True)
        await mermaid_to_file(self.config.mermaid.engine, quadrant_chart, pathname)

    async def _rename_workspace(self, prd):
        if not self.project_name:
            if isinstance(prd, (ActionOutput, ActionNode)):
                ws_name = prd.instruct_content.model_dump()["Project Name"]
            else:
                ws_name = CodeParser.parse_str(block="Project Name", text=prd)
            if ws_name:
                self.project_name = ws_name
        self.repo.git_repo.rename_root(self.project_name)
