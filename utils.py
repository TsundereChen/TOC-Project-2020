from newsapi import NewsApiClient
from config import newsapi_apikey

newsapi = NewsApiClient(api_key=newsapi_apikey)

def generateQueryString(coin, queryType):
    if queryType == "latest":
        return 'select last("' + str(coin) + '") from coinmarketcap.autogen.price'
    if queryType == "historical":
        return 'select last("' + str(coin) + '") from coinmarketcap.autogen.price where time < now() - 24h'
    else:
        return "INVALID"

def queryValidChecker(resultSet):
    response = list(resultSet.get_points(measurement='price'))
    if len(response) != 0:
        return True
    else:
        return False

def priceParser(resultSet):
    response = list(resultSet.get_points(measurement='price'))
    response = response[0]
    price = response["last"]
    return price

def getNews(currency):
    top_headlines = newsapi.get_everything(q=currency, language='en')
    articles = top_headlines["articles"]
    returnString = ""
    for i in range(5):
        article = articles[i]
        title = article["title"]
        url = article["url"]
        articleStr = title + "\n" + url + "\n"
        if i != 4:
            articleStr += "\n"
        returnString += articleStr
    return returnString
