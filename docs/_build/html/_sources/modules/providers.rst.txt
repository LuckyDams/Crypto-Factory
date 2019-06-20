.. _providers-module:

Providers
=========

**Built-in Crypto builders** and associated services can be used directly for
a quick integration in your application or can be reviewed as examples
to implement your own cryptography recipes.
(see ``templates`` for details)

They are easily accessible from the ``providers`` property of the Crypto-Factory
interface.


**Usage**:

    >>> mode = cf.services.register(config=dict(key=cf.utils.generate_key()),
    ...                      sid='fernet', builder='FernetServiceBuilder',
    ...                      tag='TAG')
    >>> data = cf.encrypt('My_Secret', mode)
    >>> cf.decrypt(data)
    'My_Secret'


**Available Crypto providers**:

* ``DummyServiceBuilder``:
    Surround data with a label (for illustration purpose only)

* ``FernetServiceBuilder``:
    **Fernet** implementation (secured)
    (https://cryptography.io/en/latest/fernet/)

* ``AESServiceBuilder``:
    **AES-CBC-PKCS7** implementation


.. warning::
    Some providers are only defined for illustration purpose and should not
    be used in real world:

    - ``DummyService`` is only surrounding plain text with a label on ``encrypt``
      action.

    - ``FernetService`` has its cipher instantiated at register time. Therefore,
      it will live in user memory space until the service is unregistered.
      Depending on your environment, this can be considered as a security
      vulnerability (in case of malicious memory dump).

For details on each providers, check relative :ref:`API <api-providers>`
documentation.
