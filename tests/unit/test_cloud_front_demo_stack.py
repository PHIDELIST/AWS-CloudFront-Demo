import aws_cdk as core
import aws_cdk.assertions as assertions

from cloud_front_demo.cloud_front_demo_stack import CloudFrontDemoStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cloud_front_demo/cloud_front_demo_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CloudFrontDemoStack(app, "cloud-front-demo")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
