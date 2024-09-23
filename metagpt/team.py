#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/12 00:30
@Author  : alexanderwu
@File    : team.py
@Modified By: mashenquan, 2023/11/27. Add an archiving operation after completing the project, as specified in
        Section 2.2.3.3 of RFC 135.
"""

import warnings
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from metagpt.actions import UserRequirement
from metagpt.const import MESSAGE_ROUTE_TO_ALL, SERDESER_PATH
from metagpt.context import Context
from metagpt.environment import Environment
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.utils.common import (
    NoMoneyException,
    read_json_file,
    serialize_decorator,
    write_json_file,
)


class Team(BaseModel):
    """
    Team: Possesses one or more roles (agents), SOP (Standard Operating Procedures), and a env for instant messaging,
    dedicated to env any multi-agent activity, such as collaboratively writing executable code.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    env: Optional[Environment] = None
    investment: float = Field(default=10.0)
    idea: str = Field(default="")

    def __init__(self, context: Context = None, **data: Any):
        super(Team, self).__init__(**data)
        ctx = context or Context()
        if not self.env:
            self.env = Environment(context=ctx)
        else:
            self.env.context = ctx  # The `env` object is allocated by deserialization
        if "roles" in data:
            self.hire(data["roles"])
        if "env_desc" in data:
            self.env.desc = data["env_desc"]

    def serialize(self, stg_path: Path = None):
        stg_path = SERDESER_PATH.joinpath("team") if stg_path is None else stg_path
        team_info_path = stg_path.joinpath("team.json")
        serialized_data = self.model_dump()
        serialized_data["context"] = self.env.context.serialize()

        write_json_file(team_info_path, serialized_data)

    @classmethod
    def deserialize(cls, stg_path: Path, context: Context = None) -> "Team":
        """stg_path = ./storage/team"""
        # recover team_info
        team_info_path = stg_path.joinpath("team.json")
        if not team_info_path.exists():
            raise FileNotFoundError(
                "recover storage meta file `team.json` not exist, " "not to recover and please start a new project."
            )

        team_info: dict = read_json_file(team_info_path)
        ctx = context or Context()
        ctx.deserialize(team_info.pop("context", None))
        team = Team(**team_info, context=ctx)
        return team

    def hire(self, roles: list[Role]):
        """Hire roles to cooperate"""
        self.env.add_roles(roles)

    @property
    def cost_manager(self):
        """Get cost manager"""
        return self.env.context.cost_manager

    def invest(self, investment: float):
        """Invest company. raise NoMoneyException when exceed max_budget."""
        self.investment = investment
        self.cost_manager.max_budget = investment
        logger.info(f"Investment: ${investment}.")

    def _check_balance(self):
        if self.cost_manager.total_cost >= self.cost_manager.max_budget:
            raise NoMoneyException(self.cost_manager.total_cost, f"Insufficient funds: {self.cost_manager.max_budget}")

    def run_project(self, idea, resume: bool = False, send_to: str = ""):
        """Run a project, optionally resuming from the last saved state."""
        if resume:
            # 尝试从上次的断点加载状态
            try:
                with open("workspace/last_run_path.txt", "r") as f:
                    last_run_path = f.read().strip()  # 读取 last_run_path.txt 中保存的路径
                    stg_path = Path(last_run_path)
                    logger.info(f"Loaded last saved workspace path: {stg_path}")
            except FileNotFoundError:
                logger.error("No previous run path found, starting a new project.")
                self._start_new_project(idea, send_to)
                return

            # 尝试从上次的断点加载状态
            if stg_path.exists():
                logger.info("Resuming from last saved state.")
                team = Team.deserialize(stg_path=stg_path)
                self.env = team.env  # 恢复环境
                self.idea = team.idea
            else:
                logger.error(f"Workspace path not found: {stg_path}. Starting a new project.")
                self._start_new_project(idea, send_to)
        else:
            # 创建新的工作区并开始新项目
            self._start_new_project(idea, send_to)


    
    def _start_new_project(self, idea: str, send_to: str):
        """Helper method to start a new project."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workspace_path = Path("workspace") / f"run_{timestamp}"
        workspace_path.mkdir(parents=True, exist_ok=True)

        self.idea = idea

        with open("workspace/last_run_path.txt", "w") as f:
            f.write(str(workspace_path))

        # Human requirement.
        self.env.publish_message(
            Message(role="Human", content=idea, cause_by=UserRequirement, send_to=send_to or MESSAGE_ROUTE_TO_ALL),
        )
        
    @serialize_decorator
    async def run(self, n_round=3, idea="", send_to="", auto_archive=True):
        """Run company until target round or no money"""
        if idea:
            self.run_project(idea=idea, send_to=send_to)

        try:
            with open("workspace/last_run_path.txt", "r") as f:
                last_run_path = f.read().strip()
                workspace_path = Path(last_run_path)
        except FileNotFoundError:
            logger.error("No workspace path found. Exiting.")
            return

        while n_round > 0:
            n_round -= 1
            self._check_balance()
            await self.env.run()

            logger.info(f"Serializing team state to {workspace_path}")
            self.serialize(stg_path=workspace_path)

            logger.debug(f"Rounds remaining: {n_round}")

        # 项目结束后，归档项目历史记录
        self.env.archive(auto_archive)
        return self.env.history
