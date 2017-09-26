import boto3
import zipfile
import StringIO
import mimetypes


def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:ap-southeast-2:345005618722:portfolioDeployTopic')

    location = {
        "bucketName": 'portfoliobuild.aws.boundarynetworks.com.au',
        "objectKey": 'portfoliobuild.zip'

    }

    try:
        job = event.get("CodePipline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print "building portfolio from " + str(location)
        portfolio_bucket = s3.Bucket('portfolio.aws.boundarynetworks.com.au')
        build_bucket = s3.Bucket(location["bucketName"])

        portfolio_zip = StringIO.StringIO()

        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                mime_type = mimetypes.guess_type(nm)[0]
                print mime_type
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        return "Job Complete!"
        topic.publish(Subject="Porfolio Deployed", Message="Portfolio Deployed Successfully")

        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="Porfolio Deployed Failed", Message="The Build was not successful")
        raise
