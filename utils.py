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
