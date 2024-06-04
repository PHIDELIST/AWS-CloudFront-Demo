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
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(block_public_policy=False),
        )

        uncached_content_bucket = s3.Bucket(
            self,"uncachedcontentbucket",
            bucket_name="uncachedcontentbuckets3",
            website_index_document="index.html",
            website_error_document="error.html",  
            block_public_access=s3.BlockPublicAccess(block_public_policy=False),
            removal_policy=RemovalPolicy.DESTROY
        )
        fallback_website_bucket = s3.Bucket(
                self,"fallback_website_bucket",
                bucket_name="fallbackwebsitebuckets3",
                website_index_document="index.html",
                removal_policy=RemovalPolicy.DESTROY,
                block_public_access=s3.BlockPublicAccess(block_public_policy=False),
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
            principals=[iam.AnyPrincipal()],
        ))
        # Allow CloudFront to access the fallback S3 bucket
        fallback_website_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject"],
            resources=[fallback_website_bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        ))
        # Website CloudFront distribution
        cloudfront_distribution = cloudfront.Distribution(self, "cachedWebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.OriginGroup(
                    primary_origin=origins.S3Origin(cached_content_bucket, 
                                       origin_access_identity=cloudfront.OriginAccessIdentity(self, 'OAI')),
                    fallback_origin=origins.S3Origin( fallback_website_bucket, 
                                        origin_access_identity=cloudfront.OriginAccessIdentity(self, 'fallbackAOAI')),
                    fallback_status_codes=[404,500,502,503,504]
                ),
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
                cache_policy= cloudfront.CachePolicy.CACHING_OPTIMIZED,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN
            ),
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/error.html"
                )
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL
        )

        # Outputs
        CfnOutput(self, "websiteCloudFrontUrl", value=cloudfront_distribution.distribution_domain_name)
        CfnOutput(self, "s3BucketWebsiteUrl", value=uncached_content_bucket.bucket_website_url)

