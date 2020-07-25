import boto3
import os
from contextlib import closing
from boto3.dynamodb.conditions import Key, Attr
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

def lambda_handler(event, context):
    dynamodb_table = os.environ['DB_TABLE_NAME']
    s3_bucket = os.environ['BUCKET_NAME']

    postId = event["Records"][0]["Sns"]["Message"]

    print("Text to Speech function. Post ID in DynamoDB: " + postId)

    #Retrieving information about the post from DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table)
    postItem = table.query(
        KeyConditionExpression=Key('id').eq(postId)
    )


    text = postItem["Items"][0]["text"]
    voice = postItem["Items"][0]["voice"]

    rest = text

    #Because single invocation of the polly synthesize_speech api can
    # transform text with about 1,500 characters, we are dividing the
    # post into blocks of approximately 1,000 characters.
    textBlocks = []
    while (len(rest) > 1100):
        begin = 0
        end = rest.find(".", 1000)

        if (end == -1):
            end = rest.find(" ", 1000)

        textBlock = rest[begin:end]
        rest = rest[end:]
        textBlocks.append(textBlock)
    textBlocks.append(rest)

    #For each block, invoke Polly API, which will transform text into audio
    polly = boto3.client('polly')
    for textBlock in textBlocks:
        response = polly.synthesize_speech(
            OutputFormat='mp3',
            Text = textBlock,
            VoiceId = voice
        )

        #Save the audio stream returned by Amazon Polly on Lambda's temp
        # directory. If there are multiple text blocks, the audio stream
        # will be combined into a single file.
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join("/tmp/", postId)
                with open(output, "wb") as file:
                    file.write(stream.read())



    s3 = boto3.client('s3')
    s3.upload_file('/tmp/' + postId,
      s3_bucket,
      postId + ".mp3")
    s3.put_object_acl(ACL='public-read',
      Bucket=s3_bucket,
      Key= postId + ".mp3")

    location = s3.get_bucket_location(Bucket=s3_bucket)
    region = location['LocationConstraint']

    # if region is None:
    #    url_begining = "https://s3.amazonaws.com/"
    # else:
    #    url_begining = "https://s3-" + str(region) + ".amazonaws.com/" \

    # url = url_begining \
    #        + str(s3_bucket) \
    #        + "/" \
    #        + str(postId) \
    #        + ".mp3"

    # For China Region
    if region.startswith("cn"):
        url = "https://" + str(s3_bucket) \
                + ".s3." \
                + str(region) \
                + ".amazonaws.com.cn/" \
                + str(postId) \
                + ".mp3"

    else:
        if region is None:
            url_begining = "https://s3.amazonaws.com/"
        else:
            url_begining = "https://s3-" + str(region) + ".amazonaws.com/" \

        url = url_begining \
                + str(s3_bucket) \
                + "/" \
                + str(postId) \
                + ".mp3"

    #Updating the item in DynamoDB
    response = table.update_item(
        Key={'id':postId},
          UpdateExpression=
            "SET #statusAtt = :statusValue, #urlAtt = :urlValue",
          ExpressionAttributeValues=
            {':statusValue': 'UPDATED', ':urlValue': url},
        ExpressionAttributeNames=
          {'#statusAtt': 'status', '#urlAtt': 'url'},
    )

    return
