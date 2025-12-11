import azure.functions as func
from azure.functions.decorators import BlobSource
import logging

from api import app
from api.external_services.blob_storage_service import create_blob_service
from api.config.envs import STORAGE_CONTAINER_NAME, CONFIG_BLOB_NAME, QUERY_BLOB_NAME
from api.config.BlobHolderService import BlobHolderService


app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
blob_holder_service = BlobHolderService()


@app.function_name(name="config_file_update_trigger")
@app.blob_trigger(arg_name="config_file",
                  path=f"{STORAGE_CONTAINER_NAME}/{CONFIG_BLOB_NAME}",
                  connection="AzureWebJobsStorage",
                  source=BlobSource.EVENT_GRID)
def handle_config_file_update(config_file: func.InputStream):
   new_config_file_content = config_file.read().decode("utf-8")

   try:
      blob_holder_service.update_blob_content(CONFIG_BLOB_NAME, new_config_file_content)
      logging.info("Updated config file")
   except Exception as e:
      logging.error(f"Error while updating config file after blob trigger: {e}")


@app.function_name(name="query_file_update_time_trigger")
@app.timer_trigger(schedule="30 * * * * *", 
                   arg_name="functiontimer",
                   run_on_startup=False) 
def test_function(functiontimer: func.TimerRequest) -> None:
   blob_service = create_blob_service()

   try:
      updated_config_file_content = blob_service.download_blob(QUERY_BLOB_NAME).decode('utf-8')
      blob_holder_service.update_blob_content(QUERY_BLOB_NAME, updated_config_file_content)
      logging.info("Updated query file after timer trigger")
   except Exception as e:
      logging.error(f"Error while updating query file after timer trigger: {e}")
