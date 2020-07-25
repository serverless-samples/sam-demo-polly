# sam-demo-polly

## Step 0: Set Environment Variable:

```sh
export suffix=`date +"%Y%m%d"`
```

## Step 1 : Download Demo Code

> Code URL: https://github.com/serverless-samples/sam-demo-polly

## Step 2 : Install SAM CLI

> Guide URL: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html

## Step 3 : SHOW ME THE CODE!

```sh
git clone https://github.com/serverless-samples/sam-demo-polly sam-demo-$suffix
```

## Step 4 : Update Template YAML!

```sh
sed "s/XXXXXX/${suffix}/g" template.yaml > template-${suffix}.yaml
```

## Step 5 : Build it!

```sh
cd sam-demo-$suffix
sam build -t template-${suffix}.yaml --profile sam-demo 
```

## Step 6 : Create S3 Bucket for Lambda Functions!

```sh
aws s3 mb s3://sam-demo-lambda-$suffix --profile sam-demo
```

## Step 7 : Package it!

```sh
sam package --s3-bucket sam-demo-lambda-$suffix --output-template-file package-${suffix}.yaml --profile sam-demo
```

## Step 8 : Deploy it!
```sh
aws cloudformation deploy --template-file package-${suffix}.yaml --stack-name sam-demo-$suffix --capabilities CAPABILITY_NAMED_IAM --profile sam-demo 
```

## Step 9 : What is Missing?


## Step 10 : Upload Website Static Contents 
```sh
cd www
aws s3 sync . s3://sam-demo-web-$suffix/ --acl public-read --profile sam-demo
curl -vv http://sam-demo-web-$suffix.s3-website.cn-northwest-1.amazonaws.com.cn/
```

## Step 11: Why Failing!

## Step 12: Incorrect API URL!

## Step 13: Re-upload it! 
```sh
cd www
aws s3 sync . s3://sam-demo-web-$suffix/ --acl public-read --profile sam-demo
curl -vv http://sam-demo-web-$suffix.s3-website.cn-northwest-1.amazonaws.com.cn/
```

## Step 14: Yes, Success!
