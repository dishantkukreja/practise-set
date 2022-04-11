import os
import requests
import pandas as pd

from src.main import fetch_merchants,\
    fetch_transactions,\
    payment_amounts,\
    normalize_details,\
    generate_csv


def test_fetch_merchants():
   test_url = "https://simpledebit.herokuapp.com/merchants"
   response = fetch_merchants(test_url)  # get_page() returns a response object
   assert response.status_code == 200


def test_response_each_merchant():
    response_API = requests.get("https://simpledebit.herokuapp.com/merchants")
    jsons_merchant = response_API.json()[0]
    response = fetch_transactions(jsons_merchant)
    assert response.status_code == 200


def test_normalize_details():
    API_url = "https://simpledebit.herokuapp.com/merchants/"
    fetched_merchant = fetch_merchants(API_url)
    merchants = fetched_merchant.json()[0]
    merchant_transaction = fetch_transactions(merchants)
    merchant_transaction_details = merchant_transaction.json()
    transaction_details = normalize_details(merchant_transaction_details)
    assert (28, 7) == transaction_details.shape
    assert transaction_details.columns[0] == 'id'
    assert transaction_details.columns[6] == 'discount_amount'


def test_payment_amounts():
    df1 = pd.DataFrame({'iban': ["GB7197158194781194", "GB4717308619277390", "GB4717308619277390", "GB7197158194781194"],
                        'amount': [5, 5, 5, 5],
                        'discount_amount': [50, 40, 30, 20]})
    result = payment_amounts(df1)
    expected = 'GB4717308619277390GB7197158194781194'

    assert result.sum()[0] == expected


def test_generate_csv():
    transactions_output_location = "./test/transaction.csv"
    API_url = "https://simpledebit.herokuapp.com/merchants/"
    fetched_merchant = fetch_merchants(API_url)
    merchants = fetched_merchant.json()[0]
    merchant_transaction = fetch_transactions(merchants)
    merchant_transaction_details = merchant_transaction.json()
    transaction_details = normalize_details(merchant_transaction_details)
    generate_csv(
        transaction_details, transactions_output_location)

    assert os.path.exists(transactions_output_location)