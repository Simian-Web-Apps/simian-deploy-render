# Deploy your Simian Web App

After developing and testing your Simian Web App locally, deployment to the web involves two main steps:
1. Publishing the app to your audience on Simian Portal
2. Deploying your Simian Web App Python code as a web service on a(ny) backend

For evaluation purposes, a shared Simian Evaluation Portal is readily available.  
For deployment, [Render](https://render.com) offers convenient and free hosting Python code as a web service, directly from GitHub.

# Exammple app & adding your own
A simple Simian Web App `hello-world.py` example is included in this repository in the `apps` directory.  
The endpoint to this is example is `https://YOUR_SUBDOMAIN.onrender.com/hello-world`

You can simply add your own Simian Web App by adding your module (a python file containing `gui_init` and `gui_event`) to the `apps` directory.  
it is recommended to name your module lower case chracters and underscores when needed. The route to your module will be the base name of your module `.py` file with underscores (`_`) replaced by dashes (`-`).

# Simian Evaluation Portal
Publishing your Simian Web App:
1. Sign up at [Simian Evaluation Portal](https://evaluate.simiansuite.com/).
1. From your Render deployment (per steps [below](#render-fastapi-web-service-as-simian-web-app-backend)), take note of:  
  The _subdomain_ of your backend deployment under _.onrender.com_  
  The _API Key_ (if enabled on the onrender.com webservice)  
1. In [Simian Evaluation Portal](https://evaluate.simiansuite.com/), configure and publish app [here](https://evaluate.simiansuite.com/configure_my_app/).  
   To configure the included `hello_world.py` app, set:
   - `Subdomain` to the subdomain of your `onrender.com web` service.  
     (Subdomain is `abc` if your webservice runs on `abc.onrender.com`.)
   - `Route` to the route to the module under the `apps` directory that you want to deploy: `hello-world` for `hello_world.py`.
     (Route to module is module file name without `.py`, and with `_` replaced by `-`.)
   - Optionally, when API Key authentication is enabled on the onrender webservice, `API Key` to the same value configured in the `SIMIAN_API_KEY` environment varible on the onrender.com web service.
1. Start your app via [Simian Evaluation Portal](https://evaluate.simiansuite.com/).  
   (If you want to bookmark the app for direct access, make sure the bookmark does not contain the `?tab_uuid=...` because that `tab_uuid` identifies a specific instance of the app which is no longer valid after closing the app.)

Notes:  
1. Simian Portal supports app sharing and access management, but app access on [Simian Evaluation Portal](https://evaluate.simiansuite.com/) is restricted to yourself only and solely serves evaluation purposes.  
   Contact [simiansuite.com](https://simiansuite.com/contact-us/) for Simian Portal cloud, and on-premises options.
1. Simian Portal works with a range of backend platforms from docker to Azure, and other cloud providers.
   For evaluation purposes render.com has been chosen because of its convenient deployment path from code on GitHub to a live FastAPI web service, its free entry offering and paid upgrade path, and last but not least because your code remains under your control.

# Deploy to FastAPI web service on Render
Use this repo as a Simian Web App template to deploy a Python [FastAPI](https://fastapi.tiangolo.com) web service on Render.

- Render build information is provided in `render.yaml`.
- Python package installation instructions are provided through `requirements.txt`.
- FastAPI routing and generation of Simian specific startup information in logs is done in `main.py`.
- API key authentication (very basic, not for production usage) is configured by means of environment variables:  
  - To enable set `API_KEY_AUTH_ENABLED` to `1`.  
    When this variable does not exist, or is set to `0` api key authentication is disabled.
  - If api key authentication is enabled, `SIMIAN_API_KEY` must be set to your API Key (lower case letters and numbers only).
  
  ![alt text](readme-images/image.png)

_**If you fork this repository, you should modify the github project url in this `readme.md` both under "Manual steps" step 1, and under "Or simply click" the "Deploy to Render" button to point to your GitHub repository.**_

## Render free plan & web service spin-down
The free individual offering from render.com does spin down web services after some period of inactivity (15 minutes at the time of writing).
When starting the Simian Web App after such period of inactivity it needs to be spinned up causing a delay of 1 minute or more. 

Consider upgrading to a paid render.com plan to avoid spinning down.

Alternatively you could schedule a (cron) job that visits (GET) the root of your webservice every 10 minutes or so.  
For example, with connect-time sufficiently large to allow for spin-up:  

With Authentication:  
```
curl --connect-timeout 300 --header "Simian-Api-Key:YOUR_API_KEY" https://YOUR_SUBDOMAIN.onrender.com/
```  

Without authentication:  
```
curl --connect-timeout 300 https://YOUR_SUBDOMAIN.onrender.com/
```  

## Manual steps
See https://render.com/docs/deploy-fastapi or follow the steps below:

1. You may use this repository directly or [create your own repository from this template](https://github.com/Rolf-MP/simian-render/generate) if you'd like to customize the code.
2. Create a new Web Service on Render.
3. Specify the URL to your new repository or this repository.
4. Render will automatically detect that you are deploying a Python service and use `pip` to download the dependencies.
5. Specify the following as the Start Command.

    ```shell
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```

6. Click Create Web Service.

## Or simply click

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=(https://github.com/Simian-Web-Apps/simian-deploy-render/))

## Thanks
Gratefully forked from [Render Examples - FastAPI](https://github.com/render-examples/fastapi) who thanks [Harish](https://harishgarg.com) for the [inspiration to create a FastAPI quickstart for Render](https://twitter.com/harishkgarg/status/1435084018677010434) and for some sample code!
