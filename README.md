# Deploy your Simian Web App

After developing and testing your Simian Web App locally, deployment to the web. This involves two main steps:
1. Publishing the app to your audience on Simian Portal
2. Deploying your Simian Web App Python code as a web service on a(ny) backend

For evaluation purposes, a shared Simian Evaluation Portal is readily available.  
For deployment, [Render](https://render.com) offers convenient and free hosting Python code as a web service, directly from GitHub.

# Simian Evaluation Portal
Publishing your Simian Web App:
1. Sign up at [Simian Evaluation Portal](https://evaluate.simiansuite.com/).
1. From your Render deployment (per steps [below](#render-fastapi-web-service-as-simian-web-app-backend)), take note of:  
  The _subdomain_ of your backend deployment under _.onrender.com_  
  The _API Key_ (if configured per instructions in [main.py](main.py))  
1. In [Simian Evaluation Portal](https://evaluate.simiansuite.com/), configure and publish app [here](https://evaluate.simiansuite.com/configure_my_app/) by setting the onrender.com subdomain, the module name under the `apps` directory that you want to deploy (without `.py`, e.g. `hello_world_step_1`), and the (optional) API Key.
1. Start your app via [Simian Evaluation Portal](https://evaluate.simiansuite.com/) and bookmark the app link for direct access.

Notes:  
1. Simian Portal supports app sharing and access management, but app access on [Simian Evaluation Portal](https://evaluate.simiansuite.com/) is restricted to yourself only and solely serves evaluation purposes.  
   Contact [simiansuite.com](https://simiansuite.com/contact-us/) for Simian Portal cloud, and on-premises options.
1. Simian Portal works with a range of backend platforms from docker to Azure, and other cloud providers.
   For evaluation purposes render.com has been chosen because of its convenient deployment path from code on GitHub to a live FastAPI web service, its free entry offering and paid upgrade path, and last but not least because your code remains under your control.

# Deploy to FastAPI web service on Render
Use this repo as a Simian Web App template to deploy a Python [FastAPI](https://fastapi.tiangolo.com) web service on Render.

- Render build information is provided in `render.yaml`.
- Python package installation instructions are provided through `requirements.txt`.
- FastAPI routing,  API key configuration and Simian Web app module configuration is done in `main.py`.
- Simple Simian Web App examples are provided in the apps directory

_**If you fork this repository, you should modify the github project url in this `readme.md` under "Manual steps 1." and "Deploy to Render" button to point to your GitHub repository.**_

Note:
1. The free individual offering from render.com does spin down web services after some period of inactivity (15 minutes at the time of writing). When starting the Simian Web App after such period of inactivity it needs to be spinned up causing a delay of 1 minute or more. Consider upgrading to a paid render.com plan to avoid spinning down.

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
