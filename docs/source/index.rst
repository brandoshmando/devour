.. devour documentation master file, created by
   sphinx-quickstart on Wed Mar 22 10:13:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Devour
======

Before we dive in, I want to give a shout out to the people at Parsely who wrote pykafka,
of which this package is largely built on top of. If you aren't familiar with pykafka, take some time to familiarize
yourself as all of the low level configuration for your consumers and producers will be done via pykafka.

Devour was created with the intention of helping
python developers build Kafka consumers and producers in a more efficient and
reusable way. With Devour, building your Kafka components is a simple as
declaring a class with specific configuration. One of the key components
of devour is the ClientHandler. The ClientHandler is a 'just in time' wrapper around
the pykafka.Client class. The client isn't configured until the first time a consumer or
producer is fetched. After the first fetch, the client and any kafka components are
persisted until the current thread/process dies. This means that expensive operations
such as configuring the client or a producer aren't done until absolutely needed,
and only done once allowing you to persist these components per process/thread.




Roadmap
^^^^^^^

* Vast improvement of docs...
* Logging
* Python 3.x compatibility

Caveats
^^^^^^^

* caveat


.. toctree::
  :maxdepth: 3

  Concepts
  Usage
