# Pension Crawler

Crawler for finding public pension web sites for financial and actuarial reports using Google and Bing. Checks periodically for new reports on found sites or search engines.

This crawler is built using the following technologies:

- [Scrapy](https://doc.scrapy.org/en/latest/)
- [Scrapyd](https://scrapyd.readthedocs.io/en/stable/)
- [Google Custom Search API](https://developers.google.com/custom-search/)
- [Bing Web Search API](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/)

This crawler contains 3 spiders:

- google
- bing
- sites

Bellow are the data points extracted for google and bing spiders:

- search query
- total estimated results
- result url
- result title
- result snippet

Bellow are the data points extracted for sites spider:

- parent url
- pdf url
- pdf link text

***IMPORTANT!*** The environment variables containing Google and Bing API keys are located in the pension_crawler/secrets.py file and should be changed when running in production.

### Running locally

The data folder is the location where the spider input / output is kept.

There are 3 input folders in the data folder for each spider respectively. Each input folder contains a default file which serves as an entrypoint to the spiders. You can configure the input file for each spider in spider settings file located at pension_crawler/spider-name/settings.py under the settings key: INPUT_FILE.

Alongside the input files there is a blacklist.txt file which controls which domains are filtered when downloading PDFs.

The output folder contains 3 folders as well, where the data from spider runs is saved. Each spider run creates an output file with a timestamp as a file name so that they can be ordered chronologically. The output files are in CSV format and contain the paths to the downloaded PDFs.

There is also an option to disable PDFs download located under pension_crawler/spider-name/settings.py. To disable downloading set the key DOWNLOAD to False.

We can change multiple options in each spider settings.py file. We can configure query modifiers, specific site search, searching by date and crawl depth.

To start the crawl process run the following commands with the default settings run:

```
scrapy crawl <spider-name>
```

You should start seeing scrapy logs after command execution.

To run the spiders with a list of keywords that overrides the keywords from the input file run the following command:

```
scrapy crawl <spider-name> -a keywords='["keyword1", "keyword2"]'
```


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

To set additional arguments for the spider run use:

```
curl http://<server-ip>:6800/schedule.json -d project=pension_crawler -d spider=<spider-name> -d <argument-name>=<argument-value>
```

For example to pass keyword list to google spider use the following command:

```
curl http://<server-ip>:6800/schedule.json -d project=pension_crawler -d spider=google -d keywords='["keyword1", "keyword2"]'
```

For more info on scheduling jobs visit Scrapyd [documentation](https://scrapyd.readthedocs.io/en/stable/api.html#schedule-json)

The scraped items and logs can be viewed from Scrapyd web interface located at http://server-ip:6800/jobs.
