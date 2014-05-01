import getopt
import sys
import configparser
import csv
import geopy
from geopy import geocoders

def usage():
	print 'batch-geocode.py -hcv -s <config-file> -i <input-file> -o <output-file>'
	print '\t-h, --help        : help'
	print '\t-c, --config      : interactively configure the program, note this cannot be combined with -s'
	print '\t-v, --verbose     : verbose'
	print '\t-s, --config-file : set input config file, note this cannot be combiend with -c'
	print '\t-i, --input       : set input file'
	print '\t-o, --output      : set output file'

def interactiveConfigure(fileptr, parser, gCoderArray):

	gCoders = []
	apiRequiredGeocoders = ["yahoo", "bing"]
	parser.add_section('API KEYS')
	parser.add_section('VALID')
	for gCoder in gCoderArray:
		parser.set('VALID',gCoder,'true')
	for gCoder in apiRequiredGeocoders:
		while True:
			reply = input('Do you want to use the ' + gCoder + ' api?(y/n)')
			if reply not in ("y", "Y", "n", "N"):
				continue
			elif reply in ("n", "N"):
				break
				parser.set('VALID', gCoder, 'false')
			elif reply in ("y", "Y"):
				gCoders.append(gCoder)
				parser.set('API KEYS', gCoder, input('Enter the ' + gCoder + 'api key'))
				parser.set('VALID', gCoder, 'true')
				break

	return gCoders

def setGeoCoders(gCoderStrings, configFilePtr):
	gCoders = {}
	config = ConfigParser.RawConfigParser()
	config.readfp(configFilePtr)
	for gCoderKey in gCoderStrings:
		if gCoderKey == "google":
			gCoders[gCoderKey] = geocoders.GoogleV3()
		elif gCoderKey == "geocoder.us":
			gCoders[gCoderKey] = geocoders.GeocoderDotUS()
		elif gCoderKey == "GeoNames":
			gCoders[gCoderKey] = geocoders.GeoNames()
		elif gCoderKey == "MediaWiki":
			gCoders[gCoderKey] = geocoders.MediaWiki()
		elif gCoderKey == "yahoo":
			gCoders[gCoderKey] = geocoders.Yahoo(config.get('API KEYS', gCoderKey))
		elif gCoderKey == 'bing':
			gCoders[gCoderKey] = geocoders.Bing(config.get('API KEYS', gCoderKey))
	return gCoders

def geocodeAndSerialize(inputCSV, outputCSV, gCoderDict, gCoderFieldsDict):
	counter = 0
	for row in inputCSV:
		counter +=1
		tempDict = {}
		tempDict['id'] = counter
		tempDict['address'] = row['address']
		for field in gCoderFieldsDict:
			foo, (tempDict[gCoderFieldsDict[field]['lat']], tempDict[gCoderFieldsDict[field]['lng']]) = gCoderDict[field].geocode(row['address'])
		outputCSV.writerow(tempDict)


def main():
	# validate and get options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hcs:i:o:v", ["help", "config", "config-file=", "input=", "output=", "verbose"])
	except:
		usage()
		sys.exit(2)

	#option flags, variables
	
	inputFileName = "input.csv"
	outputFileName = "output.csv"
	configFileName = "options.cfg"
	outputFile = None
	inputFile = None
	configFile = None
	verboseFlag = False
	configFlag = False
	config = ConfigParser.RawConfigParser()
	gCoders = ["google", "geocoder.us", "GeoNames", "MediaWiki"]

	#parse options, set flags

	for o, a in opts:
		if o in ("-v", "--verbose"):
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-c", "--config"):
			configFlag = True
		elif o in ("-s", "--config-file"):
			configFileName = a
		elif o in ("-i", "--input"):
			inputFileName = a
		elif o in ("-o", "--output"):
			outputFileName = a

	# validate option combinations, set defaults

	if (configFlag and setConfigFlag):
		usage()
		sys.exit(3)

	if (configFlag):
		#open the default config file for writing
		configFile = open(configFileName, "w")
		gCoders += interactiveConfigure(configFile, config, gCoders)
		configFile.close()
		
	configFile = open(configFileName, "r")

	inputFile = open(inputFileName, "r")
	outputFile = open(outputFileName, "w")
	inputCSVReader = csv.DictReader(inputFile, delimiter=';')
	outputFields = ['id', 'address']
	gCoderFieldsDict = {}
	for field in gCoders:
		outputFields.append(field + '_lat')
		outputFields.append(field + '_lng')
		gCoderFieldsDict[field] = {'lat': field + '_lat', 'lng': field + '_lng'}

	outputCSVWriter = csv.DictWriter(outputFile, outputFields, delimiter=';')
	outputCSVWriter.writeheader()

	# geocode and export

	geocodeAndSerialize(inputCSVReader, outputCSVWriter, setGeoCoders(gCoders,configFile), gCoderDict)

	# close pointers

	configFile.close()
	inputFile.close()
	outputFile.close()

	print 'Goodbye!'

	sys.exit()

if __name__ == "__main__":
	main()