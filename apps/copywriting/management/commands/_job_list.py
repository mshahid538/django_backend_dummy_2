import requests
import csv
import io
import boto3
import botocore

from django.db.models import Q
from apps.users.models import UserProfile
from backend.settings import (AWS_STORAGE_BUCKET_NAME,
                              AWS_ACCESS_KEY_ID,
                              AWS_SECRET_ACCESS_KEY,
                              )


API_ROOT = 'https://graph.facebook.com/v12.0'
session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')


def my_job():
    get_instagram_account_metric()


def read_metric_aws(filename):
    """
    Looks at aws s3 to see if filename exists. if filename exist, download it
    otherwise, return 'file not found'
    """
    bytes_buffer = io.BytesIO()
    try:
        s3.Bucket(AWS_STORAGE_BUCKET_NAME).download_fileobj(
            Key=filename, Fileobj=bytes_buffer)
    except botocore.exceptions.ClientError as err:
        return 'file not found'

    return bytes_buffer.getvalue().decode()


def write_metric_aws(filename, data):
    """
    Write metric to aws using filename and data
    """
    buff = io.StringIO()
    read_result = read_metric_aws(filename)
    csv_writer = csv.writer(
        buff, dialect='excel', delimiter=',')
    if read_result == 'file not found':
        csv_writer.writerow([data["values"][0]["value"], data["values"][0]["end_time"]])
    else:
        lines = read_result.splitlines()
        for line in lines:
            cells = line.split(',')
            csv_writer.writerow([cells[0], cells[1]])
        csv_writer.writerow([data["values"][0]["value"], data["values"][0]["end_time"]])

    buff2 = io.BytesIO(buff.getvalue().encode())

    s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
        Key=filename, Body=buff2)


def get_instagram_account_metric():
    """
    Get instagram account metric and store it in aws S3.
    """
    result = UserProfile.objects.filter(~Q(ig_id=""))
    metric = "impressions,reach,profile_views"
    period = "day"
    for entry in result:
        username = entry.username
        impression_filename = 'metric/{}/impression.csv'.format(username)
        reach_filename = 'metric/{}/reach.csv'.format(username)
        profile_view_filename = 'metric/{}/profile_views.csv'.format(username)

        response = requests.get(
            '{}/{}/insights?access_token={}&metric={}&period={}'.format(API_ROOT, entry.ig_id, entry.ig_token, metric,
                                                                        period))
        if response.status_code == 200:
            data = response.json()['data']
            write_metric_aws(impression_filename, data[0])
            write_metric_aws(reach_filename, data[1])
            write_metric_aws(profile_view_filename, data[2])
            print("Save instagram account metric successfully")
        else:
            print("error status code: {}".format(response.status_code))
