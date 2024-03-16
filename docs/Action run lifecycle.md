# Action Lifecycle
Action is a unit of work.

First App defines Action Type
Then users can create Action

There are 2 State. Action and ActionResult.
Action changes state during Action CRUD.
```
class Action(BaseModel):
    config: Any
```
ActionResult is state associated with running/executing the Action
```
class ActionResult(Action):
    config: Any
    input: Any
    output: Any
```

## Thoughts
Async run:
On Action Run
1. Before run - Create initial ActionResult, status as processing
2. After run - Update to Input and Output of ActionResult, status as Success OR Error
On Action Re-run
Existing Success OR Error ActionResult is the starting point
3. Before re-run - Create initial ActionResult by merging existing Input and Output into Action.config
4. Re-run - Update to Input and Output of ActionResult, status as Success OR Error

## Plan
We can make this more generic:
ActionResult is supplied
Async run/re-run:
1. Before run: Update ActionResult by merging Input and Output (if exist) into Action.config
2. After run: Update to Input and Output of ActionResult, status as Success OR Error

## Design
```python
class ActionData:
    """Action Data"""
    config: dict

class ActionResultData(ActionData):
    """Action Result data"""
    input: dict
    output: dict

class AbstractAction:
    """Abstract implementation of an Action"""
    def __init__(self, action_data: ActionData):
        self.action_data = action_data

    def get_create_type(self):
        raise NotImplementedError
    
    def get_read_type(self):
        raise NotImplementedError

    def get_update_type(self):
        raise NotImplementedError

    def get_delete_type(self):
        raise NotImplementedError
    
    def get_input_type(self):
        raise NotImplementedError
    
    def get_output_type(self):
        raise NotImplementedError
    
    def run(self, action_result: ActionResultData):
        # merging ActionResultData Input and Output (if exist) into ActionData.config
        self.merge_result(action_result.input, action_result.output)
        # self.action_data.config + action_result.input => action_result.output
        raise NotImplementedError
    
    def merge_result(self, prev_input: dict, prev_output: dict):
        """Merge prev_input and prev_output to self.action_data.config"""
        raise NotImplementedError

```
