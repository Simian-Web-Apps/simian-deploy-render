import glob
from os import getenv
from os import path

from fastapi import Body, FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from simian.entrypoint import entry_point_deploy
import apps

# Hello world example of deployment of a Simian Web App using fastapi, with API Key authentication
# between Simian Portal and BAckend Server where the Python runs as FastAPI web service.
# In Simian Portal configure back-end type `python_fastapi`.

# Enable basic API Key based authentication to prevent anonymous access.
API_KEY_AUTH_ENABLED = False
# When API Key Authentication is enabled, it must be configured in Simian Portal and on the
# Backend Server (where the Python code is deployed).
# SIMIAN Portal: configure API Key header name and value in Simian Portal under cURL options:
# Add CURLOPT_HTTPHEADER of type array and add name:value. E.g. Simian-Api-Key:abcdefg
API_KEY_HEADER_NAME = "Simian-Api-Key"
# Backend Server: Configure API Key environment variable, on many platforms labeled "secret".
API_KEY_ENV_VAR_NAME = "SIMIAN_API_KEY"

# folder next to this file containing simian app modules (and simian app modules only!)
apps_dir = "apps"

app = FastAPI()

# If API Key authentication is enabled add dependency
if API_KEY_AUTH_ENABLED:
    # Basic security by requiring an api-key to be set in header of request
    header_scheme = APIKeyHeader(name=API_KEY_HEADER_NAME)

    def api_key_auth(api_key: str = Depends(header_scheme)):
        if not api_key == getenv(API_KEY_ENV_VAR_NAME):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")

    dependencies = [Depends(api_key_auth)]
else:
    dependencies = []


def create_endpoint(simian_app_namespace: str):
    def endpoint(request_data: list = Body()) -> dict:
        return entry_point_deploy(simian_app_namespace, request_data)

    return endpoint


# Loop over the .py files in ./apps/ assuming each is a simian app module
simian_apps = glob.glob(path.join(path.dirname(path.realpath(__file__)), apps_dir, "*.py"))
for simian_app in simian_apps:
    simian_app_module, _ = path.splitext(path.basename(simian_app))
    simian_app_slug = "/" + simian_app_module.replace("_", "-")
    simian_app_namespace = apps_dir + "." + simian_app_module

    # See: https://stackoverflow.com/a/78113096 and https://stackoverflow.com/a/76526037
    app.add_api_route(
        simian_app_slug,
        create_endpoint(simian_app_namespace),
        methods=["POST"],
        response_class=JSONResponse,
        dependencies=dependencies,
    )
