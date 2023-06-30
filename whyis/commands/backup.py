# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask
from pathlib import Path
import os
import csv
import rdflib
from depot.manager import DepotManager

nanopub_search_query = '''
select distinct ?resource (coalesce(?modified,?created) as ?mod) where {
  ?resource a np:Nanopublication.
  ?resource np:hasAssertion ?assertion.
  ?assertion dc:created ?created.
  optional {
        ?assertion dc:modified ?modified.
  }
} order by ?resource'''

import datetime
import pytz

utc=pytz.UTC

class Backup(Command):
    '''Backup the graph to an archive. Synchronizes against previously saved backups.'''

    def get_options(self):
        return [
            Option ('-a', '--archive', dest='output_directory', help='Backup path', required=True, type=str),
        ]

    def run(self, output_directory):
        app = flask.current_app
        from pydoc import locate
        Path(output_directory).mkdir(parents=True, exist_ok=True)
        nanopub_backup_dir = os.path.join(output_directory,'nanopublications')
        file_backup_dir = os.path.join(output_directory,'files')
        Path(nanopub_backup_dir).mkdir(parents=True, exist_ok=True)
        Path(file_backup_dir).mkdir(parents=True, exist_ok=True)
        DepotManager.configure('backup_files', {
            'depot.storage_path': file_backup_dir
        })
        backup_files = DepotManager.get('backup_files')
        DepotManager.configure('backup_nanopublications', {
            'depot.storage_path': nanopub_backup_dir
        })
        backup_nanopubs = DepotManager.get('backup_nanopublications')
        nanopub_list_file = os.path.join(output_directory,'nanopub_index')
        nanopub_to_fileid = {}
        new_nanopubs = set()
        if os.path.exists(nanopub_list_file):
            print("Loading Nanopub List...")
            with open(nanopub_list_file) as csvfile:
                reader = csv.reader(csvfile, delimiter="\t")
                nanopub_to_fileid = dict([(x[0],x[1]) for x in reader])

        with open(nanopub_list_file,'w') as index_file:
            nanopub_list = csv.writer(index_file, delimiter="\t")
            for np_uri, last_modified in app.db.query(nanopub_search_query, initNs=app.NS.prefixes):
                nanopub_uri = str(np_uri)
                fileid = nanopub_to_fileid.get(nanopub_uri, None)
                if fileid is None:
                    nanopub = app.nanopub_manager.get(np_uri)
                    npg = rdflib.ConjunctiveGraph(store=nanopub.store)
                    quads = npg.serialize(format="trig")
                    np_uri.split('/')[-1]
                    fileid = backup_nanopubs.create(quads.encode('utf8'),
                                                    nanopub_uri.split('/')[-1]+'.trig',
                                                    "application/trig")
                else:
                    fileinfo = backup_nanopubs.get(fileid)
                    if last_modified.value > fileinfo.last_modified.replace(tzinfo=utc):
                        # Update if changed.
                        nanopub = app.nanopub_manager.get(np_uri)
                        quads = nanopub.serialize(format="trig")
                        np_uri.split('/')[-1]
                        fileid = backup_nanopubs.replace(fileinfo, quads,
                                        fileinfo.filename, "application/trig")
                # Add to the new index one way or another.
                nanopub_list.writerow([np_uri, fileid])
                new_nanopubs.add(str(np_uri))

                print("Backed up ",len(new_nanopubs)," nanopublications...\r",end='',flush=True)
            print('\n',flush=True)
            print("Deleting old nanopublications...",flush=True)
            # Now remove the nanopubs that have been deleted from the graph.
            for np_uri in nanopub_to_fileid.keys() - new_nanopubs:
                backup_nanopubs.delete(nanopub_to_fileid[np_uri])

        file_ids = app.file_depot.list()
        real_file_ids = set()
        for i, file_id in enumerate(file_ids):
            try:
                f = app.file_depot.get(file_id)
                real_file_ids.add(file_id)
                if not backup_files.exists(file_id):
                    backup_files.replace(f, f)
                else:
                    fileinfo = backup_files.get(file_id)
                    if f.last_modified.replace(tzinfo=utc) > fileinfo.last_modified.replace(tzinfo=utc):
                        backup_files.replace(f, f)
            except IOError:
                # Looks like this one's missing.
                pass
            print("Backed up ",i+1," files...\r",end='',flush=True)
        print('\n',flush=True)
        print("Deleting old files...")
        backed_up_ids = set(backup_files.list())
        for file_id in backed_up_ids - real_file_ids:
            backup_files.delete(file_id)

        print('Backing up admin database...')
        app.admin_db.serialize(os.path.join(output_directory,'admin_graph.jsonld'), format="json-ld")

        print("Complete!")
