# import asyncio
# from metagpt.logs import logger
# from metagpt.roles.di.data_interpreter import DataInterpreter
# from metagpt.roles.requirement_engineer import RequirementEngineer
# from metagpt.utils.recovery_util import save_history

# async def main(requirement: str = ""):

#     di = RequirementEngineer()
#     rsp = await di.run(requirement)
#     logger.info(rsp)
#     save_history(role=di)


# if __name__ == "__main__":

#     requirement = "Run data analysis on sklearn Iris dataset, include a plot"
#     asyncio.run(main(requirement))

import json

# 替换为你的文件路径
with open("workspace/run_20240909_025423/team.json", "r", encoding="utf-8") as f:
    data = f.read()
    try:
        json_data = json.loads(data)
        print("JSON is valid")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")