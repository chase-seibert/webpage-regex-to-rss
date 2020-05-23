#!/usr/bin/env python3

import sys

import boto3


if __name__ == '__main__':

    try:
        file_name, bucket, object_name = sys.argv[1], sys.argv[2], sys.argv[3]
    except IndexError:
        print('Usage: ./upload_s3.py FILE BUCKET OBJECT_NAME')
        exit(1)

    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={
        'ContentType': 'text/xml',
        'ACL': 'public-read',
    })
