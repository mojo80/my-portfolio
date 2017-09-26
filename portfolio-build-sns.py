import boto3


sns = boto3.resource('sns')

topic = sns.Topic('arn:aws:sns:ap-southeast-2:345005618722:portfolioDeployTopic')

topic.publish(Subject="test @12", Message="testing 123")

