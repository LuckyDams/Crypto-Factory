.. _interface-module:

Interface
=========

``CryptoFactory`` is the main client interface to access all Crypto-Factory
features. Its principal role is to offer common methods to execute cryptography
tasks from different Crypto providers (or implementations).

Also, it provides 'synthetic' methods for advanced features such as data tagging
mechanism or ability to rotate between keys and encryption algorithms.

As the client interface, it has entry-points to manage underneath Crypto
providers, to consume several utilities or helpers, and to access templates for
building your own Crypto services.


Features
--------

    - **Crypto services management** (See ``factory`` module.)

    - Abstraction **methods for encryption**; rely on underneath Crypto
      services (See ``providers`` module.)

    - **Tagging** mechanism

    - **Advanced method(s)** such as ``rotate`` to migrate encrypted data
      to another Crypto service

    - **Crypto utilities** such as generate random keys and strings, inspect
      tags or encoding functions (See ``utilities`` module.)

    - **Built-in Crypto providers** for direct use of defined encryption
      algorithms (See ``providers`` module.)

    - **Crypto templates** for building your own encryption algorithms
      (See ``providers`` module.)




For details, check relative :ref:`API <api-interface>` documentation.
