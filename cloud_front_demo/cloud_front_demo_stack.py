from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    Duration
)
from constructs import Construct

class CloudFrontDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        #S3 buckets
        cached_content_bucket = s3.Bucket(
            self,"cachedcontentbucket",
            bucket_name="cachedcontentbuckets3",
            website_index_document="index.html",
            removal_policy=RemovalPolicy.DESTROY
        )

        uncached_content_bucket = s3.Bucket(
            self,"uncachedcontentbucket",
            bucket_name="uncachedcontentbuckets3",
            website_index_document="index.html",
            website_error_document="error.html",  
            block_public_access=s3.BlockPublicAccess(block_public_policy=False),
            removal_policy=RemovalPolicy.DESTROY
        )

        #Allow public access
        uncached_content_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[uncached_content_bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        ))
         #Allow cloud front to access the cached content s3 bucket
        cached_content_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[cached_content_bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
        ))
        #Website Cloudfront distribution
        cloudfront_distribution = cloudfront.CloudFrontWebDistribution(self, "cachedWebsiteDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=cached_content_bucket,
                        origin_access_identity=cloudfront.OriginAccessIdentity(self, 'OAI')
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                            min_ttl=Duration.seconds(1),  
                            default_ttl=Duration.seconds(5),  
                            max_ttl=Duration.seconds(30), 
                            allowed_methods=cloudfront.CloudFrontAllowedMethods.GET_HEAD
                        )
                    ]
                )
            ],
            error_configurations=[
                cloudfront.CfnDistribution.CustomErrorResponseProperty(
                    error_code=403,
                    response_code=200,
                    response_page_path="/error.html"
                )
            ]
        )

        #outputs
        CfnOutput(self,"website cloudfront url", value=cloudfront_distribution.distribution_domain_name)
        CfnOutput(self,"s3bucketwebsiteurl", value=uncached_content_bucket.bucket_website_url)

