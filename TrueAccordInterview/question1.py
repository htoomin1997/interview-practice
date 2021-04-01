import requests as reqs
import json
import pandas as pd
import numpy as np
from datetime import timedelta, datetime

def dataIntialization():
    #On 4/1/2021 was taking a while to complete the response...
    #payment plans request would sometimes time out!
    try:
        debtRequest = reqs.get("https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api/debts")
        debt_dict = json.loads(debtRequest.text)
        debts_df = pd.DataFrame.from_dict(debt_dict)
        
        print("request 1 completed")

        plansReq = reqs.get("https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api/payment_plans")
        payment_plans = json.loads(plansReq.text)
        plans_df = pd.DataFrame.from_dict(payment_plans)

        print("request 2 completed")

        paymentsReq = reqs.get("https://my-json-server.typicode.com/druska/trueaccord-mock-payments-api/payments")
        payments = json.loads(paymentsReq.text)
        payment_df = pd.DataFrame.from_dict(payments)

        print("request 3 completed")

        bigDf = pd.merge(left=debts_df, right=plans_df, left_on="id", right_on="debt_id", how="outer")
        del bigDf['debt_id']

        bigDf.rename(columns={"amount":"debt_amount", "id_x": "debt_id", "id_y": "payment_plan_id"}, inplace=True)
        return (bigDf, payment_df)
 
    except:
        print("error?")

def isEnrolled(concatDf):
    isEnrolled = []
    for x in concatDf['payment_plan_id']:
        isEnrolled.append(False) if (np.isnan(x)) else isEnrolled.append(True)

    concatDf["is_in_payment_plan"] = isEnrolled
    return concatDf

#So if they are enrolled in a payment plan, instead of using the payments, just use the payment plan amount?
def remainingAmount(bigDf, payment_df):
    payments_dict = {}
    for index, row in payment_df.iterrows():
        if (row['payment_plan_id'] in payments_dict):
            payments_dict[row['payment_plan_id']] += row['amount']
        else:
            payments_dict[row['payment_plan_id']] = row['amount']
    print(payments_dict)

    amounts = []
    for index, row in bigDf.iterrows():
        if (row['is_in_payment_plan'] == True):
            amounts.append(row['amount_to_pay'] - payments_dict[row['payment_plan_id']])
        else:
            amounts.append(row['debt_amount'])
    bigDf['remaining_amount'] = amounts
    return bigDf

def nextPayment(bigDf, payment_df):
    payments_dict = {}
    for index, row in payment_df.iterrows():
        if (row['payment_plan_id'] in payments_dict):
            payments_dict[row['payment_plan_id']].append(row['date'])
        else:
            payments_dict[row['payment_plan_id']] = [row['date']]
    
    dates = []

    #Things to keep in mind:
    #No payments
    #No payment plan
    #Late Payments
    for index, row in bigDf.iterrows():
        if (row['is_in_payment_plan'] == True):
            targetDates = payments_dict[row['payment_plan_id']]
            startDate = row['start_date']
            dateAdd = 14 if row['installment_frequency'] == "BI_WEEKLY" else 7
            print("DAY TO ADD",dateAdd)
            if (len(targetDates) == 0):
                print(startDate + 14)
            else:
                targetDates.sort()
                latestDate = targetDates[len(targetDates)-1]
                latestDate = datetime.strptime(latestDate, "%Y-%m-%d")
                print("Before:",latestDate)
                latestDate += timedelta(days=14)
                print("After:",latestDate)

        else:
            dates.append(None)

def main():
    concatDf, payments = dataIntialization()
    newDf = isEnrolled(concatDf)
    newDf = remainingAmount(newDf, payments)
    print(newDf)
    nextPayment(newDf, payments)

main()