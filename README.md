AWS Idle Resource Detector (Automated via Lambda)
A lightweight solution to detect and report idle AWS resources using Python, AWS Lambda, and EventBridge (CloudWatch Scheduler). This helps reduce unnecessary cloud costs by identifying unused or underutilized services.

Features
	• Detects:
		○  Stopped EC2 instances
		○  Unattached EBS volumes
		○ Unused Elastic IPs (EIPs)
		○ Empty S3 buckets
	• Outputs structured report in JSON
	• Logs results to CloudWatch Logs
	• Optional: Save reports to S3
	• Scheduled via EventBridge (daily, hourly, etc.)

How It Works
	1. Lambda function written in Python (Boto3)
	2. Scans AWS account for idle resources
	3. Logs report to CloudWatch
	4. (Optional) Uploads report to S3
	5. Scheduled using EventBridge (e.g., daily)

---
Setup Instructions
1. Deploy Lambda

# Zip your Lambda function
```bash
zip function.zip lambda_function.py
```

# Create Lambda role (once)

# Attach policies: AmazonEC2ReadOnlyAccess, AmazonS3FullAccess, CloudWatchLogsFullAccess

# Create the Lambda function
```bash
aws lambda create-function \
  --function-name IdleResourceChecker \
  --runtime python3.12 \
  --role arn:aws:iam::<account-id>:role/LambdaIdleResourceRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 60
```
---
2. Store reports in S3

```bash
aws s3 mb s3://my-idle-reports-bucket
aws lambda update-function-configuration \
  --function-name IdleResourceChecker \
  --environment Variables="{S3_BUCKET=my-idle-reports-bucket}"
```

3. Schedule Daily Run

```bash
aws events put-rule \
  --name DailyIdleCheck \
  --schedule-expression "rate(1 day)"
```

```bash
aws lambda add-permission \
  --function-name IdleResourceChecker \
  --statement-id AllowEventBridgeInvoke \
  --action 'lambda:InvokeFunction' \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:<region>:<account-id>:rule/DailyIdleCheck
```

```bash
aws events put-targets \
  --rule DailyIdleCheck \
  --targets "Id"="1","Arn"="arn:aws:lambda:<region>:<account-id>:function:IdleResourceChecker"
```

Example Output

```json
{
  "IdleEC2Instances": [
    { "InstanceId": "i-123", "State": "stopped" }
  ],
  "UnattachedVolumes": [
    { "VolumeId": "vol-456", "Size": 8 }
  ],
  "UnusedEIPs": ["18.204.12.34"],
  "EmptyS3Buckets": ["my-unused-bucket"],
  "GeneratedAt": "2025-07-15T20:00:00Z"
}

```

---

 Requirements
	• Python 3.8+
	• AWS CLI
	• IAM permissions for EC2, S3, Lambda, CloudWatch, EventBridge

Author Vimbai Muyengwa Cloud FinOps | AWS | Python | Carnegie Mellon University
