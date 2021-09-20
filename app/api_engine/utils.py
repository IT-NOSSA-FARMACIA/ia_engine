from openapi_schema_pydantic import OpenAPI
from openapi_schema_pydantic.util import PydanticSchema, construct_open_api_with_schema_class

import secrets

def generate_token():
    return secrets.token_hex(32)