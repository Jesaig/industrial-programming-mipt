import datetime
import graphyte
import logging
import numpy as np
import requests
import time
import yaml

logging.getLogger().setLevel(logging.INFO)
URL = 'https://gov.capital/commodity/gold/'
GRAPHITE_HOST = 'graphite'


def from_date_to_timestamp(date):
    return time.mktime(
        datetime.datetime.strptime(date, '%Y-%m-%d').timetuple()
    )


def get_gold_prices_series():
    page = requests.get(URL).text
    ind = page.find('var config')
    new_ind = page[ind:].find(';')
    parsed_data = yaml.load(page[ind + len('var config = '): ind + new_ind])
    dates = parsed_data['data']['labels']

    proper_datasets = map(
        lambda dataset: dataset['data'],
        filter(lambda dataset: dataset['label'] == 'Gold price',
               parsed_data['data']['datasets']),
    )

    prices = map(lambda pair: pair[0] or pair[1], zip(*proper_datasets))

    time_series = list(map(
        lambda pair: (from_date_to_timestamp(pair[0]), float(pair[1])), list(zip(dates, prices))
    ))

    return time_series


def get_data(data_type='actual'):
    gold_prices_series = np.array(get_gold_prices_series())
    timestamps = np.array(list(map(lambda pair: pair[0], gold_prices_series)))

    current_ts = time.time()
    indeces = np.array([])

    if data_type == 'actual':
        indeces = (timestamps <= current_ts)
    else:
        indeces = (timestamps > current_ts)

    return gold_prices_series[indeces]


def send_metrics(gold_prices_series, data_type):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='gold_prices')
    for gold_price in gold_prices_series:
        sender.send(data_type, gold_price[1])


def main():
    actual_gold_prices = get_data()
    predicted_gold_prices = get_data('predicted')
    logging.info(actual_gold_prices)

    time.sleep(20)

    send_metrics(actual_gold_prices, 'actual')
    send_metrics(predicted_gold_prices, 'predicted')


if __name__ == '__main__':
    main()