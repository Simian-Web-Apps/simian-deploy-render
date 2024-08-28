import glob
from os import getenv
from os import path
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from simian.entrypoint import entry_point_deploy
import apps  # noqa: F401

# Hello world example of deployment of a Simian Web App using fastapi.
# With optional API Key authentication between Simian Portal and Backend Server where the Python
# Simian apps run as FastAPI web service. In Simian Portal configure back-end type `python_fastapi`.
#
# Enable basic API Key based authentication to prevent anonymous access.
# Backend server: set environment var "SIMIAN_API_KEY_AUTH_ENABLED" to "1" or "true" to enable
#
# When API Key Authentication is enabled, it must be configured in Simian Portal and on the
# Backend Server (where the Python code is deployed).
#
# SIMIAN Portal: configure "Simian-Api-Key" header in Simian Portal under cURL options:
# Add CURLOPT_HTTPHEADER of type array and add name:value. E.g. Simian-Api-Key:abcdefg
#
# Backend Server: set environment variable "SIMIAN_API_KEY", on many platforms labeled "secret".

# Folder next to this file containing simian app modules (and simian app modules only!)
apps_dir = "apps"


def api_key_auth_enabled():
    return getenv("SIMIAN_API_KEY_AUTH_ENABLED", "False").lower() in (
        "true",
        "1",
    )


# Provide basic authentication info, and list the available modules with corresponding routes at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    if api_key_auth_enabled():
        print("SIMIAN:   Basic authentication disabled.")
    else:
        print("SIMIAN:   Basic authentication enabled.")
        print(
            """SIMIAN:   On backend server store api key in environment variable "SIMIAN_API_KEY"."""
        )
        print(
            """SIMIAN:   On Simian Portal configuration set the header "Simian-Api-Key" to the api key."""
        )

    list_apps()
    yield


# Create fastapi object:
# 1. Without default temporary redirect (307) when misssing/extra trailing slash in route
# 2. With lifespan to manage startup behavior
app = FastAPI(redirect_slashes=False, lifespan=lifespan)

# If API Key authentication is enabled add dependency
if api_key_auth_enabled():
    # Very basic security by requiring an api-key to be set in header of request
    # Not implemented here: API Key on server should be hashed (vs stored in clear text).
    header_scheme = APIKeyHeader(name="Simian-Api-Key")

    def api_key_auth(api_key: str = Depends(header_scheme)):
        if not api_key == getenv("SIMIAN_API_KEY"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")

    dependencies = [Depends(api_key_auth)]
else:
    dependencies = []


# Provide root response at webservice startup
@app.head("/", response_class=JSONResponse, dependencies=dependencies)
@app.get("/", response_class=JSONResponse, dependencies=dependencies)
def root_response() -> dict:
    return {"status": "ok"}


# The app is served on the module name path on backend server
@app.post("/{simian_app_slug}", response_class=JSONResponse, dependencies=dependencies)
def route_app_requests(simian_app_slug, request_data: list = Body()) -> dict:
    """Route requests to the Simian App code and return the response."""
    print(simian_app_slug)
    simian_app_slug_parts = simian_app_slug.split("/")
    simian_app_slug_nr_parts = len(simian_app_slug_parts)
    simian_app_route = simian_app_slug_parts[0]
    simian_app_module = simian_app_route.replace("-", "_")
    simian_app_module_exists = module_exists(apps_dir, simian_app_module)

    if simian_app_slug_nr_parts == 1 and simian_app_module_exists:
        return entry_point_deploy(apps_dir + "." + simian_app_module, request_data)
    elif (
        simian_app_slug_nr_parts == 2
        and simian_app_slug_parts[1] == ""
        and simian_app_module_exists
    ):
        raise HTTPException(status_code=404, detail="""Not found, remove trailing "/".""")
    else:
        raise HTTPException(status_code=404, detail="Not found.")


def module_exists(apps_dir, simian_app_module) -> bool:
    return path.isfile(
        path.join(path.dirname(path.realpath(__file__)), apps_dir, simian_app_module + ".py")
    )


def list_apps():
    simian_apps = glob.glob(path.join(path.dirname(path.realpath(__file__)), apps_dir, "*.py"))
    print("SIMIAN:   The apps can be reached using the following routes:")
    for simian_app in simian_apps:
        simian_app_module, _ = path.splitext(path.basename(simian_app))
        simian_app_slug = "/" + simian_app_module.replace("_", "-")
        simian_app_namespace = apps_dir + "." + simian_app_module
        print(f"SIMIAN:   {simian_app_namespace} : {simian_app_slug}")
