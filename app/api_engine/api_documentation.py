from openapi_schema_pydantic import OpenAPI
from openapi_schema_pydantic.util import (
    PydanticSchema,
    construct_open_api_with_schema_class,
)
from .models import FunctionService
import json


class OpenAPIDoc:
    def __init__(self):
        pass

    @classmethod
    def get_openapi_schema_by_function_service(cls, function_service) -> str:
        exec(function_service.code, globals())
        content_request_body = {}
        content_response = {}
        try:
            content_request_body["application/json"] = {
                "schema": PydanticSchema(schema_class=Request)
            }
        except NameError:
            pass

        try:
            content_response["application/json"] = {
                "schema": PydanticSchema(schema_class=Response)
            }
        except NameError:
            pass

        if function_service.public:
            request_parameters = []
        else:
            request_parameters = [
                {
                    "in": "header",
                    "name": "Api-Key",
                    "schema": {"type": "string", "format": "uuid"},
                    "required": True,
                }
            ]

        if function_service.get_http_method_display() == "GET":
            content_request_body = {}
            try:
                schema_request = json.loads(Request.schema_json())
                properties = schema_request["properties"]
                properties_required = schema_request["required"]
                for key, value in properties.items():
                    print(key, value)
                    request_parameters.append(
                        {
                            "in": "query",
                            "name": key,
                            "schema": {"type": value["type"]},
                            "required": True if key in properties_required else False,
                        }
                    )
            except NameError:
                pass

        open_api_obj = OpenAPI.parse_obj(
            {
                "info": {
                    "title": f"{function_service.name}",
                    "version": "v1",
                    "description": f"{function_service.description}",
                },
                "paths": {
                    f"{function_service.full_url}": {
                        f"{function_service.get_http_method_display().lower()}": {
                            "tags": [function_service.domain.name],
                            "parameters": request_parameters,
                            "requestBody": {"content": content_request_body},
                            "responses": {
                                "200": {
                                    "description": "",
                                    "content": content_response,
                                }
                            },
                        }
                    },
                },
            }
        )
        open_api = construct_open_api_with_schema_class(open_api_obj)
        open_api.openapi = "3.0.0"
        openapi_json = open_api.json(by_alias=True, exclude_none=True, indent=4)
        return openapi_json

    @classmethod
    def get_openapi_schema_by_domain_function_service(cls, domain_function_service):
        function_service_list = FunctionService.objects.filter(
            domain=domain_function_service, active=True
        )

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": f"API's {domain_function_service.name}",
                "description": "",
                "version": "v1",
            },
            "servers": [{"url": "/"}],
            "paths": {},
            "components": {"schemas": {}},
        }

        for function_service in function_service_list:
            function_openapi_schema = json.loads(
                cls.get_openapi_schema_by_function_service(function_service)
            )
            function_path = function_openapi_schema["paths"]
            function_path_key = list(function_path.keys())[0]
            response_content_function = function_path[function_path_key][
                function_service.get_http_method_display().lower()
            ]["responses"]["200"]["content"]

            if response_content_function:
                response_content_function["application/json"]["schema"][
                    "$ref"
                ] = f"#/components/schemas/Response {function_service.name}"

            request_content_function = function_path[function_path_key][
                function_service.get_http_method_display().lower()
            ]["requestBody"]["content"]
            if request_content_function:
                request_content_function["application/json"]["schema"][
                    "$ref"
                ] = f"#/components/schemas/Request {function_service.name}"

                request_function_service = function_openapi_schema["components"][
                    "schemas"
                ]["Request"]
                openapi_schema["components"]["schemas"][
                    f"Request {function_service.name}"
                ] = request_function_service
                openapi_schema["components"]["schemas"][
                    f"Request {function_service.name}"
                ]["title"] = f"Request {function_service.name}"

            response_function_service = function_openapi_schema["components"][
                "schemas"
            ]["Response"]
            openapi_schema["paths"][function_path_key] = function_path[
                function_path_key
            ]
            openapi_schema["components"]["schemas"][
                f"Response {function_service.name}"
            ] = response_function_service
            openapi_schema["components"]["schemas"][
                f"Response {function_service.name}"
            ]["title"] = f"Response {function_service.name}"

        return json.dumps(openapi_schema)

    @classmethod
    def get_openapi_schema_by_team(cls, team):
        function_service_list = FunctionService.objects.filter(team=team, active=True)

        openapi_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": f"API's {team.name.title()}",
                "description": "",
                "version": "v1",
            },
            "servers": [{"url": "/"}],
            "paths": {},
            "components": {"schemas": {}},
        }

        for function_service in function_service_list:
            function_openapi_schema = json.loads(
                cls.get_openapi_schema_by_function_service(function_service)
            )
            function_path = function_openapi_schema["paths"]
            function_path_key = list(function_path.keys())[0]
            response_content_function = function_path[function_path_key][
                function_service.get_http_method_display().lower()
            ]["responses"]["200"]["content"]

            if response_content_function:
                response_content_function["application/json"]["schema"][
                    "$ref"
                ] = f"#/components/schemas/Response {function_service.name}"

            request_content_function = function_path[function_path_key][
                function_service.get_http_method_display().lower()
            ]["requestBody"]["content"]
            if request_content_function:
                request_content_function["application/json"]["schema"][
                    "$ref"
                ] = f"#/components/schemas/Request {function_service.name}"

                request_function_service = function_openapi_schema["components"][
                    "schemas"
                ]["Request"]
                openapi_schema["components"]["schemas"][
                    f"Request {function_service.name}"
                ] = request_function_service
                openapi_schema["components"]["schemas"][
                    f"Request {function_service.name}"
                ]["title"] = f"Request {function_service.name}"

            response_function_service = function_openapi_schema["components"][
                "schemas"
            ]["Response"]
            openapi_schema["paths"][function_path_key] = function_path[
                function_path_key
            ]
            openapi_schema["components"]["schemas"][
                f"Response {function_service.name}"
            ] = response_function_service
            openapi_schema["components"]["schemas"][
                f"Response {function_service.name}"
            ]["title"] = f"Response {function_service.name}"

        return json.dumps(openapi_schema)
