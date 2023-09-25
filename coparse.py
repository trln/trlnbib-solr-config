#!/usr/bin/env python

# script to copy any changes made to select_edismax.xml to 
# configoverlay.json;
# when using Solr's Config API or ZooKeeper, solrconfig is ignored and
# only the contents of configoverlay.json are used.

# usage: make changes to config/select_edismax.xml to configure the edismax
# request handler (default for trlnbib).
# run `../coparse.py` from the `trlnbib` directory, which will extract
# the edismax qf/pf field definitions and write them to configoverlay.json
# If possible, test your configuration by uploading it via zkcli.sh (see README.md)
# commit select_edismax and configoverlay.json

from lxml import etree
import json
import shutil

with open('config/select_edismax.xml') as f:
    data = "<root>{}</root>".format(f.read())

with open("configoverlay.json") as f:
    overlay = json.load(f)

update_keys = dict([ (x.attrib.get('name'), x.text) for x in etree.XML(data) ])

seldefaults = overlay['requestHandler']['/select']['defaults']

seldefaults.update(update_keys)

with open('configoverlay.json', 'w') as f:
    json.dump(overlay, f)
