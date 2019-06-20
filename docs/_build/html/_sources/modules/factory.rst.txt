.. _factory-module:

Factory
=======

The "factory" is responsible for managing Crypto providers. It is available
within the Crypto-Factory interface through the ``services`` property.

Its principal duties are:

    - **register** and initialize Crypto services through their associated
      builders.

    - **get** a Crypto service to provide implementation of an interface method
      (encrypt/decrypt).

    - maintain index of active Crypto **providers** and associated **tags**.

    - provide helpers to list built-in providers, and get active service
      details.


**Usage**:

Helpers for built-in providers::

    >>> cf.services._builtins                               # doctest: +ELLIPSIS
    {'AESServiceBuilder': <class '...AESServiceBuilder'>,
     'DummyServiceBuilder': <class '...DummyServiceBuilder'>,
     'FernetServiceBuilder': <class '...FernetServiceBuilder'>}
    >>> help(cf.services._builtins.FernetServiceBuilder)    # doctest: +ELLIPSIS
    Help on class FernetServiceBuilder in module crypto_factory.providers:
    ...

Crypto provider registration::

    >>> cf.services.register(config={'key' : b'...='}, sid='fernet',
    ...                      builder='FernetServiceBuilder', tag='FERNET')
    >>> # or
    >>> conf_Fernet = {'id'      : 'fernet',
    ...                'builder': 'FernetServiceBuilder',
    ...                'tag'     : 'FERNET',
    ...                'key'     : b'...=',
    ...                }
    >>> cf.services.register(conf_Fernet)


Index of active providers::

    >>> cf.services.providers
    {'fernet':
      {'id': 'fernet',
       'builder': <FernetServiceBuilder object at 0x...>,
       'tag': 'FERNET'}, ...
    }
    >>> cf.services.providers.fernet.tag
    'FERNET'
    >>> cf.services.providers.fernet.builder.args_in_fct
    ['key']
    >>> cf.services.providers.fernet.builder.features
    ['decrypt', 'encrypt']

Index of tags::

    >>> cf.services.tags
    {'FERNET': {'id': 'fernet}, ...}

Deregister a provider::

    >>> cf.services.register(sid='fernet')
    >>> cf.services.providers.fernet
    {'id': 'fernet', 'builder': None, 'tag': None}

For details, check relative :ref:`API <api-factory>` documentation.
