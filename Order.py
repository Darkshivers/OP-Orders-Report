import requests
import datetime
import json
import csv
import re
import io

apikey = "Key "

def getOrderList():
    url = "https://oak-partnership.co.uk/api/Orders/orders/{IncludeOnlyActiveOrders}"

    headers = {
                'Content-Type': "application/json",
                    'Authorization': apikey,
                        'Cache-Control': "no-cache",
                            'Postman-Token': "97662d3b-e23f-499c-a1e3-046bd0b64441"
                             }

    responseList = requests.request("GET", url, headers=headers)
    return responseList.text

def getOrder(ordernumber):
    url = "https://oak-partnership.co.uk/api/Orders/orderDetails/" + ordernumber

    headers = {
                'Content-Type': "application/json",
                    'Authorization': apikey,
                        'Cache-Control': "no-cache",
                            'Postman-Token': "e0700b0c-b37e-4cce-bf0a-e310fadf6504"
                                }

    response = requests.request("GET", url, headers=headers)
    return response.text

print 'Loading Order Numbers'
allorders = json.loads(getOrderList())

order_header = []
order_body = []


def writefile(header,content):

    for i in range(len(content)):
        content[i] = unicode(content)

    headerpos = 0 
    with open("OP_Order_Report-March.csv", "w") as myfile:
        wr = csv.writer(myfile,quoting=csv.QUOTE_ALL)
        if headerpos == 0:
                wr.writerow(header)
                headerpos+= 1
        if headerpos > 0:
            wr.writerow(content)
def removeTrash(value):
    
    del_list = [' ', '}', '{','\[','\]']
    x = 0 
    value = value.split(",")
    print len(value)
    arr_length = len(value)

    for x in range(arr_length):
        if "rewardProductOptionDetailID" in value[x]:
            value[x] = ""
            value[x+1] = "" 
            value[x+2] = ""
        elif "accountID" in value[x] or "comments" in value[x] or "isSpecialOffer" in value[x] or "orderDetails" in value[x] or "emailAddress" in value[x] or "image" in value[x] or "orderDetailID" in value[x] or "rewardProductID" in value[x]:
            value[x] = ""
        else:
            value[x] = re.sub("|".join(del_list),"", value[x])
        if x <= 13 and not "":
            if value[x] != "":
                order_header.append(value[x])
        elif x > 13 and not "":
            if value[x] != "":
                order_body.append(value[x])
    order_body_length = len(order_body)

    count = 0 

    for x in range(order_body_length):
        if "orderSupplierInvoiceDetailID" in order_body[x]:
            count+= 1
            print("Checking Currency" )
            print "Grabbing Order: " + str(count)
            print " "
            buildOrder((getItemPrice(GetIndividualOrders(count))))


def buildOrder(single_item):

    headers = []
    content = []

    single_order_formatted = []
    single_order_formatted.extend(order_header[x] for x in [0,1,2,6,8])
    single_order_formatted.extend(single_item)

    for i in range(len(single_order_formatted)):
        print single_order_formatted[i]
        segmented_objects = single_order_formatted[i].split(':')
        headers.append(segmented_objects[0])
        content.append(segmented_objects[1])

    return writefile(headers,content)

def outputHeader():
    for x in range(len(order_header)):
        print str(order_header[x])
            
def getItemPrice(order):

    order_length = range(len(order))
    item_cost = []
    item_flags = []

    ordercount = 0

    isPoints = False
    isCurrency = False

    dspflag = '"isDealerSupport"'
    rewardflag = '"rewardProductOption"'
    orderflag = "orderSupplierInvoiceDetailID"

    for x in order_length: 
        if rewardflag in order[x]:
            print "Reward Flag Found!"
            item_flags.append(order[x])
        if dspflag in order_body[x]:
            print "DSP Flag Found!"
            item_flags.append(order[x])
        if orderflag in order_body[x]:
            ordercount+=1
        else:
            "No Order Found!"
        
    if len(item_flags) > 0:
        for x in range(len(item_flags)):
            if item_flags[x] == '"isDealerSupport:"true' or '"rewardProductOption:"None'  :
                isPoints = True
    else:
        isCurrency = True
              
    print "Order is in Points: " + str(isPoints)
    print "Order is in Currency: " + str(isCurrency)

    for x in order_length:
        if "pointsSpent" in order[x]:
            print "Point found!"
            print " "
            itemcost = order[x].split(":")
            item_cost.append(itemcost[1])
        
            if isCurrency == True:
                print "Converting Points value to currency..."
                print " "
                order[x] = str(itemcost[0]) + ":" + unichr(163) + str(float(itemcost[1]) / 100).encode('utf-8').strip()
                print order[x]
                print " "
                return order
            
            if isPoints == True:
                print order[x]
                return order
            else:
                print "No Currency Found"

def GetIndividualOrders(order_number):

    orders = order_body
    single_order = []
    count = 0

    for i in range(len(orders)):
        if "orderSupplierInvoiceDetailID" in orders[i]:
            count+= 1
            if count == 1:
                print "OrderSupplier Flags Found!"
        if count == order_number and "orderSupplierInvoiceDetailID" not in orders[i]:
            single_order.append(orders[i])
            if "orderSupplierInvoiceDetailID" in orders[i]:
                count+= 1

    return single_order
            
def getOrderAmount(): 
    return len(json.loads(getOrderList()))

def getEveryOrder():
    print 'Getting Oak Partnership Orders...'
    amount = getOrderAmount()
    for x in range(1):
        print str(x) + ' Out of: ' +  str(amount)
        removeTrash(getMonthsOrders(x))

def getMonthsOrders(i):
    current  = allorders[i]
    current  = str(current).split(",")
    orderno = str(current[7]).split(" ")
    orderitem = getOrder("355133")
    return orderitem

def GetJSON():

    amount = 0
    order_list = []

    for i in range(getOrderAmount()):
        current  = allorders[i]
        current  = str(current).split(",")
        orderno = current[7].split(" ")
        date = str(current[3]).split(" ")
        if '2019-02' in date[2]:
            amount += 1
            order_list.append(orderno[2])
    print amount

    file = open("monthsOrders.txt","w")

    for i in range(len(order_list)):

        print "Getting Order " + str(i + 1) + " Of " + str(len(order_list))
        order_value = getOrder(order_list[i]).encode('utf-8').strip()

        file.write(order_value)    

def getMonthlyOrders():

    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    print lastMonth.strftime("%Y-%m")

    datestring = str(lastMonth.strftime("%Y-%m"))
    
    for i in range(len(allorders)):
        if datestring in allorders[i]:
            print allorders[i]
         
getEveryOrder()



