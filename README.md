## HTML to PDF converter and URL shortener

Deploy with `Serverless` framework to AWS Lambda. Written using Flask and Python 3.8.

Endpoints:
- ```POST /htmlToPdf/ Body: `url` or `file` ```
- ```POST /newUrl/ Body: `url` ```
- ```GET /r/<url_id>```
