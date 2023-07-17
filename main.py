import csv
import os

import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import asyncio

# class to store scraped data
@dataclass
class Item:
    # define instance variable
    var1: str
    var2: str
    var3: str

# class to scrape data
@dataclass
class Scraper:
    # define instance variable
    ivar1: str = None
    ivar2: str = None

    # define function
    # fetch regular function
    def search_result_fetch(self, url):
        # define headers
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
        }

        # get request
        client = httpx.Client(headers=headers)
        response = client.get(url)
        print(response.text)
        return client, response

    def second_fetch(self, client):
        url = 'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-169&count=25&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_OTHER_ENTRY,keywords:insurance,locationUnion:(geoId:102095887),selectedFilters:(sortBy:List(R)),spellCorrectionEnabled:true)&start=25'
        response = client.get(url)
        print(response)
        print(response.text)

    def get_job_links(self, response):
        tree = HTMLParser(response.text)
        jobs = tree.css('ul.jobs-search__results-list > li')
        print(len(jobs))
        job_links = [job.css_first('a[data-tracking-control-name="public_jobs_jserp-result_search-card"]').attributes.get('href', 'None') for job in jobs]
        print(job_links)

    # parse function
    def get_data(self, response):
        # parse html
        tree = HTMLParser(response.text)

        # select element
        data1 = tree.css_first('li').text()
        data2 = tree.css_first('a').text()
        if tree.css_first('p'):
            data3 = tree.css_first('p').text()
        else:
            data3 = None

        # Conver result into dict form
        item = Item(var1=data1, var2=data2, var3=data3)

        return asdict(item)

    def get_csrf(self, response):
        tree = HTMLParser(response.text)
        csrf = tree.css_first('input[name="loginCsrfParam"]').attributes.get('value', '')
        return csrf

    # write to csv function
    def to_csv(self, datas, filename):
        filepath = os.getcwd() + filename
        if os.path.exists(filepath):
            os.remove(filepath)
        for data in datas:
            with open(filename, 'a', encoding='utf-8') as f:
                headers = ['var1', 'var2', 'var3']
                writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)
                if os.path.exists(filepath):
                    writer.writeheader()
                writer.writerow(data)

    # main function
    def main(self):
        # define targerted url
        keyword = "Insurance"
        location = "San%20Francisco%20County%2C%20California%2C%20United%20States"
        geoId = "100901743"
        trk = "public_jobs_jobs-search-bar_search-submit"
        position = 1
        pageNum = 0

        url = f'https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}&geoId={geoId}&trk={trk}&position={str(position)}&pageNum={str(pageNum)}'

        # main program
        client, response = self.search_result_fetch(url)
        job_links = self.get_job_links(response)

        # csrf = self.get_csrf(response)
        # self.second_fetch(client)
        # self.get_data()

        # datas = self.parse(response)
        # print(datas)
        # self.to_csv(datas, 'result.csv')

if __name__ == '__main__':
    s = Scraper()
    s.main()