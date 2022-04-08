import requests
import json
import pandas as pd

from pandas import DataFrame


# Get a list of merchant ids from - https://simpledebit.herokuapp.com/merchants
def response_merchant_api(url: str):
    return requests.get(url)


# Extract transactions for each merchant from -https://simpledebit.herokuapp.com/merchants/MERCHANT_ID
def response_each_merchant(jsons_merchant: str):
    return requests.get(f"https://simpledebit.herokuapp.com/merchants/{jsons_merchant}")


# Coverting each dict to df from -https://simpledebit.herokuapp.com/merchants/MERCHANT_ID
def convert_to_df(tr_req: dict, column: str) -> DataFrame:
    # print(type(tr_req))
    return pd.DataFrame([tr_req[column]])


def transactions_pandas(tr_req: dict) -> DataFrame:
    # print(type(tr_req))
    return pd.DataFrame(tr_req["transactions"])


# Adding same value column in each df for merging
def one_add_to_all_column(df: DataFrame) -> DataFrame:
    new_column = df["one"] = 1
    return new_column


# merging data frames for required(transactions) csv output
def merge_df(id_pandas: DataFrame, iban_pandas: DataFrame) -> DataFrame:
    join1 = pd.merge(id_pandas, iban_pandas, on="one").drop("one", axis=1)
    return join1


# Calculate the discount . Subractinf fees_discount from fee
def discount_amount(df: DataFrame) -> DataFrame:
    df["discount_amount"] = df["fee"] - df["fees_discount"]
    return df


# reseting the proper column names
def rename_columns(df: DataFrame) -> DataFrame:
    return df.rename(columns={"0_x": "id", "0_y": "iban"}).reset_index(drop=True)


# adding new column of payment_amount for required(transactions) csv output
def payment_amounts(discount_and_transactions: DataFrame) -> DataFrame:
    payment_amount = (
        discount_and_transactions.groupby(["iban"])
        .agg({"amount": "sum", "discount_amount": "sum"})
        .reset_index()
    )
    payment_amount["payment_amount"] = (
        payment_amount["amount"] + payment_amount["discount_amount"]
    )
    payment_amount = payment_amount[["iban", "payment_amount"]]
    return payment_amount


def main():
    url = "https://simpledebit.herokuapp.com/merchants"
    response_api = response_merchant_api(url)
    print(type(response_api))
    merchants = response_api.json()[0:3]
    all_data = []
    payment = []
    for merchant in merchants:
        target_merchant = response_each_merchant(merchant)
        each_mer = target_merchant.json()

        ids = convert_to_df(each_mer, "id")
        iban = convert_to_df(each_mer, "iban")
        discount = convert_to_df(each_mer, "discount")
        transactions = transactions_pandas(each_mer)

        one_add_to_all_column(ids)
        one_add_to_all_column(iban)
        one_add_to_all_column(discount)
        one_add_to_all_column(transactions)

        iban_di = merge_df(iban, discount)
        one_add_to_all_column(iban_di)

        id_and_iban = merge_df(ids, iban)
        one_add_to_all_column(id_and_iban)
        iban_and_discount = merge_df(id_and_iban, discount)
        one_add_to_all_column(iban_and_discount)
        discount_and_transactions = merge_df(iban_and_discount, transactions)
        discount_and_transactions = rename_columns(discount_and_transactions)

        discount_amount(discount_and_transactions)

        payment_amount = payment_amounts(discount_and_transactions)

        payment.append(payment_amount)
        all_data.append(discount_and_transactions)

    payment = pd.concat(payment)
    all_data = pd.concat(all_data)
    # all_data.to_csv("transactin.csv")
    # payment.to_csv("payment.csv")
    print(payment)


if __name__ == "__main__":
    main()
