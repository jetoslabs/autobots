# Code Structure

Each folder in Autobots represent a Service
(Service here refers to distinct feature of Autobots)

./x
|-> x_orm_model.py (orm model definition)
|-> x_crud.py (orm operation)
|-> x_pydantic_model.py (pydantic model definition)
|-> x.py (functionality)
|-> x_users.py (multi-tenant wrapper over functionality)
|-> x_service.py (contract x provides to the world)

./y => should use only x_service.py from folder x


Common:
./core
./conn
./api