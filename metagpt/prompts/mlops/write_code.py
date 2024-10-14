INTERPRETER_SYSTEM_MSG = """As a data engineer in an MLOps environment, you need to help the user achieve their goal step by step by generating executable Python scripts. Each step will result in a standalone Python file that can be executed in a terminal environment. Ensure that the generated Python code is self-contained, includes necessary imports, and can be executed independently.You will have to handle different types of data, please make sure you know where the data is and what to do with the data. The data could be stored in many forms, make sure you use the proper library to process the data."""

STRUCTUAL_PROMPT = """
# User Requirement
{user_requirement}

# Plan Status
{plan_status}

# Constraints
- Take on Current Task if it is in Plan Status, otherwise, tackle User Requirement directly.
- Ensure the generated code is executable as a standalone Python script file (.py).
- Prioritize using pre-defined libraries and tools where applicable.

# Output
While some concise thoughts are helpful, code is absolutely required.Your response must include Python code that is ready to be saved as a Python script (.py) file. Output only one code block in the following format:

```python
your code
```
"""

REFLECTION_SYSTEM_MSG = """You are an AI Python assistant in an MLOps environment. You will be given your previous Python script implementation, runtime errors, and a hint to appropriately modify the implementation. Write a complete, improved Python script file based on the reflection and ensure it is executable as a standalone file."""

DEBUG_REFLECTION_EXAMPLE = '''
[previous impl]:
assistant:
```python
def add(a: int, b: int) -> int:
   """
   Given integers a and b, return the total value of a and b.
   """
   return a - b
```

user:
Tests failed:
assert add(1, 2) == 3 # output: -1
assert add(1, 3) == 4 # output: -2

[reflection on previous impl]:
The implementation failed the test cases where the input integers are 1 and 2. The issue arises because the code does not add the two integers together, but instead subtracts the second integer from the first. To fix this issue, we should change the operator from `-` to `+` in the return statement. This will ensure that the function returns the correct output for the given input.

[improved impl]:
def add(a: int, b: int) -> int:
   """
   Given integers a and b, return the total value of a and b.
   """
   return a + b
'''

REFLECTION_PROMPT = """
[example]
Here is an example of debugging with reflection.
{debug_example}
[/example]

[context]
{context}

[previous impl]:
{previous_impl}

[instruction]
Analyze your previous code and error in [context] step by step, provide me with improved method and code. Remember to follow [context] requirement. Don't forget to write code for steps behind the error step.
Output a json following the format:
```json
{{
    "reflection": str = "Reflection on previous implementation",
    "improved_impl": str = "Refined code after reflection.",
}}
```
"""

CHECK_DATA_PROMPT = """
# Background
Check latest data info to guide subsequent tasks.

## Finished Tasks
```python
{code_written}
```end

# Task
Check code in finished tasks, print key variables to guide your following actions.
Specifically, if it is a data analysis or machine learning task, print the the latest column information using the following code, with DataFrame variable from 'Finished Tasks' in place of df:
```python
from metagpt.tools.libs.data_preprocess import get_column_info

column_info = get_column_info(df)
print("column_info")
print(column_info)
```end
Otherwise, print out any key variables you see fit. Return an empty string if you think there is no important data to check.

# Constraints:
- Your code is to be added to a new cell in jupyter.

# Instruction
Output code following the format:
```python
your code
```
"""

DATA_INFO = """
# Latest Data Info
Latest data info after previous tasks:
{info}
"""
