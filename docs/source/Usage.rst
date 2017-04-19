Usage
=====

Getting started
^^^^^^^^^^^^^^^

Installation
------------

Without django:

.. code-block:: python

  pip install devour --install-option='--no-django'

With django:

.. code-block:: python

  pip install devour


Configuration
-------------

Devour connects to your Kafka client using settings defined by a variable named `KAFKA_CONFIG`. If you're using a pure python implementation, devour assumes that this setting is in a file called `settings.py` at the root of your application. If you're settings have a different name or location, you have the option of setting an environment variable `KAFKA_SETTINGS_PATH` that contains the path to your settings file, starting from the root of your application to the module name.
If you're using devour with django, you should define this within whatever file is specified by `DJANGO_SETTINGS_MODULE`.


.. py:data:: KAFKA_CONFIG

  The following options are validated for you when the client handler is first instantiated within a process/thread. A `DevourConfigException` is thrown when a validation error is encountered.

  .. py:attribute:: dict

    - Contains all cluster specific settings
    - `key` is the attribute name and `value`
      is the value

    :param str hosts: Comma separated list of Kafka hosts (required)
    :param str zookeeper_hosts: Comma separated list of zookeeper hosts
    :param dict ssl_config: Specifies SSL config

      - `cafile` - Path to cafile within your filesystem (required)
      - `certfile` - Path to certfile within your filesystem
      - `keyfile` - Path to keyfile within your filesystem
      - `password` - Password corresponding to your keyfile

    :param int socket_timeout_ms: Amount of time (ms) before socket times out during network requests
    :param int offsets_channel_socket_timeout_ms: Amount of time (ms) before socket times out while reading responses for offset commit and offset fetch requests
    :param bool use_greenlets: Use greenlets vs OS threads for parallel operations
    :param bool exclude_internal_topics: Whether messages from internal topics (specifically, the offsets topic) should be exposed to the consumer
    :param str source_address: Source address for socket connections
    :param str broker_version: The Kafka protocol version of the cluster being used. *Note:* If this version does not match the actual broker version, some feature may not work.

    Also included in the config is a key called `consumer_routes`. This particular setting contains the routes
    to the consumers that you define.

    * **consumer_routes (dict)** `key` is the desired name of the consumer, and the `value` is the relative route from the root of your application to the declared consumer class.

    .. code-block:: python

      #...snip
      'consumer_routes' : {
          'my_consumer': 'my_proj_root.path.to.consumer_module.ConsumerClass'
      },
      #...snip


.. envvar:: KAFKA_SETTINGS_PATH

  .. code-block:: bash

    export KAFKA_SETTINGS_PATH='my_proj_root.path.to.settings_module'


Consumers
^^^^^^^^^

Building a consumer with devour is as simple as writing a class that inherits from `DevourConsumer` and defining
reusable config. The crux of the consumer is the `digest` method. This method is the entry point where devour
passes each message received from the Kafka topic. All of this is kicked off by running the `consume` command that
starts the consumer and connects to Kafka in its own process.

.. seealso::

  Setting up your consumers also requires defining your consumer routes. See the configuration section for details


.. py:class:: DevourConsumer

  .. py:module:: devour.consumers.DevourConsumer

  .. py:method:: digest(self, offset, *args, **kwargs)

  .. py:attribute:: topic

  .. py:attribute:: digest_name

  .. py:attribute:: consumer_type

  .. py:attribute:: config

  .. py:attribute:: schema_class

  .. py:attribute:: dump_raw

  .. py:attribute:: dump_obj

  .. py:attribute:: dump_json


Example

.. code-block:: python

  from devour.consumers import DevourConsumer

  class ExampleConsumer(DevourConsumer):
    pass


Django
------

If you're pairing devour with django, consumer syntax is the same across the board. The only
difference is the command used start the consumer process. For that, devour includes a custom
management command. This seems subtle, but is actually very useful. This allows you to set up
your consumers *within* your django project, enabling you to utilize your existing django models
and database setup.

**Command:**

.. code-block:: bash

  ./python manage.py consume consumer_name



Producers
^^^^^^^^^

With devour, producers are created in similar fashion to how consumers are created. Simply
create a producer class inherited from `Producer`, and define it's configuration. The difference
here is how the configuration is defined. For producers configuration is done using a nested class
you define called `ProducerConfig`. When a producer's `produce` method is called, the configuration
is used to format and produce a message to your desired topic. The `Producer` class also provides
a set of customizable methods to help you write logic that produces a message tailored to the event
that is triggering it.

.. py:class:: devour.producers.Producer

  .. py:method:: produce(self, event=None, source=None, extras={}, context={})

  .. py:method:: get_topic(self, event, source, context)

  .. py:method:: get_schema(self, event, source, context)

  .. py:method:: get_partition_key(self, event, source, context)

  .. py:method:: _get_generic_topic(self, identifier='topic')

  .. py:class:: ProducerConfig

    .. py:attribute:: topic

    .. py:attribute:: partition_key

    .. py:attribute:: schema_class

    .. py:attribute:: producer_type


Django
------

Using devour producers with django is extremely useful. Devour provides
class `ProducerModel` that allows you to turn your desired models into producers. To do so
either replace the `models.Model` inheritance with `ProducerModel` for an existing model
or inherit from `ProducerModel` if you're writing your model from scratch. Then declare your
nested `ProducerConfig` class with desired options. When your django app is started, devour registers two signals
automatically: `post_save` and `post_delete`. When these signals are triggered on a model
that inherits from the `ProducerModel` class, the `produce` method will be called. Bam,
the current state of your model is produced to your desired topic.

.. seealso::

  The ProducerModel class takes all of the same parameters and has all of the same customizable
  methods as the Producer class, so see that section for specifics.

.. py:class:: devour.django.models.ModelProducer

In addition to the customizable methods provided by the `Producer` class, devour's `ProducerModel` allows
you to pass additional keyword arguments through your `save` and `delete` calls to give you control over what and
when your producers produce messages.

  **produce** (bool, default=True) - Allows you to trigger or suppress a message from your producer. If your producer config has `auto_produce` set to `True`, passing `produce=False` into `save` or `delete` will suppress messages being produced for each of those events, while passing in `produce=True` when `auto_produce` is `False` on your producer will trigger a message.

  **produce_context** (dict) - Data that gets passed into each of the customizable methods provided by the `producer`. This can be helpful when making decisions within those methods and additional context about where this message is being produced from is needed.

  **produce_extras** (dict) - Any extra data that you'd like to be included in the message being produced can be passed in with this dict. **Note:** Any extras that are passed in that have identical keys to fields on the model that is being produced, will override those field's values on the model.

.. note::

  For each message produced from the `ProducerModel`, devour will determine an `event` value (create, update, or delete)
  and automatically add it to the message being produced.


Schemas
^^^^^^^


Django
------
