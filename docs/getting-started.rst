.. _getting-started:

===============
Getting started
===============

Welcome! This section is an overview of Crypto-Factory; for further details,
see the documentation for each modules and the API doc section.


Introduction
============

Main purpose of Crypto-Factory library is to provide a **common interface**
to application for cryptographic tasks.

Based on Factory method design pattern, it provides an abstraction layer to
define cryptographic recipes as service providers, a **'factory' manager** to
register and create individual instances, and a standardized client interface
to interact with them.
With this approach, implementing existing or new cryptographic methods is
simplified, more reusable and easier to maintain.

Crypto-Factory does not provide any Cryptographic algorithms on its own but
relies on existing Python packages such as
`pyca/cryptography <https://github.com/pyca/cryptography>`_ which is used to
define some **built-in Crypto providers**. These providers can be used as a
quick starter or samples for dedicated implementations.
For this purpose, **Templates** class are also available to design your own
recipes using your preferred cryptography packages.


Quick start
===========
::

    # Import  & initialize
    >>> from crypto_factory import CryptoFactory
    >>> cf = CryptoFactory()

    # Define your Crypto providers configuration
    >>> conf_AES = {
    ...     # existing service
    ...     'key' : b'WkqHg8m9RwmE1iPQJAbuJRKmh72vLvUNFepIWrOldKg=',
    ...     'iv'  : b'vdU1T6NvAZJIlnznSe8gbQ==',
    ... }


    >>> new_key = cf.utils.generate_key()
    >>> conf_Fernet = {
    ...     # new service
    ...     'id' : 'new',
    ...     'builder' : 'FernetServiceBuilder',
    ...     'tag' : 'FERNET_TAG',
    ...     'key' : new_key,
    ... }

    # Register both providers
    >>> cf.services.register(
    ...     conf_AES,
    ...     sid='aes',
    ...     builder='AESServiceBuilder',
    ...     tag="AES_TAG",
    ... )
    'aes'

    >>> new_mode = cf.services.register(conf_Fernet)
    >>> print(new_mode)
    'new'

    # Encrypt data
    >>> old_secret = cf.encrypt('My_Secret', mode='aes', tag=False)
    >>> new_secret = cf.encrypt('My_Secret', new_mode)

    # Decrypt data
    >>> cf.decrypt(old_secret, mode='aes')
    'My_Secret'

    >>> cf.decrypt(new_secret)  # (mode is not required with tagging)
    'My_Secret'

    # Decrypt wrong hash
    >>> cf.decrypt(old_secret, mode='new')
    Traceback (most recent call last):
    ...
    CryptoFactoryError: Unable to decrypt with Crypto service: new

    # Rotate cipher from one or more modes to a target one (migration)
    >>> secret = cf.rotate(old_secret, from_modes=['aes', ], to_mode='new')
    >>> cf.decrypt(secret, mode='new')
    'My_Secret'



Features
========

Current implemented features are:

**Client interface**:
    Symmetric encryption: encrypt, decrypt, rotate.

**Factory** (Services manager):
    To register and call Crypto service providers.

**Built-in Crypto providers**:
    Services for AES & Fernet encryption.
    (can be used as quick starter or samples to define your own recipes)

**Tagging mechanism**:
    Tag encrypted data to identify provider ; can be enforced or disabled.

**Utilities & helpers**:
    Manage tags & providers, generate random keys, string encoding, ...

**Exceptions**:
    Single `CryptoFactoryError` class to catch errors.
    (basic implementation to simplify errors management on client side)

**Templates**:
    Base classes to implement a Crypto services and its related builder(s).


Install
=======

Crypto-Factory is best installed via `pip <http://pip-installer.org>`_::

    $ pip install Crypto-Factory


Or cloning the Git repository and running within it::

    $ pip install -e .


Dependencies
============

In order for Crypto-Factory's installation to succeed, you will need the following:

* `Python <https://www.python.org/downloads/>`_ programming language, versions 3.4+
* `Attr-Dict <https://pypi.org/project/Attr-Dict/>`_ and
  `cryptography <https://pypi.org/project/cryptography/>`_ libraries
