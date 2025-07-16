import boto3
import json
import datetime
import os

def detect_idle_ec2():
    ec2 = boto3.client('ec2')
    instances = ec2.describe_instances()
    idle = []
    for r in instances['Reservations']:
        for i in r['Instances']:
            if i['State']['Name'] == 'stopped':
                idle.append({
                    'InstanceId': i['InstanceId'],
                    'State': i['State']['Name'],
                    'Tags': i.get('Tags', [])
                })
    return idle

def detect_unattached_volumes():
    ec2 = boto3.client('ec2')
    vols = ec2.describe_volumes(Filters=[
        {'Name': 'status', 'Values': ['available']}
    ])
    return [{'VolumeId': v['VolumeId'], 'Size': v['Size']} for v in vols['Volumes']]

def detect_unused_eips():
    ec2 = boto3.client('ec2')
    eips = ec2.describe_addresses()
    return [e['PublicIp'] for e in eips['Addresses'] if 'InstanceId' not in e]

def detect_empty_buckets():
    s3 = boto3.client('s3')
    result = []
    buckets = s3.list_buckets()['Buckets']
    for b in buckets:
        try:
            name = b['Name']
            objs = s3.list_objects_v2(Bucket=name)
            if objs.get('KeyCount', 0) == 0:
                result.append(name)
        except Exception:
            continue
    return result

def lambda_handler(event, context):
    report = {
        "IdleEC2Instances": detect_idle_ec2(),
        "UnattachedVolumes": detect_unattached_volumes(),
        "UnusedEIPs": detect_unused_eips(),
        "EmptyS3Buckets": detect_empty_buckets(),
        "GeneratedAt": datetime.datetime.utcnow().isoformat()
    }

    print(json.dumps(report, indent=2))  # Logs to CloudWatch

    if os.environ.get("S3_BUCKET"):
        s3 = boto3.c

