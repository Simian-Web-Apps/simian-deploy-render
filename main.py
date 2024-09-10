import glob
import logging
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

# Hard-code logging level to INFO for now
logging.basicConfig(level=logging.INFO, format="%(levelname)s:SIMIAN: %(message)s")


def api_key_auth_enabled():
    return getenv("SIMIAN_API_KEY_AUTH_ENABLED", "False").lower() in (
        "true",
        "1",
    )


# Provide basic authentication info, and list the available modules with corresponding routes at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    log_startup_info()
    yield


# FastAPI:
# Without default temporary redirect (307) when misssing/extra trailing slash in route
# With lifespan to manage startup behavior
app = FastAPI(redirect_slashes=False, lifespan=lifespan)

header_scheme = APIKeyHeader(name="Simian-Api-Key", auto_error = False)

async def check_api_key(api_key: str = Depends(header_scheme)):
    # Very basic security by requiring an api-key to be set in header of request if api key auth enabled
    # Not implemented here: API Key on server should be hashed (vs stored in clear text).
    if api_key_auth_enabled():
        if api_key != getenv("SIMIAN_API_KEY"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Forbidden")


# Provide root response at webservice startup
@app.head("/", response_class=JSONResponse, dependencies=[Depends(check_api_key)])
@app.get("/", response_class=JSONResponse, dependencies=[Depends(check_api_key)])
def root_response() -> dict:
    return {"status": "ok"}


# The app is served on the module name path on backend server
@app.post("/{simian_app_slug}", response_class=JSONResponse, dependencies=[Depends(check_api_key)])
def route_app_requests(simian_app_slug, request_data: list = Body()) -> dict:
    """Route requests to the Simian App code and return the response."""
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


# Check if module (constructed from route) exists.
def module_exists(apps_dir, simian_app_module) -> bool:
    return path.isfile(
        path.join(path.dirname(path.realpath(__file__)), apps_dir, simian_app_module + ".py")
    )


# log list of available apps with the corresponding route.
def list_apps():
    simian_apps = glob.glob(path.join(path.dirname(path.realpath(__file__)), apps_dir, "*.py"))
    logging.info("The apps can be reached using the following routes:")
    for simian_app in simian_apps:
        simian_app_module, _ = path.splitext(path.basename(simian_app))
        simian_app_slug = "/" + simian_app_module.replace("_", "-")
        simian_app_namespace = apps_dir + "." + simian_app_module
        logging.info(f"{simian_app_namespace} : {simian_app_slug}")


# log info at startup of FastAPI
def log_startup_info():
    if api_key_auth_enabled():
        logging.info("Basic authentication disabled.")
    else:
        logging.info("Basic authentication enabled.")
        logging.info(
            """On backend server store api key in environment variable "SIMIAN_API_KEY"."""
        )
        logging.info(
            """On Simian Portal configuration set the header "Simian-Api-Key" to the api key."""
        )
    list_apps()
