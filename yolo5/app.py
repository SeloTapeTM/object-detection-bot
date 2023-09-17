import time
from pathlib import Path
from flask import Flask, request, jsonify
from detect import run
import uuid
import yaml
from loguru import logger
import os
import boto3
import logging
from botocore.exceptions import ClientError
import pymongo

# define bucket name
BUCKET_NAME_FILE = os.environ['BUCKET_NAME_FILE']  # images_bucket = os.environ['BUCKET_NAME']
with open(BUCKET_NAME_FILE, 'r') as file:
    images_bucket = file.read().rstrip()

# mongoDB stuff
database_name = "mydb"
collection_name = "predictions"
mongodb_uri = f'mongodb://mongo1:27017,mongo2:27018,mongo3:27019/{database_name}?replicaSet=myReplicaSet'
client = pymongo.MongoClient(mongodb_uri)
db = client[database_name]
collection = db[collection_name]

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

# Initialize the S3 client
s3 = boto3.client('s3')

app = Flask(__name__)


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


@app.route('/predict', methods=['POST'])
def predict():
    # Generates a UUID for this current prediction HTTP request. This id can be used as a reference in logs to
    # identify and track individual prediction requests.
    prediction_id = str(uuid.uuid4())

    logger.info(f'prediction: {prediction_id}. start processing')

    # Receives a URL parameter representing the image to download from S3
    img_name = request.args.get('imgName')

    # TODO download img_name from S3, store the local image path in original_img_path
    #  The bucket name should be provided as an env var BUCKET_NAME.
    filename = img_name.split('/')[-1]  # Get the filename alone as srt
    local_dir = 'photos/'  # str of dir to save to
    os.makedirs(local_dir, exist_ok=True)  # make sure the dir exists
    original_img_path = local_dir + filename  # assign the full path of the file to download
    s3.download_file(images_bucket, img_name, original_img_path)  # download the file

    logger.info(f'prediction id: {prediction_id}, path: \"{original_img_path}\" Download img completed')

    # Predicts the objects in the image
    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=original_img_path,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction: {prediction_id}, path: {original_img_path}. done')

    # This is the path for the predicted image with labels The predicted image typically includes bounding boxes
    # drawn around the detected objects, along with class labels and possibly confidence scores.
    predicted_img_path = f'static/data/{prediction_id}/{filename}'  # predicted_img_path = Path(f'static/data/{prediction_id}/{filename}')  # get the result path
    # TODO Uploads the predicted image (predicted_img_path) to S3 (be careful not to override the original image).
    predicted_img_name = f'predicted_{filename}'  # assign the new name
    os.rename(f'/usr/src/app/static/data/{prediction_id}/{filename}',
              f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}')  # rename the file before upload
    s3_path_to_upload_to = '/'.join(img_name.split('/')[:-1]) + f'/{predicted_img_name}'  # assign the path on s3 as str
    file_to_upload = f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}'  # assign the path locally as str
    upload_response = upload_file(file_to_upload, images_bucket, s3_path_to_upload_to)  # upload the file to same path with new name s3
    if not upload_response:
        raise ClientError
    os.rename(f'/usr/src/app/static/data/{prediction_id}/{predicted_img_name}',
              f'/usr/src/app/static/data/{prediction_id}/{filename}')  # rename the file back after upload

    # Parse prediction labels and create a summary
    filename_no_ext = filename.split('.')[0]
    pred_summary_path = Path(f'static/data/{prediction_id}/labels/{filename_no_ext}.txt')
    logger.info(f'prediction: {prediction_id}, sum path: static/data/{prediction_id}/labels/{filename_no_ext}.txt. done')
    if pred_summary_path.exists():
        with open(pred_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': original_img_path,
            'predicted_img_path': predicted_img_path,
            'labels': labels,
            'time': time.time()
        }

        logger.info(f'prediction: {prediction_id}/{original_img_path}. created prediction summery')
        insert_id = collection.insert_one(prediction_summary)  # TODO store the prediction_summary in MongoDB
        logger.info(f'prediction: {prediction_id}/{original_img_path}. written to mongodb cluster. ID:{insert_id}')
        prediction_summary.pop('_id')
        logger.info(f'prediction: {prediction_id}/{original_img_path}. current pred_sum: {prediction_summary}')
        return prediction_summary
    else:
        return f'prediction: {prediction_id}/{original_img_path}. prediction result not found', 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
