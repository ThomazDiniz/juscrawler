import pytest_regtest
import crawler

def test_regression_crawler_tjal(regtest):
	result = crawler.crawl("0000269-48.2014.8.02.0024",crawler.TJAL)
	print(result, file=regtest)

def test_regression_crawler_tjce(regtest):
	result = crawler.crawl("0007737-79.2011.8.06.0049",crawler.TJCE)
	print(result, file=regtest)

def test_regression_crawler_tjal_not_found(regtest):
	result = crawler.crawl("11111111-48.2014.8.02.0024",crawler.TJAL)
	print(result, file=regtest)

def test_regression_crawler_tjce_not_found(regtest):
	result = crawler.crawl("1111111-79.2011.8.06.0049",crawler.TJCE)
	print(result, file=regtest)

