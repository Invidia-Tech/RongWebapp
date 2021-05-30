from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
import requests
import UnityPy
import os
import os.path
import time
import sqlite3
import json
from contextlib import closing
import brotli
import time


def _iterdump(connection, table_name, schema_name):
    """
    Returns an iterator to the dump of the database in an SQL text format.

    Used to produce an SQL dump of the database.  Useful to save an in-memory
    database for later restoration.  This function should not be called
    directly but instead called from the Connection method, iterdump().
    """

    cu = connection.cursor()
    table_name = table_name

    # sqlite_master table contains the SQL CREATE statements for the database.
    q = """
       SELECT name, type, sql
        FROM sqlite_master
            WHERE sql NOT NULL AND
            type == 'table' AND
            name == :table_name
        """
    schema_res = cu.execute(q, {'table_name': table_name})
    for table_name, type, sql in schema_res.fetchall():
        if table_name == 'sqlite_sequence':
            yield('DELETE FROM sqlite_sequence;')
        elif table_name == 'sqlite_stat1':
            yield('ANALYZE sqlite_master;')
        elif table_name.startswith('sqlite_'):
            continue
        else:
            yield(('%s;' % sql).replace("'", '"').replace('"%s"' % table_name, '"%s"."%s"' % (schema_name, table_name)))

        # Build the insert statement for each row of the current table
        table_name_ident = table_name.replace('"', '""')
        res = cu.execute("PRAGMA table_info('%s')" % table_name)
        column_names = [str(table_info[1]) for table_info in res.fetchall()]
        q = """SELECT 'INSERT INTO "{4}"."{0}" VALUES({1})' FROM "{0}" ORDER BY {2} ASC, {3} ASC; """.format(
            table_name_ident,
            ", ".join("""'||quote("{0}")||'""".format(
                col.replace('"', '""')) for col in column_names),
            column_names[0],
            column_names[1] if len(column_names) > 1 else column_names[0],
            schema_name)
        query_res = cu.execute(q)
        for row in query_res:
            yield("{0};".format(row[0]))


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('version', type=str, choices=[
                            'en', 'jp', 'cn'], help='PCRD version to update')
        parser.add_argument('--download', action='store_true',
                            help='Download latest database from PCRD servers')

    def download(self, version):
        # default version
        default_versions = {"en": "10000000", "jp": "0", "cn": "0"}
        truth_version = default_versions[version]

        if os.path.exists('./redive_dbs/truthversion_%s' % version):
            with open('./redive_dbs/truthversion_%s' % version, "r", encoding="utf-8") as f:
                truth_version = json.load(f)

        if version == 'en':
            fails = 0
            test_version = int(truth_version) + 10
            while fails < 20:
                print("[TESTING] %d" % test_version)
                with requests.get('http://assets-priconne-redive-us.akamaized.net/dl/Resources/%d/Jpn/AssetBundles/iOS/manifest/manifest_assetmanifest' % test_version) as r:
                    if r.status_code == 200:
                        print(
                            "[SUCCESS] %d returned status code 200 (valid version)" % test_version)
                        truth_version = str(test_version)
                        fails = 0
                    else:
                        fails += 1
                    test_version += 10
                time.sleep(1.0)

            with requests.get('http://assets-priconne-redive-us.akamaized.net/dl/Resources/%s/Jpn/AssetBundles/iOS/manifest/masterdata_assetmanifest' % truth_version) as rm:
                manifest = rm.text
                dbhash = manifest.split(",")[1]
                print(
                    'http://assets-priconne-redive-us.akamaized.net/dl/pool/AssetBundles/'+dbhash[0:2]+'/'+dbhash)
                with requests.get('http://assets-priconne-redive-us.akamaized.net/dl/pool/AssetBundles/'+dbhash[0:2]+'/'+dbhash) as r2:
                    if r2.status_code == 200:
                        with open("./redive_en.unity3d", "wb") as fh:
                            fh.write(r2.content)
                        env = UnityPy.load('./redive_en.unity3d')
                        for object in env.objects:
                            if object.type == 'TextAsset':
                                data = object.read()

                                with open("./redive_dbs/%s.db" % version, "wb") as fh3:
                                    fh3.write(data.script)
                                    print(
                                        "Successfully downloaded db version %s" % truth_version)
                    else:
                        print("DB version %s: status code %d" %
                              (truth_version, r2.status_code))

            os.remove("./redive_en.unity3d")
        elif version in ['jp', 'cn']:
            with requests.get('https://redive.estertion.win/last_version_%s.json' % version) as rv:
                new_tv = rv.json()["TruthVersion"]
                if new_tv > truth_version:
                    with requests.get('https://redive.estertion.win/db/redive_%s.db.br' % version) as rd:
                        with open("./redive_dbs/%s.db" % version, "wb") as fh3:
                            fh3.write(brotli.decompress(rd.content))
                            truth_version = new_tv

        with open('./redive_dbs/truthversion_%s' % version, "w", encoding="utf-8") as f:
            json.dump(truth_version, f)

    def handle(self, *args, **options):
        # check that the schema exists
        with connection.cursor() as cur:
            schema_name = 'redive_%s' % options['version']
            cur.execute("SELECT EXISTS(SELECT FROM information_schema.schemata WHERE schema_name = %s)", [
                        schema_name])
            if not cur.fetchone()[0]:
                # try to create it, error if not possible
                cur.execute("CREATE SCHEMA {0}".format(schema_name))

            # download new database if asked
            if options['download']:
                self.download(options['version'])

            # check for database presence
            if not os.path.exists('./redive_dbs/%s.db' % options['version']):
                raise CommandError(
                    "Database file not present for %s (try --download)" % options['version'])

            with open('./redive_dbs/truthversion_%s' % options['version'], "r", encoding="utf-8") as f:
                truth_version = json.load(f)

            print("Attempting to install %s database, truth version %s..." %
                  (options['version'], truth_version))

            # check if already on this version
            try:
                cur.execute(
                    'SELECT truth_version FROM "{0}"."__current_version"'.format(schema_name))
                if cur.fetchone()[0] == truth_version:
                    print(
                        "Truth version %s already installed. Skipping install." % truth_version)
                    return
            except:
                # table doesn't exist or has no row, whatever really, just continue to apply it
                pass

            # apply downloaded database
            # start by temporarily dropping foreign keys to its schema
            start_time = time.time()

            cur.execute("""
SELECT
    tc.table_schema, tc.table_name, kcu.column_name,
	ccu.table_schema AS foreign_schema_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
	tc.constraint_name
FROM
    information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage 
        AS kcu ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage 
        AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY' AND ccu.table_schema = %s;
            """, [schema_name])
            fkeys = list(cur.fetchall())

            for fkey in fkeys:
                cur.execute(
                    "ALTER TABLE {0}.{1} DROP CONSTRAINT {6}".format(*fkey))

            try:
                # convert database
                # start by dropping all tables
                cur.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = %s", [schema_name])
                for row in cur.fetchall():
                    cur.execute("DROP TABLE {0}.{1}".format(
                        schema_name, row[0]))

                # now move over sqlite data
                with sqlite3.connect('./redive_dbs/%s.db' % options['version']) as sqlite_conn:
                    sqlite_conn.row_factory = sqlite3.Row
                    with closing(sqlite_conn.cursor()) as sqlite_cur:
                        sqlite_cur.execute(
                            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
                        tables = [row["name"] for row in sqlite_cur.fetchall()]
                        for table in tables:
                            for line in _iterdump(sqlite_conn, table, schema_name):
                                cur.execute(line)

                # insert record of truth version to skip importing later
                cur.execute(
                    'CREATE TABLE "{0}"."__current_version" ("truth_version" TEXT);'.format(schema_name))
                cur.execute('INSERT INTO "{0}"."__current_version" ("truth_version") VALUES(%s)'.format(
                    schema_name), [truth_version])
            finally:
                # add back fkeys when done
                for fkey in fkeys:
                    cur.execute(
                        "ALTER TABLE ONLY {0}.{1} ADD CONSTRAINT {6} FOREIGN KEY({2}) REFERENCES {3}.{4}({5}) DEFERRABLE INITIALLY DEFERRED".format(*fkey))

            end_time = time.time()
            print("Install complete, took", round((end_time-start_time) * 1000), "ms")
