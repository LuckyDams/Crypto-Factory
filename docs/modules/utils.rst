.. _utils-module:

Utilities
=========

**Crypto utilities** are available within the Crypto-Factory interface through
the ``utils`` property. Based on the ``CryptoUtils`` class which consists of
a collection of static or class methods only. Therefore, they can be used
without the need to instantiate an object.


Current features are:
    - generate random keys
    - normalize, get, remove & compare tags
    - string/bytes conversion


Usage::

    >>> cf.utils.generate_key(size=256, urlsafe=True)
    b'...='
    >>> data = cf.encrypt('My_Secret', 'fernet')
    >>> cf.utils.get_tag(data)
    'TAG'
    >>> cf.utils.compare_tag(data, 'TAG')
    True
    >>> cf.utils.data_bytes(data, encoding='utf-8', errors='strict')
    b'TAG$...=='



For details, check relative :ref:`API <api-utils>` documentation.
