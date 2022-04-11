import json
import pandas as pd
import requests
import numpy as np

from pandas import DataFrame

url = "https://simpledebit.herokuapp.com/merchants"


# Get a list of merchant ids
def fetch_merchants(url: str):
    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return "Error: " + str(e)

    return response

# Extract transactions for merchant
def fetch_transactions(merchant_id: str):
    """ Fetches merchant's transaction details """
    response = requests.get(f"https://simpledebit.herokuapp.com/merchants/{merchant_id}")
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        return "Error: " + str(e)
    return response

def normalize_details(merchant_transaction_details: json) -> pd.DataFrame:
    """ Normalizes the transactions details """
    try:
        # Normalizing te transaction details
        merchant_transaction_details = pd.json_normalize(
            merchant_transaction_details, 'transactions', ['id', 'iban', ['discount', 'minimum_transaction_count'], ['discount', 'fees_discount']])
        merchant_transaction_details = merchant_transaction_details.reindex(
            columns=['id', 'iban', 'discount.minimum_transaction_count', 'discount.fees_discount', 'amount', 'fee'])
        return calculate_discount_amount(merchant_transaction_details)
    except Exception as e:
        print(e)


def calculate_discount_amount(transaction_details: pd.DataFrame) -> pd.DataFrame:
    """ Adds discount_amount column """
    try:
        # checking the no of transactions of the merchant and comparing it with minimum_transaction_count.
        # to find out whether he/she is eligible for the discount or not.
        # mask = transaction_details['id'].map(transaction_details['id'].value_counts(
        # )) >= transaction_details['discount.minimum_transaction_count']
        # checking whether the discount.fees_discount is less than transactions.fee if yes,
        # then the discount amount would be fees_discount. And on contrary if the transactions.fee is
        # less than fees_discount then the discount amount would be transactions.fee.
        # because the discount applies only on fees not on the whole amount. That means if the transactions.fee
        # less than fees_discount we are giving them 100% discount on fees.
        conditions = [
            (transaction_details['discount.fees_discount'] < transaction_details['fee']),
            (transaction_details['fee'] < transaction_details['discount.fees_discount'])]
        values = [transaction_details['discount.fees_discount'], transaction_details['fee']]
        transaction_details['discount_amount'] = np.select(conditions, values)
        transaction_details['id_counts'] = transaction_details['id'].value_counts()[0]
        transaction_details.loc[transaction_details['id_counts'] < transaction_details['discount.minimum_transaction_count'], 'discount_amount'] = 0
        transaction_details.drop('id_counts', axis='columns', inplace=True)
        return transaction_details
    except Exception as e:
        print(e)


# adding new column of payment_amount for required(transactions) csv output
def payment_amounts(discount_and_transactions: DataFrame) -> DataFrame:
    try:
        payment_amount = (
            discount_and_transactions.groupby(["iban"])
            .agg({"amount": "sum","discount_amount": "sum",})
            .reset_index()
        )
        payment_amount["payment_amount"] = (
            payment_amount["amount"] -  payment_amount["discount_amount"]
        )
        payment_amount = payment_amount[["iban", "payment_amount"]]
        return payment_amount
    except Exception as e:
        print(e)


def generate_csv(merchant_transaction_details: pd.DataFrame, location: str) -> None:
    """ Generates transactions.csv file contains 1 record for each transaction """
    try:
        merchant_transaction_details.to_csv(
            location, index=False)
    except Exception as e:
        print(e)


def main():
    response = fetch_merchants(url)
    merchants = response.json()
    transactions = []
    payment = []
    for merchant in merchants:
        target_merchant = fetch_transactions(merchant)
        merchant_transactions = target_merchant.json()

        transaction_details = normalize_details(merchant_transactions)
        payments_transaction = payment_amounts(transaction_details)
        payment.append(payments_transaction)
        transactions.append(transaction_details)
    payment = pd.concat(payment)
    transactions = pd.concat(transactions)


    # writing data of transaction csv
    generate_csv(transactions,"transaction.csv")
    # writing data of payment csv
    generate_csv(payment, "payment.csv")


if __name__ == '__main__':
    main()