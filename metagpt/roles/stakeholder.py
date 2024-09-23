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
from metagpt.utils.common import CodeParser
from metagpt.actions.write_prd_MLOps import WritePRD


ANALYZE_PROMPT = """
# User Requirement
{user_requirement}

# MLOps Background
You are familiar with Machine Learning Operations (MLOps), which consists of several key phases. Each phase has its own purpose in the overall machine learning lifecycle. Your task is to analyze the user's requirements and align them with the necessary MLOps phases. Below is a brief description of the key MLOps phases:

1. **Data Engineering**: This phase involves extracting, transforming, and loading (ETL) data from various sources. Typical tasks include:
   - Connecting to raw data (e.g., from batch, stream, or cloud storage).
   - Data extraction and cleaning (removing nulls, handling missing values).
   - Data transformation (feature engineering, feature scaling).

2. **Feature Engineering**: In this phase, new features are generated to improve model performance. The tasks include:
   - Defining transformation rules and cleaning rules.
   - Generating new features from the raw data (e.g., calculating derived features).

3. **Model Experimentation**: This phase involves training and validating machine learning models. The tasks include:
   - Data analysis and preparation (splitting datasets, handling imbalanced data).
   - Model training and hyperparameter tuning (finding the best model for the given data).
   - Model validation (assessing the model performance on unseen data).

4. **Automated ML Workflow Pipeline**: Once a model is trained, it needs to be integrated into a pipeline for automated retraining and versioning. The tasks include:
   - Versioning the model and feature data.
   - Scheduling the retraining of the model as new data becomes available.
   - Logging metadata to track the performance and changes to the model.

5. **Model Deployment and Serving**: The final phase involves deploying the model into production and making predictions. The tasks include:
   - Deploying the model to a model serving platform (for online or batch predictions).
   - Monitoring the model's performance in production (e.g., checking for model drift, recalibrating predictions).
   - Integrating continuous feedback loops for model refinement.

# Step 1: Extract Core Tasks
Analyze the provided user requirements and extract the core tasks that the project needs to achieve. Focus on data processing, model training, and result submission.

# Step 2: Align with MLOps Phases
Based on the extracted tasks, identify which phases of MLOps (e.g., data engineering, model experimentation, automated workflow) are required to fulfill the user requirements. For each phase, provide a rationale.

# Output Format:
```json
{{
    "core_tasks": [
        {{"task": "string", "description": "string"}}
    ],
    "mlops_phases": [
        {{"phase": "string", "necessary": true/false, "rationale": "string"}}
    ],
}}
"""

class Stakeholder(Role):
    name: str = "Stakeholder"
    profile: str = "Stakeholder"
    goal: str = "focuses on aligning business goals with technical solutions, and ensures clear communication of business requirements."
    scrum_profile: str = "Product Owner"
    MLOps_profile: str = "Business Stakeholder"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    init: bool = True
    # execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    react_mode: Literal["plan_and_act", "react"] = "react"
    max_react_loop: int = 3  # used for react mode

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([WritePRD])
        self._watch([UserRequirement]) # UserRequirement是Message缺省的cause_by的值


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

            prompt = ANALYZE_PROMPT.format(user_requirement=user_requirement, context=context)
            rsp = await self.llm.aask(prompt)
            rsp_dict = json.loads(CodeParser.parse_code(block=None, text=rsp))
            return Message(content=rsp, role="assistant", cause_by=self.rc.todo)
    
