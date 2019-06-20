.. _exceptions-module:

Exceptions
==========

The ``CryptoFactoryError`` Exception class is used to catch errors raised by
underneath Crypto providers (based on different libraries). In such
implementation, managing exceptions on the client side is simplified.

**Example**::

    >>> cf.decrypt('BAD_DATA', mode='aes')
    Traceback (most recent call last):
    ...
    binascii.Error: Incorrect padding

    # Then followed by...
    Traceback (most recent call last):
    ...
    ValueError: Invalid key or string

    # Finally caught by CryptoFactoryError...
    Traceback (most recent call last):
    ...
    CryptoFactoryError: Unable to decrypt with Crypto service: aes


**Usage**::

    >>> from crypto_factory.exceptions import CryptoFactoryError
    >>> try:
    ...     cf.decrypt('BAD_DATA', mode='aes')
    ... except CryptoFactoryError as err:
    ...     print("CryptoFactory error: {0}".format(err))
    ...
    CryptoFactory error: Unable to decrypt with Crypto service: aes

For details, check relative :ref:`API <api-exceptions>` documentation.
