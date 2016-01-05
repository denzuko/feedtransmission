#!/usr/bin/python

import sys, os
import feedparser
import transmissionrpc
import argparse
import logging

# path to the added items list file
added_items_filepath = os.path.join(os.path.abspath(os.path.dirname(os.path.abspath(__file__))), 'addeditems.txt')

# read the added items list from the file
def readAddedItems():
	addeditems = []
	if os.path.exists(added_items_filepath):
		with open(added_items_filepath,'r') as f:
			for line in f:
				addeditems.append(line.rstrip('\n'))
	return addeditems

# appends a link to the added items
def addItem(link):
	with open(added_items_filepath, 'a') as f:
		f.write(link + '\n')

# parses and adds torrents from feed
def parseFeed(feed_url):
	feed = feedparser.parse(feed_url)
	if feed.bozo and feed.bozo_exception:
		logging.error("Error reading feed \'{0}\': ".format(feed_url) + str(feed.bozo_exception).strip())
		return

	addeditems = readAddedItems()

	for item in feed.entries:
		if item.link not in addeditems:
			try:
				logging.info("Adding Torrent: " + str(item.title))
				tc.add_torrent(item.link)
				addItem(item.link)
			except:
				logging.error("Error adding item \'{0}\': ".format(item.link) + str(sys.exc_info()[0]).strip())

# argparse configuration and argument definitions
parser = argparse.ArgumentParser(description='Reads RSS/Atom Feeds and add torrents to Transmission')
parser.add_argument('feed_urls', metavar='<url>', type=str, nargs='+',
				   help='Feed Url(s)')
parser.add_argument('--transmission-host',
					metavar='<host>',
					default='localhost',
					help='Host for Transmission RPC (default: %(default)s)')
parser.add_argument('--transmission-port',
					default='9091',
					metavar='<port>',
					help='Port for Transmission RPC (default: %(default)s)')
parser.add_argument('--transmission-user',
					default=None,
					metavar='<user>',
					help='Port for Transmission RPC (default: %(default)s)')
parser.add_argument('--transmission-password',
					default=None,
					metavar='<password>',
					help='Port for Transmission RPC (default: %(default)s)')
parser.add_argument('--log-file',
					default=None,
					metavar='<logfile path>',
					help='The logging file, if not specified, prints to output')
parser.add_argument('--clear-added-items',
					action='store_true',
					help='Clears the list of added torrents. You can also do that by deleting the addeditems.txt')

# parse the arguments
args = parser.parse_args()

if args.log_file:
	logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',level=logging.DEBUG, filename=args.log_file)
else:
	logging.basicConfig(format='%(asctime)s: %(message)s',level=logging.DEBUG)


# clears the added items file if asked for
if args.clear_added_items:
	os.remove(added_items_filepath)

# Connecting to Tranmission
try:
	tc = transmissionrpc.Client(args.transmission_host, port=args.transmission_port, user=args.transmission_user, password=args.transmission_password)
except transmissionrpc.error.TransmissionError as te:
	logging.error("Error connecting to Transmission: " + str(te).strip())
	exit(0)
except:
	logging.error("Error connecting to Transmission: " + str(sys.exc_info()[0]).strip())
	exit(0)

# read the feed urls from config
for feed_url in args.feed_urls:
	parseFeed(feed_url)

