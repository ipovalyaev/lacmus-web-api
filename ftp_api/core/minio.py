from minio import Minio
import os
from commons import config
import logging

from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

def bucket_name(id:str): return  'project%s'%id

def get_client():
    return Minio('localhost:9000',
                            access_key=config.MINIO_ACCESS_KEY,
                            secret_key=config.MINIO_SECRET_KEY,
                            secure=False)

def create_project(project_id:str):
    try:
        logging.info("Creating on minio project %s"%bucket_name(project_id))
        minioClient = get_client()
        minioClient.make_bucket(bucket_name(project_id))
    except BucketAlreadyOwnedByYou as err:
        logging.warning("minio returned error BucketAlreadyOwnedByYou, but it's fine")
        pass
    except BucketAlreadyExists as err:
        logging.warning("minio returned error BucketAlreadyExists, but it's fine")
        pass
    except ResponseError as err:
        logging.error("Cann't create minio bucket for project",exc_info=True)
        raise err

def upload_file(project_id:str, file_path:str, file_name: str):
    minioClient = get_client()
    minioClient.fput_object(bucket_name(project_id), file_name, os.path.join(file_path,file_name))
