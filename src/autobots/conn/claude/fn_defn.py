from typing import Dict, Any, List

from pydantic import BaseModel


class AnthropicFunctionDefinitionGen:
    """
    AnthropicFunction class contains methods to create function definitions for Anthropic's assistant.
    """

    @staticmethod
    async def get_defination(func, description: str) -> Dict[str, Any]:
        func_name = func.__name__
        parameters_obj = await AnthropicFunctionDefinitionGen._get_func_parameters(func)
        function_obj = {
            "name": func_name,
            "description": description,
            "input_schema": parameters_obj
        }
        return function_obj
    @staticmethod
    async def _get_func_parameters(func) -> Dict[str, Any]:
        func_parameters = {}
        func_parameter_names = await AnthropicFunctionDefinitionGen._get_func_parameter_names(func)
        for func_parameter_name in func_parameter_names:
            annotation = func.__annotations__[func_parameter_name]
            if issubclass(annotation, BaseModel):
                model_json_schema = annotation.schema()
                func_param = await AnthropicFunctionDefinitionGen._get_func_parameter(model_json_schema)
                func_parameters = func_param  # Since Anthropic currently supports only one parameter
                break
        return func_parameters

    @staticmethod
    async def _get_func_parameter(model_json_schema: Dict[str, Any]) -> Dict[str, Any]:
        param_type = model_json_schema["type"]
        properties = await AnthropicFunctionDefinitionGen._get_properties(model_json_schema)
        required = model_json_schema.get("required")

        parameters_dict = {
            "type": param_type,
            "properties": properties
        }
        if required:
            parameters_dict["required"] = required
        return parameters_dict

    @staticmethod
    async def _get_func_parameter_names(func) -> List[str]:
        params = [key for key in func.__annotations__ if key != "return"]
        return params

    @staticmethod
    async def _get_properties(model_json_schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        properties = {}
        properties_initial_state = model_json_schema["properties"]
        references = model_json_schema.get("$defs", {})
        
        for property_name, property_value in properties_initial_state.items():
            de_referenced_property = await AnthropicFunctionDefinitionGen._get_de_referenced_property(
                references, property_value, property_name
            )
            properties[property_name] = de_referenced_property
        return properties

    @staticmethod
    async def _get_de_referenced_property(references: Dict[str, Any], property_value: Dict[str, Any],
                                          property_name: str) -> Dict[str, Any]:
        expanded_property = property_value
        while "$ref" in expanded_property:
            ref_value = expanded_property["$ref"].split("/")[-1]
            expanded_property = references.get(ref_value, expanded_property)
        return expanded_property
