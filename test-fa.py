from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
    aws_iam as iam,
    Duration,
    aws_cloudfront_origins as origins
)
from constructs import Construct

class CloudFrontDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # S3 buckets
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

        # Allow public access to the uncached content bucket
        uncached_content_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[uncached_content_bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        ))

        # Allow CloudFront to access the cached content S3 bucket
        cached_content_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[cached_content_bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
        ))

        #Origin Access Identity
        origin_access_identity = cloudfront.OriginAccessIdentity(self, 'OAI')

        # Cache Policy
        cache_policy = cloudfront.CachePolicy.CACHING_OPTIMIZED

        # Website CloudFront distribution
        cloudfront_distribution = cloudfront.Distribution(self, "cachedWebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(cached_content_bucket, origin_access_identity=origin_access_identity),
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cache_policy
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/error.html"
                )
            ]
        )

        # Outputs
        CfnOutput(self, "websiteCloudFrontUrl", value=cloudfront_distribution.distribution_domain_name)
        CfnOutput(self, "s3BucketWebsiteUrl", value=uncached_content_bucket.bucket_website_url)

