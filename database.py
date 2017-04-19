# -*- coding:utf-8 -*-

import flask_ld as ld
from rdflib import *

def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+"queryEndpoint" in config:
        from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
        store = SPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"])
        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    else:
        graph = ConjunctiveGraph(identifier=defaultgraph)
    return graph



#=============



import sqlite3
import subprocess

from datetime import datetime
import urllib

def init_db():
    conn = sqlite3.connect('update_log.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS update_dates(data_source TEXT, last_update DATETIME)')
    conn.commit()
    conn.close()


#check if data source, if it is, push update.
#unchecked update_date. update_date should be in format yyyy-mm-dd hh:mm seconds optional
#if NO update_date, default is yyyy-mm-dd hh:mm:ss
#if none defaults to current datetime (never checked timezone) -- defaults to  14:43 at 10:43(LOCAL TIME)
def update_date(data_source, update_date=None):
    conn = sqlite3.connect('update_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM update_dates WHERE data_source=?', [data_source])
    if c.fetchone() == None:
        if update_date:
            c.execute('INSERT INTO update_dates VALUES(?,?)', [data_source, update_date])
        else:
            c.execute('INSERT INTO update_dates VALUES(?, DATETIME("NOW"))',[data_source])
    else:
        if update_date:
            c.execute('UPDATE update_dates SET last_update = ? WHERE data_source = ?', [update_date, data_source])
        else:
            c.execute('UPDATE update_dates SET last_update = DATETIME("NOW") WHERE data_source = ?', [data_source])
    conn.commit()
    conn.close()

def does_exist(data_source):
    conn = sqlite3.connect('update_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM update_dates WHERE data_source=?', [data_source])
    if c.fetchone() == None:
        return False
    return True



#returns none if data_source doesn't exist
#returns string date if exists
def get_date(data_source):
    conn = sqlite3.connect('update_log.db')
    c = conn.cursor()
    c.execute('SELECT * FROM update_dates where data_source=?', [data_source])
    fetched = c.fetchone();
    return_val = None
    if fetched:
        return_val = fetched[1]
        return_val = return_val.encode('ascii','ignore')
    conn.close()
    return return_val



#really janky way of checking for updates(place into curation page)

#update_date("dblp", "2015-03-17 00:00:12")
def check_update_dblp():
    url = "http://dblp.uni-trier.de/xml"
    f = urllib.urlopen(url)

    html_text = f.read()
    checked_date = html_text.split('dblp.xml.gz</a></td><td align="right">')[1]
    checked_date = checked_date.split('</td><td')[0]
    checked_date = checked_date.strip()

    last_update = get_date("dblp")

    try:
        conv_last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M")
    except:
        conv_last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")

    try:
        conv_check_time = datetime.strptime(checked_date, "%Y-%m-%d %H:%M")
    except:
        conv_check_time = datetime.strptime(checked_date, "%Y-%m-%d %H:%M:%S")

    if(conv_check_time > conv_last_update):
        return True
    else:
        return False

def update_dblp():
    print "downloading dblp.xml"
    #shell script to download using curl and run setlr.py on the new xml file when finished
    subprocess.call('./update_dblp.sh')
    update_date("dblp")
