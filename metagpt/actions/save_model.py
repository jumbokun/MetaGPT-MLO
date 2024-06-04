import subprocess
from pathlib import Path
from typing import Tuple

from pydantic import Field

from metagpt.actions.action import Action
from metagpt.logs import logger
from metagpt.schema import SaveModelContext, SaveModelResult
from metagpt.utils.exceptions import handle_exception

SAVE_MODEL_PROMPT = """
Role: You are a senior machine learning engineer, your role is to run the existing code, save the final model as a checkpoint file so that others can directly import it.
Please rewrite the code anyway such that it will save the final result as a checkpoint file.
Here is the code info:
{context}.
Now you should begin your development.
---
## Rewrited code:
Please check the code and rewrite or extend it so that it can save the final training result to a checkpoint file.
## Status:
Determine if all of the code works fine, if so write PASS, else FAIL.
WRITE ONLY ONE WORD, PASS OR FAIL, IN THIS SECTION
## Model File Name:
If the code runs without any bug and the final result i.e. the model can be validated, please write the name of file which saves the model, i.e. the final result in order to push it to the model registry. The file name should be like modelName_time_version.cpt. 
## Send To:
Please write SoftwareEngineer if there are no errors, Engineer if the errors are due to problematic development codes, else SoftwareEngineer,
WRITE ONLY ONE WORD, NoOne OR Engineer OR SoftwareEngineer, IN THIS SECTION.
---
You should fill in necessary instruction, status, model file name and send to, and finally return all content between the --- segment line.
"""


class SaveModel(Action):
    name: str = "SaveModel"
    i_context: SaveModelContext = Field(default_factory=SaveModelContext)


    async def run_script(self, working_directory, additional_python_paths=[], command=[]) -> Tuple[str, str]:
        working_directory = str(working_directory)
        additional_python_paths = [str(path) for path in additional_python_paths]

        # Copy the current environment variables
        env = self.context.new_environ()

        # Modify the PYTHONPATH environment variable
        additional_python_paths = [working_directory] + additional_python_paths
        additional_python_paths = ":".join(additional_python_paths)
        env["PYTHONPATH"] = additional_python_paths + ":" + env.get("PYTHONPATH", "")
        SaveModel._install_dependencies(working_directory=working_directory, env=env)

        # Start the subprocess
        process = subprocess.Popen(
            command, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )
        logger.info(" ".join(command))

        try:
            # Wait for the process to complete, with a timeout
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            logger.info("The command did not complete within the given timeout.")
            process.kill()  # Kill the process if it times out
            stdout, stderr = process.communicate()
        return stdout.decode("utf-8"), stderr.decode("utf-8")

    async def run(self, *args, **kwargs) -> SaveModelResult:
        logger.info(f"Running {' '.join(self.i_context.command)}")
        if self.i_context.mode == "script":
            outs, errs = await self.run_script(
                command=self.i_context.command,
                working_directory=self.i_context.working_directory,
                additional_python_paths=self.i_context.additional_python_paths,
            )
        elif self.i_context.mode == "text":
            outs, errs = await self.run_text(code=self.i_context.code)

        logger.info(f"{outs=}")
        logger.info(f"{errs=}")

        context = TEMPLATE_CONTEXT.format(
            code=self.i_context.code,
            code_file_name=self.i_context.code_filename,
            test_code=self.i_context.test_code,
            test_file_name=self.i_context.test_filename,
            command=" ".join(self.i_context.command),
            outs=outs[:500],  # outs might be long but they are not important, truncate them to avoid token overflow
            errs=errs[:10000],  # truncate errors to avoid token overflow
        )

        prompt = PROMPT_TEMPLATE.format(context=context)
        rsp = await self._aask(prompt)
        return SaveModelResult(summary=rsp, stdout=outs, stderr=errs)

    @staticmethod
    @handle_exception(exception_type=subprocess.CalledProcessError)
    def _install_via_subprocess(cmd, check, cwd, env):
        return subprocess.run(cmd, check=check, cwd=cwd, env=env)

    @staticmethod
    def _install_requirements(working_directory, env):
        file_path = Path(working_directory) / "requirements.txt"
        if not file_path.exists():
            return
        if file_path.stat().st_size == 0:
            return
        install_command = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
        logger.info(" ".join(install_command))
        SaveModel._install_via_subprocess(install_command, check=True, cwd=working_directory, env=env)

    @staticmethod
    def _install_pytest(working_directory, env):
        install_pytest_command = ["python", "-m", "pip", "install", "pytest"]
        logger.info(" ".join(install_pytest_command))
        SaveModel._install_via_subprocess(install_pytest_command, check=True, cwd=working_directory, env=env)

    @staticmethod
    def _install_dependencies(working_directory, env):
        SaveModel._install_requirements(working_directory, env)
        SaveModel._install_pytest(working_directory, env)
