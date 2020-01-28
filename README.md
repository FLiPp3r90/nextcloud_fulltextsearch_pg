# Nagios/Icinga monitoring for Nextcloud fulltextsearch app 

## Overview
This is a simple script to monitor the Nextcloud fulltextsearch app in Postgres DB backend.

## Authors

### Main Authors
 - https://github.com/FLiPp3r90 Filip Krahl

## Installation
In your Nagios plugins directory run

<pre><code>git clone https://github.com/FLiPp3r90/nextcloud_fulltextsearch_pg.git</code></pre>

Then use pip to ensure you have all pre-requisites.

<pre><code>pip install -r requirements</code></pre>

## Actions

### connect
A simple connect to postgrs backend. It is a dummy test.

### fts_queue
Checks the documents the table oc_fulltextsearch_indexes resides in Nexcloud database which are not indexed yet.

### fts_errors
Check documents with error in the table oc_fulltextsearch_indexes resides in Nextcloud database.

## Options

- -H, --host      = The hostname of postgres database
- -d, --database  = The nextcloud database the fulltextsearch table is inside
- -u, --user      = The user which has access to nextcloud database
- -p, --password  = The password of nextcloud db user
- -P, --port      = The port of nextcloud database
- -D, --perf-data = Enable output for monitoring performance data (Nagios/Icinga)
- -A, --action    = The action the script should execute
- -w, --warning   = Warning threshold
- -c, --critical  = Critical threshold
