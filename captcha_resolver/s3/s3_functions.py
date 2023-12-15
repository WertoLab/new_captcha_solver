import uuid

import boto3
import shutil
import os
from captcha_resolver.init import init_s3
import base64

s3 = init_s3()


def get_batch():
    os.mkdir("download_captchas")
    counter = 0
    folder_id = ""
    for key in s3.list_objects(Bucket='capchas-bucket')['Contents']:
        print(key['Key'])
        get_object_response = s3.get_object(Bucket='capchas-bucket', Key=key['Key'])
        if(counter % 2 == 0):
            folder_id = str(uuid.uuid4())
            os.mkdir("download_captchas/"+folder_id)
        with open("download_captchas/"+folder_id+"/" + key['Key'].split("/")[-1][:-4] + ".png", "wb") as fh:
            fh.write(base64.decodebytes(get_object_response['Body'].read()))
        counter += 1
    counter = 0
    shutil.make_archive('captchas', 'zip', 'download_captchas')
    shutil.rmtree("download_captchas")


def put_object_to_s3(new_object_captcha, new_object_icons, content_captcha, content_icons):

    s3.put_object(Bucket='capchas-bucket', Key=new_object_captcha, Body=content_captcha,
                  StorageClass='COLD')
    s3.put_object(Bucket='capchas-bucket', Key=new_object_icons, Body=content_icons,
                  StorageClass='COLD')


def delete_captchas():
    objects = s3.list_objects(Bucket='capchas-bucket', Prefix='captchas/')
    for object in objects['Contents']:
        s3.delete_object(Bucket='capchas-bucket', Key=object['Key'])
    return {"stutus": "deleted"}
