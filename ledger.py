#!/usr/bin/env python3
import sys
import re
import datetime

datePattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")

defaultCurrency = "$"

class Transaction():
    pass

class Posting():
    pass


def handleFile(filePath, transactions):
    with open(filePath) as file:
        accounts = 0
        for line in file.readlines():
            if line.startswith(";"):
                 continue

            if line.startswith("!include"):
                handleFile(line.split()[1], transactions)
                continue
            
            print(line)
            if  datePattern.match(line):
                transaction = Transaction()
                transaction.postings = []
                transactions.append(transaction)
                dateString = datePattern.search(line).group()
                transaction.date = datetime.datetime.strptime(dateString, "%Y/%m/%d")
                transaction.description = line.replace(dateString, '').strip()

                accounts = 2
                continue

            if accounts >= 1:
                posting = Posting()
                transaction.postings.append(posting)
                line = line.strip()

                splittedLine = [x.strip() for x in line.replace("\t", '', line.count('\t') - 1).split('\t')]

                account = splittedLine[0];
                amountStr = splittedLine[1].strip() if len(splittedLine) > 1 else "Pending"
                amount = 0

                if defaultCurrency in amountStr:
                    amount = float(amountStr.replace(defaultCurrency, ''))
                    currency = defaultCurrency
                else:
                    if len(amountStr.split(" ")) > 1:
                        amount = float(amountStr.split(" ")[0])
                        currency = amountStr.split(" ")[1]
                    else:
                        currency = defaultCurrency
            
                if amount == 0:
                    amount = transaction.postings[0].amount
                    for pos in transaction.postings[1:-1]:
                        amount += pos.amount;
                    amount = -amount

                posting.account = account
                posting.amount = amount
                posting.currency = currency
                accounts -=1
        
def register(regex, transtions):
    currencies = {};
    for transaction in transactions:
        print(str(transaction.date) + " " + transaction.description, end='\t')
        for posting in transaction.postings:
            print(posting.account, end="\t")
            print(str(posting.amount) + posting.currency, end="\t")

            # Apply operation
            if posting.currency not in currencies:
                currencies[posting.currency] = 0
            
            currencies[posting.currency] += posting.amount
            
            # Print balances
            for curr, amnt in currencies.items():
                if amnt != 0:
                    print(str(amnt) + curr)
            
            if(all(value == 0 for value in currencies.values())):
                print("0")
        


transactions = []
filePath = sys.argv[1]
handleFile(filePath, transactions)


register("", transactions)




