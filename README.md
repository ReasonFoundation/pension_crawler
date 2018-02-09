# Pension Crawler

Crawler for finding public pension web sites for financial and actuarial reports using Google and Bing.

This crawler is built using the following technologies:

- [Scrapy](https://doc.scrapy.org/en/latest/)
- [Scrapyd](https://scrapyd.readthedocs.io/en/stable/)
- [Google Custom Search API](https://developers.google.com/custom-search/)
- [Bing Web Search API](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/)

This crawler contains 2 spiders:

- google
- bing

Bellow are the datapoints extracted from search engine results:

- search query
- total estimated results
- result url
- result title
- result snippet

***IMPORTANT!*** The environment variables containing Google and Bing API keys are located in the secrets file and should be changed when running in production.

### Running localy

This project includes provisioning and deployment scripts for running the crawlers locally on a Debian based server. After the project is deployed we can control the spiders using [Scrapy CLI](https://doc.scrapy.org/en/latest/topics/commands.html).

The input for the spiders is a CSV file located at the data directory named input.csv. To start the crawl process run the following commands:

```
scrapy crawl <spider-name>
```

You should start seeing scrapy logs after command execution.

During the crawl process PDF files from result links are downloaded to data/spider-name/downloads/full folder. After the crawl process is finished the results are saved to an CSV output file named output.csv located in data/spider-name. The CSV file contains paths to dowloaded PDFs per result.

Make sure you are running python 3.5 or above. Running python 2.7, for instance, will cause errors like ImportError among others.

For Mac users, refer to this link: https://apple.stackexchange.com/questions/106778/how-do-i-set-environment-variables-on-os-x with how to set environmental variables. Another approach would be to directly hardcode it in either the google or bing folder's settings.py file.

### Deployment

This project includes provisioning and deployment scripts for running the crawlers remotely on a Debian based server. After the project is deployed we can control spiders using [Scrapyd HTTP API](https://scrapyd.readthedocs.io/en/stable/api.html).

**Important!** This setup has been tested on [Digital Ocean](https://www.digitalocean.com/) servers and may vary when other servers are used.

To provision the server login as root:

```
ssh root@<ip-address>
```

To start the deployment process clone this repo from the command line change directory to deployment folder and execute the provision.sh script:

```
git clone https://github.com/ReasonFoundation/pension_crawler.git
cd pension_crawler/deployment
sudo ./provision.sh
```

After the script is finished you should be able to access Scrapyd jobs endpoint at the following url:
http://server-ip:6800/jobs

To schedule a job remotely issue an HTTP POST request to the following endpoint with the following data. Example using curl:

```
curl http://<server-ip>:6800/schedule.json -d project=pension_crawler -d spider=<spider-name>
```

For more info on scheduling jobs visit Scrapyd [documentation](https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json)

The scraped items and logs can be viewed from Scrapyd web interface located at http://server-ip:6800/jobs.
