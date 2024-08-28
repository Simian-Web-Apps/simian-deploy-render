import glob
from os import getenv
from os import path
from contextlib import asynccontextmanager

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


# Provide basic authentication info, and list the available modules with corresponding routes at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    if API_KEY_AUTH_ENABLED:
        print("SIMIAN:   Basic authentication disabled.")
    else:
        print("SIMIAN:   Basic authentication enabled.")
        print(
            f"""SIMIAN:   On render web service store api key in environment variable "{API_KEY_ENV_VAR_NAME}"."""
        )
        print(
            f"""SIMIAN:   On Simian Portal configuration set the header "{API_KEY_HEADER_NAME}" to the api key."""
        )

    listApps()
    yield


app = FastAPI(redirect_slashes=False, lifespan=lifespan)


# Provide responese at startup
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
    simian_app_module_exists = moduleExists(apps_dir, simian_app_module)

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


def moduleExists(apps_dir, simian_app_module) -> bool:
    return path.isfile(
        path.join(path.dirname(path.realpath(__file__)), apps_dir, simian_app_module + ".py")
    )


def listApps():
    simian_apps = glob.glob(path.join(path.dirname(path.realpath(__file__)), apps_dir, "*.py"))
    print("SIMIAN:   The apps can be reached using the following routes:")
    for simian_app in simian_apps:
        simian_app_module, _ = path.splitext(path.basename(simian_app))
        simian_app_slug = "/" + simian_app_module.replace("_", "-")
        simian_app_namespace = apps_dir + "." + simian_app_module
        print(f"SIMIAN:   {simian_app_namespace} : {simian_app_slug}")
