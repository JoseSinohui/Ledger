#!/usr/bin/env python3
import sys
import re
import datetime
import collections
import argparse
import os

datePattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")

defaultCurrency = "$"


class Transaction():
    pass


class Posting():
    pass


def handleFile(filePath, transactions, prnt):
    with open(filePath) as file:
        accounts = 0
        for line in file.readlines():
            if line.startswith(";"):
                continue

            if line.startswith("!include"):
                handleFile(line.split()[1], transactions, prnt)
                continue
            if prnt:
                print(line)
            if datePattern.search(line):
                transaction = Transaction()
                transaction.postings = []
                transactions.append(transaction)
                dateString = datePattern.search(line).group()
                transaction.date = datetime.datetime.strptime(
                    dateString, "%Y/%m/%d")
                transaction.description = line.replace(dateString, '').strip()

                accounts = 2
                continue

            if accounts >= 1:
                posting = Posting()
                transaction.postings.append(posting)
                posting.transaction = transaction
                line = line.strip()

                splittedLine = [x.strip() for x in line.replace(
                    "\t", '', line.count('\t') - 1).split('\t')]

                account = splittedLine[0]
                amountStr = splittedLine[1].strip() if len(
                    splittedLine) > 1 else "Pending"
                amount = 0

                if defaultCurrency in amountStr:
                    amount = float(amountStr.replace(defaultCurrency, ''))
                    currency = defaultCurrency
                else:
                    if len(amountStr.split(" ")) > 1:
                        amount = float(amountStr.split(" ")[0])
                        currency = amountStr.split(" ")[1]
                    else:
                        currency = transaction.postings[0].currency

                if amount == 0:
                    amount = transaction.postings[0].amount
                    for pos in transaction.postings[1:-1]:
                        amount += pos.amount
                    amount = -amount

                posting.account = account
                posting.amount = amount
                posting.currency = currency
                accounts -= 1


def register(transactions, *regexes):
    patterns = [re.compile(regex, re.IGNORECASE) for regex in regexes]
    currencies = {}
    columns = os.popen('stty size', 'r').read().split()[1]
    for transaction in transactions:
        if not any(any(pattern.search(posting.account) for pattern in patterns) for posting in transaction.postings):
            continue

        print(str(transaction.date) + " " + transaction.description, end='\t')

        for posting in transaction.postings:
            if not any(pattern.search(posting.account) for pattern in patterns):
                continue
            print(posting.account, end= "\t")
            print(str(posting.amount) + " " + posting.currency)
            print("\tBalances:")

            # Apply operation
            if posting.currency not in currencies:
                currencies[posting.currency] = 0

            currencies[posting.currency] += posting.amount

            # Print balances
            for curr, amnt in currencies.items():
                if amnt != 0:
                    print("\t\t" + (str(amnt) +" "+ curr))

            if(all(value == 0 for value in currencies.values())):
                print("\t\t0")
            print('')

class Tree():
    pass

class Node():
    def __init__(self, name):
        self.childNodes = []
        self.currenciesBalance = collections.defaultdict(lambda: 0)
        self.name = name
        self.amount = 0
    

def printNode(node, patterns):
    # Print balances
    for i, (curr, amnt) in enumerate(node.currenciesBalance.items()):
        endString = '' if i==len(node.currenciesBalance) - 1 else '\n'
        print("\t{:.2f} {}\t".format(amnt, curr), end=endString)
    line = ""
    if len(node.childNodes) == 1:
        print(node.name + ":" + node.childNodes[0].name)
    else:
        print(node.name)
        for childNode in node.childNodes:
            printNode(childNode, patterns)
    

def balance(transactions, *regexes):
    patterns = [re.compile(regex, re.IGNORECASE) for regex in regexes]
    tree = Tree()
    currentNode = Node("root")
    tree.root = currentNode

    for tr in transactions:
        for posting in tr.postings:

            if not any(pattern.search(posting.account) for pattern in patterns):
                continue

            currentNode.currenciesBalance[posting.currency] += posting.amount # <- updates root

            for i, account in enumerate(posting.account.split(":")):
                # check for existing node in childs of currentNode
                nextNode = None
                for childNode in currentNode.childNodes:
                    if childNode.name == account:
                        nextNode = childNode
                        break
                
                # Update currentNode
                if nextNode:
                    currentNode = nextNode
                else:
                    newNode = Node(account)
                    currentNode.childNodes.append(newNode)
                    currentNode = newNode

                # Update the balance of the node
                currentNode.currenciesBalance[posting.currency] += posting.amount
            
            # reset to root
            currentNode = tree.root

    # Sort by name for default
    tree.root.childNodes = sorted(tree.root.childNodes, key=lambda node: node.name)

    
    for x in tree.root.childNodes:
        printNode(x, patterns)

    print("--------------------")

    for currency, amount in tree.root.currenciesBalance.items():
        print('\t{:.2f} {}'.format(amount, currency))
    

bal_choices = ['b', 'bal', 'balance']
reg_choices = ['r', 'reg', 'register']
print_choices = ['print', 'p']
choices = []
choices.extend(bal_choices)
choices.extend(reg_choices)
choices.extend(print_choices)
argparser = argparse.ArgumentParser()
argparser.add_argument("command", help='Command to run (bal, reg, print)', choices=choices)
argparser.add_argument("-f", "--file",help="Ledger file")
argparser.add_argument("--price-db", help="Price DB File")
argparser.add_argument("-s", "--sort", help="Sort (date, amount)", choices = ["d"])
argparser.add_argument("filters", help='Regexes to match', nargs='*')
args = argparser.parse_args()
transactions = []
filePath = args.file
handleFile(filePath, transactions, args.command in print_choices)

if args.sort:
    if args.sort == "d":
        transactions.sort(key=lambda x: x.date)
if args.command in bal_choices:
    balance(transactions, '')
elif args.command in reg_choices:
    register(transactions, '')
