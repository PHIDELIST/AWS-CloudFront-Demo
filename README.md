# Enhancing Website Performance with CDN
![Architecture](<Blank diagram (16).png>)

### Cloudfront Website
![s3website](image.png)

### SE website
![cloudfront](image-1.png)


+ Checking s3 uncached website response time ```curl -w "TTFB: %{time_starttransfer}| Total time: %{time_total} \n" -o /dev/null -vsL http://uncachecontentbuckets3.s3-website-us-east-1.amazonaws.com/```
+ Checking cloudfront respsne ```curl -w "TTFB: %{time_starttransfer}| Total time: %{time_total} \n" -o /dev/null -vsL https://d1zvjexmyq20af.cloudfront.net/```




