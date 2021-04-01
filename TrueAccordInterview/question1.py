import requests as reqs
import json
import pandas as pd

def debtRequest():
    debtRequest = reqs.get("https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api/debts")
    debt_dict = json.loads(debtRequest.text)
    return debt_dict

def paymentReq():
    paymentRequest = reqs.get(" https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api/payment_plans")
    pay_dict = json.loads(paymentRequest.text)
    return pay_dict

def dictionaryConcat(debts, payments):
    my_dict = {}
    for x in debts:
        if (x['id'] in my_dict):
            pass
        else:
            my_dict[x['id']] = {"amount": x['amount'], "payments": []}
    for x in payments:
        if (x['id'] in my_dict):
            my_dict[x['id']]['payments'].append(x)
    print(my_dict)


def main():
    debts = debtRequest()
    for x in debts:
        print(x)
    payments = paymentReq()
    for x in payments:
        print(x)
    dictionaryConcat(debts, payments)

main()