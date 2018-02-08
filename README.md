# Pension Crawler

Crawler for finding public pension web sites for financial and actuarial reports.

This crawler contains 2 spiders:

- google
- bing

The spiders integrate [Google Custom Search API](https://developers.google.com/custom-search/) and [Bing Web Search API](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/) with [Scrapy](https://doc.scrapy.org/en/latest/) framework.

The input for the spiders is a CSV file located at the data directory named input.csv. To start the crawl process run the following commands:

```
scrapy crawl <spider-name>
```

During the crawl process PDF files from result links are downloaded to downloads/full folder. After the crawl process is finished the results are saved to an CSV output file named output.csv. The CSV file contains paths to dowloaded PDFs per result.

The fields extracted from the search results are:

- search query
- total estimated results
- result url
- result title
- result snippet

# Deployment

To provision and deploy the spider on a Ubuntu based Linux instance run the provision.sh file under root user account. This script installs system and python dependencies and configures Supervisord and Scrapyd. Scrapyd is used as an HTTP API for scheduling spider crawls. To run the provision.sh file execute the folowing command:

```
./provision.sh
```

If not the root user, try the following:

```
sudo chmod +x provision.sh
sudo ./provision.sh
```

To schedule spider run using Scrapyd HTTP API issue the following command:

```
curl http://<server-ip>:6800/schedule.json -d project=pension_crawler -d spider=<spider-name>
```

To check the status of the running tasks visit the following endpoint in a browser: http://<server-ip>:6800/jobs


