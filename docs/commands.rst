######################################
Using the Whyis command-line interface
######################################

If you're using a Docker container::

  docker exec -it <container name> bash

In Docker, the whyis command is available at `/opt/venv/bin/whyis`.

******************
Running the Server
******************

Commands to run or initialize the server. Run them in an empty directory to
create a new kgapp (knowledge graph application).

:program:`whyis`
  Runs the command `run` ::

    usage: whyis [-?] [backup,createuser,load,init,restore,retire,run,test,runagent,updateuser]

  :-?, --help: show this help message and exit


:program:`whyis run`
  Runs the Flask development server i.e. app.run()::

    usage: whyis run [-?] [-h HOST] [-p PORT] [--threaded]
                     [--processes PROCESSES] [--passthrough-errors] [-d]
                     [-D] [-r] [-R] [--ssl-crt SSL_CRT] [--ssl-key SSL_KEY]
                     [--watch]

  :-?, --help: show this help message and exit
  :-h, --host: The host IP to serve on.
  :-p, --port: The port to serve on.
  :--threaded: Use threading to serve multiple requests.
  :--processes: The size of the process pool.
  :--passthrough-errors:
  :-d, --debug: enable the Werkzeug debugger (DO NOT use in production code)
  :-D, --no-debug: disable the Werkzeug debugger
  :-r, --reload: monitor Python files for changes (not 100% safe for production use)
  :-R, --no-reload: do not monitor Python files for changes
  :--ssl-crt: Path to ssl certificate
  :--ssl-key: Path to ssl key

:program:`whyis init`
  Initialize fuseki. ::

    usage: whyis init [-?]

  :-?, --help: show this help message and exit

********************
Knowledge operations
********************

:program:`whyis load`
  Add a nanopublication to the knowledge graph. ::

    usage: whyis load [-?] -i INPUT_FILE [-f FILE_FORMAT]
                      [-r WAS_REVISION_OF] [--temp-store TEMP_STORE]

  :-?, --help: show this help message and exit
  :-i, --input: Path to file containing nanopub
  :-f, --format: File format (default: trig; also turtle,
                 json-ld, xml, nquads, nt, rdfa)
  :-r, --revises: URI of nanopublication that this is a revision of
  :--temp-store: backing store type to use for temporary graphs; deprecated

:program:`whyis retire`
  Retire a nanopublication from the knowledge graph. ::

    usage: whyis retire [-?] -n NANOPUB_URI

  :-?, --help: show this help message and exit
  :-n, --nanopub_uri: URI of the nanopub to retire



**************
Backup/Restore
**************

These operations can also be used to export knowledge graphs to other systems.

:program:`whyis backup`
  Backup the graph to an archive. Synchronizes
  against previously saved backups. ::

    usage: whyis backup [-?] -a OUTPUT_DIRECTORY

  :-?, --help: show help message and exit
  :-a, --archive: Backup path


:program:`whyis restore`
  Restores a knowledge graph from an archive. ::

    usage: whyis restore [-?] -a INPUT_DIRECTORY

  :-?, --help: show this help message and exit
  :-a, --archive: Backup path

***************
Code Operations
***************

:program:`whyis test`
  Run tests ::

    usage: whyis test [-?] [-v VERBOSITY] [--failfast] [--test TESTS]
                      [--ci] [--apponly]

  :-?, --help: show this help message and exit
  :-v , --verbosity: verbosity level of output, between 0 and 2
                     (default 2)
  :--failfast: Stop the test after the first failure
  :--test: Name of python file (without extension) to run
           tests from, or glob pattern
  :--ci: Analyze coverage and store all results as XML (for CI server)
  :--apponly: Runs the app tests only

:program:`whyis runagent`
  Runs a specified inference agent. ::

    usage: whyis runagent [-?] -a AGENT_PATH [-e ENTITY_URI] [-d]

  :-?, --help: show this help message and exit
  :-a, --agent: Python path (dotted) of agent to use
  :-e, --entity: Entity URI to run against
  :-d, --dry-run: Do not store agent output

********
Accounts
********

:program:`whyis updateuser`
  Update a user in Whyis ::

    usage: whyis updateuser [-?] [-e EMAIL] [-p PASSWORD] [-f NAME]
                            [-l NAME] -u IDENTIFIER [--add-roles ADD_ROLES]
                            [--remove-roles REMOVE_ROLES]

  :-?, --help: show this help message and exit
  :-e , --email: Email address for this user
  :-p, --password: Password for this user
  :-f, --fn: First name of this user
  :-l, --ln: Last name of this user
  :-u, --username: Username for this user
  :--add-roles: Comma-delimited list of roles to add
  :--remove-roles: Comma-delimited list of roles to remove


:program:`whyis createuser`
  Add a user to Whyis ::

    usage: whyis createuser [-?] [-e EMAIL] [-p PASSWORD] [-f FN] [-l LN]
                             -u IDENTIFIER [--roles ROLES]

  :-?, --help: show this help message and exit
  :-e, --email: Email address for this user
  :-p, --password: Password for this user
  :-f, --fn: First name of this user
  :-l, --ln: Last name of this user
  :-u, --username: Username for this user
  :--roles: Comma-delimited list of role names
