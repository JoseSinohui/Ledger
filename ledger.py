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
                amount = splittedLine[1] if len(splittedLine) > 1 else "Pending"
                

                if defaultCurrency in amount:
                    amount = float(amount.replace(defaultCurrency, ''))


                # if amount == '':
                #     amount = transaction.postings[0]
                #     for pos in transaction.postings[1:]:
                #         amount += pos.amount;

                posting.account = account
                posting.amount = amount
                accounts -=1
        
transactions = []
filePath = sys.argv[1]
handleFile(filePath, transactions)
print("Done")



