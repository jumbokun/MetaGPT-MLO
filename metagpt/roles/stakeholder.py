from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, model_validator

from metagpt.actions.action import Action
from metagpt.actions.add_requirement import UserRequirement
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
from metagpt.actions.write_prd_MLOps import WritePRD
from metagpt.actions.review_prd import ReviewPRD, FeedbackHuman

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

SPRINT_THINK_PROMPT = """
# User Requirement
{user_requirement}

# MLOps Background
You are familiar with Machine Learning Operations (MLOps), including project initiation, data engineering pipelines, model experimentation, and automated ML workflow pipelines. Consider these phases as you define and prioritize the project requirements.

# Step 1: Define Clear Requirement Document
Analyze the provided user requirements within the MLOps framework and define a clear requirement document. The document should include the following sections:
1. **Business Objectives**: What are the main business goals that the project aims to achieve?
2. **Functional Requirements**: Based on the MLOps phases (e.g., data engineering, model experimentation, automated workflow), what specific functionalities are required to achieve the business objectives?
3. **Non-Functional Requirements**: Consider performance, security, scalability, compliance, and MLOps-specific requirements such as versioning, monitoring, and CI/CD pipelines.
4. **Constraints and Assumptions**: What constraints (e.g., budget, time, resources) and assumptions (e.g., available data, infrastructure) are associated with the project?

# Step 2: Prioritize the Requirements
Based on the requirement document, prioritize the requirements according to the following MLOps criteria:
1. **Business Value**: How critical is this feature to achieving the business objectives?
2. **Technical Feasibility**: Assess the complexity of implementing this feature within the MLOps framework.
3. **Risks**: Evaluate potential risks (e.g., data quality, model accuracy, deployment issues) associated with the feature.
4. **Dependencies**: Identify dependencies on other tasks, data sources, or system components within the MLOps pipeline.

Provide a prioritized list of requirements, ordered from highest to lowest priority, with a focus on aligning with MLOps best practices.

# Context
{context}

# Output
The output should be structured as follows, please pay attention to the format requirement:
```json
{{
    "requirement_document": {{
        "business_objectives": "string",
        "functional_requirements": ["requirement1", "requirement2", ...],
        "non_functional_requirements": ["requirement1", "requirement2", ...],
        "constraints_assumptions": "string"
    }},
    "prioritized_requirements": [
        {{"requirement": "string", "priority": "high/medium/low", "rationale": "string"}},
        ...
    ]
}}
"""


NEW_REQ_TEMPLATE = """
### Legacy Content
{old_prd}

### New Requirements
{requirements}
"""

test_result = """
{
    "requirement_document": {
        "business_objectives": "The main business goal is to develop an artificial intelligence system that can aid in the detection and classification of degenerative spine conditions using lumbar spine MR images.",
        "functional_requirements": [
            "Classify five lumbar spine degenerative conditions: Left Neural Foraminal Narrowing, Right Neural Foraminal Narrowing, Left Subarticular Stenosis, Right Subarticular Stenosis, and Spinal Canal Stenosis",
            "Provide severity scores (Normal/Mild, Moderate, or Severe) for each of the five conditions across the intervertebral disc levels L1/ L2, L2/L3, L3/L4, L4/L5, and L5/S1"
        ],
        "non_functional_requirements": [
            "The system should be able to process a large dataset of images",
            "The system should provide accurate results in a timely manner"
        ],
        "constraints_assumptions": "The system will be developed using a multi-institutional, expertly curated dataset. The development team will have access to the necessary resources and expertise."
    },
    "prioritized_requirements": [
        {
            "requirement": "Classify five lumbar spine degenerative conditions",
            "priority": "high",
            "rationale": "This is a critical functionality that directly addresses the business objective. It requires significant technical expertise and has high business value."
        },
        {
            "requirement": "Provide severity scores for each of the five conditions across the intervertebral disc levels",
            "priority": "medium",
            "rationale": "This requirement is important for providing accurate results, but it is dependent on the classification functionality. It requires moderate technical expertise and has medium business value."
        },
        {
            "requirement": "The system should be able to process a large dataset of images",
            "priority": "medium",
            "rationale": "This requirement is important for scalability, but it is not directly related to the core functionality. It requires moderate technical expertise and has medium business value."
        },
        {
            "requirement": "The system should provide accurate results in a timely manner",
            "priority": "low",
            "rationale": "This requirement is important for user satisfaction, but it is dependent on other functionalities. It requires low technical expertise and has low business value."
        }
    ]
}
"""



class Stakeholder(Role):
    name: str = "Stakeholder"
    profile: str = "Focuses on aligning business goals with technical solutions, prioritizes ROI, and ensures clear communication of business requirements."
    scrum_profile: str = "Product Owner"
    MLOps_profile: str = "Business Stakeholder"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    init: bool = True
    execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    tools: list[str] = []  # Use special symbol ["<all>"] to indicate use of all registered tools
    tool_recommender: ToolRecommender = None
    react_mode: Literal["plan_and_act", "react"] = "react"
    max_react_loop: int = 10  # used for react mode
    reserved: Action = Field(default=None, exclude=True)
    reviewed: bool = False 

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([WritePRD])
        self._watch([UserRequirement, ReviewPRD, FeedbackHuman]) # UserRequirement是Message缺省的cause_by的值


    @property
    def working_memory(self):
        return self.rc.working_memory
    
    async def _observe(self, ignore_memory=False) -> int:
        """Deal with news"""
        # short memo: you could select n.cause_by from news such that determine what action caused this
        return await super()._observe(ignore_memory)
        

    async def _think(self) -> bool:
        """Decide self.rc.todo in think"""
        news = self.rc.news[-1]
        logger.info(f"{self.name} got news, thingking. News from {news.cause_by}")

        if news.cause_by == self.rc.watch[0]:
            self.rc.todo = WritePRD
            return True
        if news.cause_by == self.rc.watch[1] or news.cause_by == self.rc.watch[2]:
            if not self.reviewed:
                self.rc.todo = WritePRD
                self.working_memory.add(news)
                self.reviewed = True
                return True
            else:
                return False

    async def _act(self) -> Message:
        """Once todo decided in think, act."""
        if self.rc.todo == WritePRD:
            user_requirement = self.get_memories()[0].content
            context = self.working_memory.get()
            # auto gen
            # prompt = SPRINT_THINK_PROMPT.format(user_requirement=user_requirement, context=context)
            # rsp = await self.llm.aask(prompt)
            # FOR TEST ONLY
            rsp = test_result
            print(rsp)
            # TEST ONLY
            # print(rsp)
            # rsp_dict = json.loads(CodeParser.parse_code(block=None, text=rsp))
            return Message(content=rsp, role="assistant", cause_by=self.rc.todo)

    
