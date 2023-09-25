# TRLN Discovery Shared Bibliographic Solr configuration

Defines the primary shared index for bibliographic records used by the TRLN
Discovery project.

Heavily inspired by https://github.com/billdueber/solr6_test_conf

Incorporates plugins from https://github.com/mlibrary/umich_solr_library_filters
and https://github.com/sul-dlss/CJKFilterUtils

## TRLN Discovery Solr Configs

This directory contains Solr ConfigSets for various indexes.

Each ConfigSet describes a collection, including the index schema and various
'handlers' that affect the behavior of the collection when queried.  In
general, changes to a ConfigSet should be tested somewhere, then committed to a
shared Git repository, before they are sent to production Solr.

## Managing ConfigSets via ZooKeeper

Since we run Solr in "SolrCloud" mode, the configuration of each collection is
managed through ZooKeeper.  Solr ships with an 'embedded' ZooKeeper instance
that includes a `zkcli.sh` script for communicating with ZooKeeper; such a
script is also available from the standalone ZooKeeper distribution, but the
one in a Solr distribution seems to work best. 

Solr-specific documentation is kept in the "Solr Reference Guide" which changes
from version to version, here is a link to the v7.2 reference guide:

https://lucene.apache.org/solr/guide/7_2/command-line-utilities.html

### A note about updating configsets

If a configuration contains 'overlay' files (e.g. `configoverlay.json` that store the same
values as ones that are also found in, e.g. `solrconfig.xml`, then those values will override
whatever is stored in `solrconfig.xml`.  In general we are trying to avoid doing this, as JSON
has formatting requirements (no multiline strings) that make it hard to maintain
configurations this way.  Note that using Solr's "web" API to manage the configuration *will* automatically create `configoverlay.json` so please don't mix and match that API with direct ZK management of the configuration.

If you do, please note that Zookeeper's `upconfig` command copies new files and updates ones previously stored, but does *not* _delete_ any files that you have removed from the directory you upload.  If you do run into a situation where the configoverlay.json (or other file) is present, and you want to delete it, look at the `clear` command offered by the ZooKeeper client; it will delete individual named files as well as directories.

The `coparse.py` script in this directory is an historical artifact created before we'd figured out
all the above, but if you eventually decide you want to edit the XML config and copy the changes to `configoverlay.json` (e.g. so you can manage some changes via the web API but also continue to use ZooKeeper), it will help 
automate this process for you.

### `zkcli.sh` examples at a glance.

For a running Solr instance, it will typically have a `SOLR_HOME` which will
usually be something like `/opt/solr/server`, and you can usually find
`zkcli.sh` under `$SOLR_HOME/scripts/cloud-scripts`.

In general, though, you should expect to run these scripts from a different host specifically
set up to do management tasks, so the "ansible master" host is a good one to use.  To that end,
we've created some Ansible tasks to run some of the fiddly details for you.  Since some of the tasks
are used to deploy Solr, it turns out that we have a handy Solr distribution we can unpack 
and use to call `zkcli.sh` scripts.

### Downloading the current configuration for a collection:

You need to be able to 'talk to' the ZooKeeper instance Solr is using; in general, for TRLN Discovery services, that means you need to run these from a host in the same VPC, and moreover one that can talk to ZooKeeper -- once again the management console (ansible) node is a good one to use.  If you are doing this so that you can copy the configsets down to your local machine, you can zip up the directory created by the commands and `scp` them to another machine.

You might need to do the above if the configuration in this repository somehow gets out of synch with the configuration in ZooKeeper.

#### 'embedded' Solr on the same machine, running standalone SolrCloud

    $ $SOLR_HOME/scripts/cloud-scripts/zkcli.sh -zkhost localhost:9983 -cmd downconfig -confname trlnbib -confdir trlnbib

Notes:

  * `zkhost` is a comma-separated list hostname:port pairs of *all* the zookeeper nodes in the cluster; the example has a single ZK node
  * `-cmd downconfig` says you want to copy the configuration to your machine
  * `-confname` is the name of the configuration  (collection)
  * `-confdir` is the path (on the machine where you are running the command)
    to which the configuration will be downloaded.  May be absolute or relative
    to the current working directory.

#### Remote SolrCloud with standalone ZooKeeper cluster from a management host

This assumes we have multiple ZK hosts; uploading the configset to any of the Solr nodes attached to the same ZK cluster
will propagate the changes across the cluster.

    $ $SOLR_HOME/scripts/cloud-scripts/zkcli.sh -zkhost zk1:2181,zk2:2181,zk3:2181 -cmd downconfig -confname trlnbib -confdir trlnbib

Note that the values of zkhost here have to be resolvable hostnames, so you should have already set up your `/etc/hosts` file for this to work.

#### Uploading a new config

See above, but swap `-cmd downconfig` for `-cmd upconfig`

### ConfigSet

  * `trlnbib`: the 'main' TRLN shared bibliographic record index
 - this is the one used by Blacklight 

## Ansible Tasks

Assuming this directory lives alongside the main `ansible` directory, the `solr_indexes.yml` playbook in the 
Ansible directory can be run to upload the configsets and create the collections on the SolrCloud cluster.

Super short answer:

    $ ansible-playbook solr_indexes.yml -e 'update_configsets=["trlnbib"]'
    
calls 'upconfig` on the contents of the `trlnbib` directory below this file and sends it to ZooKeeper, then reloads the collection.  See the Ansible documents in Confluence for more about this.
