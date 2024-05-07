import inspect
import json


class FunctionFactory:

    @staticmethod
    async def run_function(func, name, *args, **kwargs):
        """
        Function factory that runs a given function with specified name and parameters.

        Args:
        - func: The function to be executed.
        - name: Name of the function.
        - args: Positional arguments to be passed to the function.
        - kwargs: Keyword arguments to be passed to the function.

        Returns:
        - The result of executing the function.
        """
        # Check if the function exists
        if not hasattr(func, '__call__'):
            raise TypeError("Invalid function provided.")

        # Print the function name
        print(f"Running function: {name}")

        func_signature = inspect.signature(func)

        args_dict = json.loads(args[0])

        # Create an instance of the Pydantic model using the filtered arguments
        arg_instance = func_signature.parameters['req'].annotation(**args_dict)

        # Execute the function with the argument instance
        result = await func(arg_instance)

        return result

