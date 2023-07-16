# Integration engineer
Automating integration to 3rd party services

# Requirement
Write an API that will take openapi file in json or yaml as input and generate integration APIs.
The generated code is added to the integration repo.
eg. Input is openapi.yaml for slack. Output is Integration APIs for slack added to the integration repo.

## Process of Integration
Given a openapi doc, use tools to generate server-stubs and client stubs. Then we create APIs that
has server functions with input params for client function.

- step 1: Generate server-stubs
  ```python
  def slack_serverside(params):
    pass
  ```

- step 2: Generate client-stubs
  ```python
  def slack_clientside(params):
    ...
    pass
  ```

- step 3: Incorporate client-side function in server-side function. 
  To create integration service to slack, call corresponding clint function inside server side function
  ```python
  def slack_serverside(params):
    return slack_clientside(params)
  ```

- step 4: Create an API to use slack_serverside func
  ```python
  from fastapi import APIRouter

  router = APIRouter()

  @router.post("/path")
  async def slack_serverside(params):
      return slack_serverside(params)
  ```

Connection to 3rd party APIs involve api-key that will be specific to the user. User will enable integration to a service
by giving their api-key for the service. 
Integration repo is multi-tenant. It is able to identify a user and store user api-keys for integrated services
```python
from fastapi import APIRouter
  
router = APIRouter()
  
@router.post("/enable/{service}")
async def enable_service(user, api_key):
  store_api_keys(user, service, api_key)
  return True
```


