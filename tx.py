import json
def tx(sender,reciever,amount):
    x = json.load(open("bank.json"))
    y = json.load(open("settings.json"))
    if sender not in x:
        return "Fail"
    if reciever not in x:
        return "Fail"
    if x[sender]["balance"] < amount+(y["tax"]/100)*amount:
        return "Fail"
    if sender == "tax_collecter" or reciever == "tax_collecter":
        return "Fail"
    if sender == reciever:
        return "Fail"
    x[reciever]["balance"] = round(x[reciever]["balance"]+amount,3)
    x[sender]["balance"] = round((x[sender]["balance"]) - (amount - ((x[sender]["cashback"]/100)*amount) + (y["tax"]/100)*amount),3)
    x["tax_collecter"]["balance"] = round(x["tax_collecter"]["balance"]+y["tax"]/100*amount,3)
    json.dump(x,open("bank.json","w"), indent=4)
    return "Success"
def balance(account):
    x = json.load(open("bank.json"))
    if account not in x:
        return "Fail"
    return x[account]["balance"]