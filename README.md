# Pension Crawler

Crawler for finding public pension web sites for financial and actuarial reports using Google and Bing. Checks periodically for new reports on found sites or search engines.

### Project scope

This project is based on input/output directories. There are 3 input folders in the data folder for each spider respectively. Each input folder contains a default file which serves as an entrypoint to the spiders. You can configure the input file for each spider in spider settings file located at pension_crawler/pension_crawler/spider-name/settings.py under the settings key: INPUT_FILE.

Alongside the input files there is a blacklist.txt file which controls which domains are filtered when downloading PDFs.

The output folder contains 3 folders as well, where the data from spider runs is saved. Each spider run creates an output file with a timestamp as a file name so that they can be ordered chronologically. The output files are in CSV format and contain the paths to the downloaded PDFs.

There is also an option to disable PDFs download located under pension_crawler/pension_crawler/spider-name/settings.py. To disable downloading set the key DOWNLOAD_ENABLED to False.

This crawler is built using the following technologies:

- [Scrapy](https://doc.scrapy.org/en/latest/)
- [Scrapyd](https://scrapyd.readthedocs.io/en/stable/)
- [Google Custom Search API](https://developers.google.com/custom-search/)
- [Bing Web Search API](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/)
- [PyPDF2](https://pythonhosted.org/PyPDF2/)
- [Textract](https://textract.readthedocs.io/)

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
- state
- system
- report_type
- year
- page_count

Bellow are the data points extracted for sites spider:

- parent url
- pdf url
- pdf link text
- state
- system
- report_type
- year
- page_count

***IMPORTANT!*** The environment variables containing Google and Bing API keys are located in the pension_crawler/pension_crawler/spider-name/settings.py file and should be changed when running in production.

### PDF text extraction

This project uses 2 PDF extraction methods. The PDF files are downloaded and analyzed asynchronous.

The first library used is PyPDF2 which extracts text from text based PDF files. The fallback option is textract which uses tesseract in the background to extract text using OCR.

The first found year is extracted using REGEX and is stored in the CSV output.

### Running locally

This project includes provisioning and deployment scripts for running the crawlers localy on a Debian based systems. One of the scripts should be run as root/sudo user and the other one as normal user!

For Mac users, make sure you have [homebrew](https://brew.sh/) installed. This is needed in order to install all the necessary dependencies of Textract. More details about that in this [link](http://textract.readthedocs.io/en/latest/installation.html). It has a guide for Mac, Ubuntu/Debian, and other OS'.

To start the deployment process clone this repo from the command line, change directory to deployment folder and execute the as_root.sh and as_user.sh scripts:

```
git clone https://github.com/ReasonFoundation/pension_crawler.git
cd pension_crawler/deployment
sudo ./as_root.sh
./as_user.sh
```

After the script is finished, change the Google and Bing API keys in pension_crawler/pension_crawler/spider-name/settings.py.  Then you should be able to run scrapy cli commands. To start the crawl process run the following commands with the default settings:

```
scrapy crawl <spider-name>
```

You should start seeing scrapy logs after command execution.
