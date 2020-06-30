import json
import subprocess
import re

# This script may be called in two different ways:
# 1) With Prebid auto-granularity setting
# 2) Manually

linItemNamePrefix = "PubMatic OpenWrap" # here you need to put line item name prefix, line items will be generated as "Line Item Name ( 0.05 )" for bid value 0.05
firstLineItemBidRate = 0.05 # here you have to mention the bid rate of the last line-item created on UI
bidBucketOf = 0.05 # here you need to mention the bucket value in increment of which you want next line item to be created
maxBidRate = 1.00 # here you need to mention the max value of bid rate of which you want to create a line item; if you mention 5.00 then line item of bid rate 5.00 will be created
fileName = "mopub_test_6_9_20.txt" # name or path of the text file in which you have copied the Curl call of the line item which we need to refer; make sure it is created recently to have a valid csrf token


# copying the curlCall from the given file; if invalid file name is provided then code will stop after throwing errors
f = open(fileName, "r")
curlCall = f.read()
f.close()

# grab the JSON post data
postData = re.findall("(--data-binary '(.*?)')", curlCall)
if postData and postData[0] and postData[0][1]:
	postDataJson = json.loads(postData[0][1])
	print(postDataJson)
else:
	print("Curl Call string is not as expected")

# this function creates MoPub line items.
# type can be set to 'manual' or 'prebid_autogranularity'
def create_line_items(postDataJson, linItemNamePrefix, firstLineItemBidRate, maxBidRate, bidBucketOf):

	# initializing value for new bid rate
	currentBidRate = firstLineItemBidRate
	linItemName = linItemNamePrefix

	# check whether new value is less than max allowed bid rate
	while currentBidRate < maxBidRate:
		print("")
		# updating next bid rate value
		currentBidRate = round((currentBidRate + bidBucketOf),2)
		print("Executing the MoPub API to create new line item with Bid Rate: %.2f" % (currentBidRate))
		postDataJson['bid'] = currentBidRate # Limit to 2 decimal points to get around the float behavior
		postDataJson['name'] = linItemName + (" ( %.2f )" % (currentBidRate)) # changing line item name
		postDataJson['keywords'][0] = ("pwtplt:inapp AND pwtbst:1 AND pwtpb:%.2f" % (currentBidRate)) # setting line item keywords
		# creating a copy of given curl call with new bid rate value
		newCurlCall = re.sub(r'--data-binary \'.*?\'', '--data-binary \'%s\'' % (json.dumps(postDataJson)), curlCall)
		# execute curl call
		output = subprocess.Popen(newCurlCall, shell=True, stdout=subprocess.PIPE).stdout.read()
		print(output)
		outputJson = json.loads(output)
		# check response; if not successful, inform and break the loop
		if outputJson['status'] == "error":
			print("Something went wrong, stopping the line item creation process. You may need to copy a new CSRF token from the browser and restart the process with firstLineItemBidRate set to %.2f ." % (currentBidRate - bidBucketOf))
			break
		else:
			print("Line item created successfuly.")

# OpenWrap SDK only supports Prebid's Auto Granularity at this time with MoPub.
# Documentation for this is available at prebid.org
# There are four separate CPM levels set within auto-granularity:
# CPM of <= $5 at $0.05 increments
# CPM of <= $10 and > $5 at $0.10 increments
# CPM of <= $20 and > $10 at $0.50 increments
# CPM > $20 is capped at $20

# Create settings for Prebid auto-granularity.
def set_prebid_autogranularity():
	create_line_items(postDataJson, linItemNamePrefix, 0.00, 5, 0.05)
	create_line_items(postDataJson, linItemNamePrefix, 5, 10, 0.10)
	create_line_items(postDataJson, linItemNamePrefix, 10, 20, 0.50)
	create_line_items(postDataJson, linItemNamePrefix, 20, 20, 0)

# uncomment the line below to set auto-granularity. This is the only setting
# supported by OpenWrap SDK.
set_prebid_autogranularity()

# run manually by uncommenting the code below
# create_line_items(postDataJson, linItemNamePrefix, 47.48, 50, 0.01)
