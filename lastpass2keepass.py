# LastPassConvertor
#
# Supports:
# Keepass XML - keepassxml
#
# USAGE: python lastpassconvertor.py LASTPASSEXPORT OUTPUT
# Example: python lastpassconvertor.py export keepass.db
#
# The LastPass format;
# url,username,password,1extra,name,ignore for now- grouping (\ delimited),last_touch,launch_count,fav

import sys, csv, time, datetime
from lxml import etree

fileError = "You either need more permissions or the file does not exist."
lineBreak = "____________________________________________________________\n"

inputFile = sys.argv[1]
outputFile = sys.argv[2]

# Generate Creation date
now = datetime.datetime.now()

# Check if we can read/write to input/output.
try:
    f = open(sys.argv[1])
    try:
        open(outputFile, "w").close()
        w = open(outputFile, "aw")
    except IOError:
        print "Cannot write to disk... exiting.", fileError
        sys.exit()
except IOError:
    print "Cannot read file: '%s'" % (inputFile), fileError
    sys.exit()


# Create a csv dialect and extract the data to a reader object.
dialect = csv.Sniffer().sniff(f.read(1024))
f.seek(0)
reader = csv.reader(f, dialect)

# Create a list of the entries, allow us to manipulate it.
# Can't be done with reader object.

allEntries = []

for x in reader:
    allEntries.append(x)
allEntries.pop(0)

# Keepass xml generator

def keepassxml():

    # Add doctype
    w.write("<!DOCTYPE KEEPASSX_DATABASE>")
  
    formattedNow = now.strftime("%Y-%m-%dT%H:%M")

    # Initialize tree
    page = etree.Element ('database')
    doc = etree.ElementTree (page)
    headElt = etree.SubElement (page, 'group')
    title = etree.SubElement (headElt, 'title')
    title.text = 'LastPassConversion'
    icon = etree.SubElement (headElt, 'icon')
    icon.text = '0'

    # List of failed entries
    failed = {}
    print lineBreak
    print "DEBUG of '%s' file conversion to the KeePassXML format, outputing to the '%s' file.\n" % (inputFile,outputFile)
    
    # Initilize and loop through all entries
    for x in allEntries:
        # Each Entry
        entryElt = etree.SubElement (headElt, 'entry')
        # Entry information
        try:
            etree.SubElement (entryElt, 'title').text = str(x[4])
            etree.SubElement (entryElt, 'username').text = str(x[1])
            etree.SubElement (entryElt, 'password').text = str(x[2])
            etree.SubElement (entryElt, 'url').text = str(x[0])
            etree.SubElement (entryElt, 'comment').text = str(x[3])
            etree.SubElement (entryElt, 'icon').text = "0"
            etree.SubElement (entryElt, 'creation').text = formattedNow
            etree.SubElement (entryElt, 'lastaccess').text = str(x[6])
            etree.SubElement (entryElt, 'lastmod').text = str(x[7])
            etree.SubElement (entryElt, 'expire').text = "Never"
        except:
            # Catch illformed entries
            
            # Grab entry position
            p = allEntries.index(x) + 2
            failed[p] = [",".join(x)]
            print "Failed to format entry at line %d" % (p)
            
    if len(failed) != 0:
        failedList = ["%d : %s" % (p, str(e[0]).decode("utf-8")) for p, e in failed.items()]
        print "\nThe conversion was not clean."
        print "You need to manually import the below entries from the '%s' file, as listed by below." % (inputFile)
        print "Line Number : Entry"
        for x in failedList:
            print x
    print lineBreak
    # Write out tree
    doc.write(w)
    return
    
# Call the keepassxml generator

keepassxml()

f.close()
w.close()           

print "\n'%s' has been succesfully converted to the KeePassXML format." % (inputFile)
print "Converted data can be found in the '%s' file.\n" % (outputFile)