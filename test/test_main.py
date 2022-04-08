import requests
import pandas as pd

from src.main import response_merchant_api,response_each_merchant,merge_df,\
    convert_to_df,transactions_pandas,one_add_to_all_column,discount_amount,\
    rename_columns, payment_amounts

def test_response_merchant_api():
   test_url = "https://simpledebit.herokuapp.com/merchants"
   response = response_merchant_api(test_url)  # get_page() returns a response object
   assert response.status_code == 200


# response_API = requests.get("https://simpledebit.herokuapp.com/merchants")
# jsons_merchant = response_API.json()[0]
# response = response_each_merchant(jsons_merchant)
# print(response)

def test_response_each_merchant():
    response_API = requests.get("https://simpledebit.herokuapp.com/merchants")
    jsons_merchant = response_API.json()[0]
    response = response_each_merchant(jsons_merchant)
    assert response.status_code == 200
#
#
def test_convert_to_df():
    dict = {'id': 'M28A9'}
    result  = convert_to_df(dict, 'id')
    expected = 1

    assert result.count()[0] == expected


def test_transactions_pandas():
    dict = { "transactions": [
    {
      "amount": 54869,
      "fee": 290
    }]}
    result  = transactions_pandas(dict)
    expected = 1
    assert result.count()[0] == expected


def test_one_add_to_all_column():
    data = {'Name': ['Jai', 'Princi', 'Gaurav', 'Anuj']}
    df = pd.DataFrame(data)
    result = one_add_to_all_column(df)
    expected = 1

    assert result == expected


def test_one_add_to_all_column():
    df1 = pd.DataFrame({'lkey': ['foo', 'bar', 'baz', 'foo'],
                        'one': [1, 1, 1, 1]})
    df2 = pd.DataFrame({'rkey': ['foo', 'bar', 'baz', 'foo'],
                        'one': [1, 1, 1, 1]})
    result = merge_df(df1,df2)
    expected = (16, 2 )

    assert result.shape == expected


def test_one_add_to_all_column():
    df1 = pd.DataFrame({'fees_discount': [5, 5, 5, 5],
                        'fee': [50, 40, 30, 20]})
    result = discount_amount(df1)
    expected = None

    assert result == expected


def test_one_add_to_all_column():
    df1 = pd.DataFrame({'0_x': [5, 5, 5, 5],
                        '0_y': [50, 40, 30, 20]})
    result = rename_columns(df1)
    expected = (4, 2)

    assert result.shape == expected


def test_payment_amounts():
    df1 = pd.DataFrame({'iban': ["GB7197158194781194", "GB4717308619277390", "GB4717308619277390", "GB7197158194781194"],
                        'amount': [5, 5, 5, 5],
                        'discount_amount': [50, 40, 30, 20]})
    result = payment_amounts(df1)
    expected = 'GB4717308619277390GB7197158194781194'

    assert result.sum()[0] == expected