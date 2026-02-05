from pydantic import BaseModel, Field
import dspy


class InputModel(BaseModel):
    request_parameters_schema: str = Field(
        description="Define the parameters required for the request as a query. Use this schema specifically to extract and structure the request parameters content in the final output."
    )
    request_body_schema: str = Field(
        description="Provide the schema for the request body. This will be used to extract and structure only the request body content in the final output."
    )
    query: str = Field(
        description="The input query from which the request parameters and request body will be extracted. Ensure that all relevant details for both are captured accurately."
    )


class OutputModel(BaseModel):
    request_parameters: dict = Field(
        default={},
        description="A JSON object containing ONLY request parameters that are EXPLICITLY mentioned in the user's query. Return an empty dict {} if no specific parameter values are mentioned. DO NOT add optional parameters like 'expand', 'limit', or others unless the user specifically asks for them. When in doubt, return empty {}."
    )
    request_body: dict = Field(
        default={},
        description="A JSON object containing ONLY request body fields that are EXPLICITLY mentioned in the user's query. Return an empty dict {} if no specific values are provided. DO NOT guess or infer values. When in doubt, return empty {}."
    )


class RequestSchemaGeneratorSignature(dspy.Signature):
    input: InputModel = dspy.InputField()
    output: OutputModel = dspy.OutputField()
