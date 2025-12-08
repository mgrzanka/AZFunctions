import azure.functions as func
import logging
import requests

from api import app
from api.env import STORAGE_CONTAINER_NAME, CONFIG_BLOB_NAME, API_URI, INTERNAL_SECRET


app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)


@app.function_name(name="config_file_update_trigger")
@app.blob_trigger(arg_name="config_file", 
                  path=f"{STORAGE_CONTAINER_NAME}/{CONFIG_BLOB_NAME}",
                  connection="AzureWebJobsStorage")
def handle_config_file_update(config_file: func.InputStream):
   new_config_file_content = config_file.read().decode("utf-8")

   try:
      response = requests.post(
         url=f"{API_URI}/_internal/config_update",
         headers={"Content-Type": "application/json", "X-Internal-Secret": INTERNAL_SECRET},
         json={"new_config_file_content": new_config_file_content},
      )
      response.raise_for_status()
      logging.info(f"Config file update status: {response.status_code}")
   
   except requests.exceptions.RequestException as e:
      logging.error(f"Error while changing config file: {e}")
