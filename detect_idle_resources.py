import boto3
import json

def detect_idle_ec2():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    idle = []

    for r in response['Reservations']:
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
    volumes = ec2.describe_volumes(Filters=[
        {'Name': 'status', 'Values': ['available']}
    ])
    return [{'VolumeId': v['VolumeId'], 'Size': v['Size']} for v in volumes['Volumes']]

def detect_unused_eips():
    ec2 = boto3.client('ec2')
    addresses = ec2.describe_addresses()
    return [a['PublicIp'] for a in addresses['Addresses'] if 'InstanceId' not in a]

def detect_empty_buckets():
    s3 = boto3.client('s3')
    result = []
    buckets = s3.list_buckets()['Buckets']
    for b in buckets:
        name = b['Name']
        try:
            objs = s3.list_objects_v2(Bucket=name)
            if objs.get('KeyCount', 0) == 0:
                result.append(name)
        except Exception:
            continue
    return result

def main():
    report = {
        "IdleEC2Instances": detect_idle_ec2(),
        "UnattachedVolumes": detect_unattached_volumes(),
        "UnusedEIPs": detect_unused_eips(),
        "EmptyS3Buckets": detect_empty_buckets(),
    }

    with open("idle_resources_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Idle resources report saved to idle_resources_report.json")

if __name__ == "__main__":
    main()
