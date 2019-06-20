.. _templates-module:

Templates
=========

In order to design your own cryptography recipes, you will need:
    - One or more **builder(s)** based on the ``CryptoBuilder`` class to
      initialize a service.
    - One **service** based on ``CryptoService`` class to provide cryptography
      methods (encrypt/decrypt).


**Usage**::

    from crypto_factory import CryptoFactory
    from crypto_factory.templates import CryptoBuilder, CryptoService

    cf = CryptoFactory()

    class MyBuilder(cf.CryptoBuilder):
        service = MyService

        @staticmethod
        def initialize(key=None):
            ...
            cipher = MyCryptoRecipe(key)
            return cipher

    class MyService(cf.CryptoService):

        def encrypt(self, data):
            ...
            enc = self.cipher.encrypt(data)
            return enc

        def decrypt(self, data):
            ...
            plain = self.cipher.decrypt(data)
            return plain

    cf.register(config={key: '...'}, sid='MyID', builder=MyBuilder, tag=...)
    cf.encrypt('My_Secret', 'MyID')


Please note **Built-in providers** can also be sub-classed in order to
personalized their behaviour.
(See :ref:`this note <provider-subclassing>` from ``AESServiceBuilder``)


.. _memory-warning:

.. warning::
    A note about **sensitive data in memory**:

    Sensitive data like keys or any Crypto service parameters are loaded in
    memory when a builder instantiate the service (``register`` method from
    ``factory`` class). They will live in memory until the service is
    unregistered. Depending on your environment, this can be considered as a
    security vulnerability (in case of malicious memory dump).

    In the same way, if your encryption algorithm (cipher) is created in the
    builder ``initialize`` method, it will live as long as the service is
    available. For lower exposure, the cipher creation can be implemented in
    the Crypto Service methods (``encrypt`` & ``decrypt`` or a dedicated
    method on your own). Therefore, it will only live on demand upon ``get``
    method call from ``factory`` class (at the cost of creating it each times).

    Please also note, there is no memory clearing process implemented in
    ``Crypto-Factory`` as there is no reliable solution in Python.
    For more details, check
    https://cryptography.io/en/latest/limitations/?highlight=memory.


.. note::
    For implementation details, check relative :ref:`API <api-templates>`
    documentation. Also, Crypto built-in builders and services from the ``providers``
    module can be reviewed as real use cases.
