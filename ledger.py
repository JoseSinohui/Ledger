#!/usr/bin/env python3
import sys
import re
import datetime

datePattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")

class Transaction():
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
                transactions.append(transaction)
                dateString = datePattern.search(line).group()
                transaction.date = datetime.datetime.strptime(dateString, "%Y/%m/%d")
                transaction.description = line.replace(dateString, '').strip()

                accounts = 2
                continue

            if accounts >= 1:
                if accounts == 2:
                    transaction.fromAccount = line
                if accounts == 1:
                    transaction.toAccount = line
                accounts -=1

            

                
            
            
            
        
        
transactions = []
filePath = sys.argv[1]
handleFile(filePath, transactions)
print("Done")



