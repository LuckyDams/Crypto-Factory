# -*- coding: utf-8 -*-
"""
templates
---------

This module contains ``CryptoBuilder`` & ``CryptoService`` parent classes to use when designing a Crypto provider.
"""

# TODO: Update docstrings
# TODO: Rework templating to improve user implementation


__all__ = [
    'CryptoBuilder',
    'CryptoService',
]


import inspect


class CryptoBuilder:
    """
    Template to design a **Crypto Builder**. Main purpose is to define an
    ``initialize`` method to assign to a Crypto Service.

    This Crypto Service must be designated in the ``service`` class attribute.

    By default, the ``initialize`` method will forward all parameters received by
    the ``register`` command as a dict. This method can be personalised to fulfill
    the needs of the implemented cryptography recipe.

    All defined Crypto Builders must inherit from the ``CryptoBuilder`` class.

    Example::

        class MyBuilder(CryptoBuilder):
            service = MyService

            @staticmethod
            def initialize(key=None):
                ...
                cipher = MyCryptoRecipe(key)
                return cipher

    Note:
        See this **warning** on :ref:`sensitive data in memory <memory-warning>`.
    """
    service = None

    def __init__(self):
        self.__instance = None
        self.args_present = None
        self.args_in_fct = None
        # self.args_required = None
        self.features = None
        self.service = self.__get_service()

    def __call__(self, **kwargs):

        if not self.__instance:
            # Update self.attrs
            self.args_present = list(kwargs.keys())
            # self.features = [x for x in dir(self.service) if
            #                  not x.startswith("__") and hasattr(getattr(self.service, x), "__call__")]
            self.features = [f[0] for f in inspect.getmembers(self.service, inspect.isfunction) if not f[0].startswith('_')]

            # Define available args for init
            sig = inspect.signature(self.initialize)
            self.args_in_fct = [x.name for x in sig.parameters.values()]
            # self.args_required = [x.name for x in sig.parameters.values() if x.empty == inspect.Parameter.empty]
            params = dict([x for x in kwargs.items() if x[0] in self.args_in_fct])

            # Initialize service
            config = self.initialize(**params)
            if config and self.service:
                self.__instance = self.service(config)
            else:
                raise RuntimeError("Builder initialisation failure, check method and arguments.")

        return self.__instance

    @classmethod
    def __get_service(cls):
        if cls.service:
            return cls.service
        else:
            raise AttributeError("Builder class must have set 'service' attribute")

    @staticmethod
    def initialize(**params):
            return params
        # raise NotImplementedError("Builder class must implement 'initialize' method")


class CryptoService:
    """
    Template to design a **Crypto Service**. Called by an associated builder,
    it must implement abstraction methods from the ``interface`` module
    (encrypt & decrypt).

    By default, ``__init__`` method will provide the **cipher** (config) built
    by the Crypto builder. It can be personalised to fulfill the needs of the
    implemented cryptography recipe.

    All defined Crypto Services must inherit from the ``CryptoService`` class.

    Example::

        class MyService(CryptoService):

            def encrypt(self, data):
                ...
                enc = self.cipher.encrypt(data)
                return enc

            def decrypt(self, data):
                ...
                plain = self.cipher.decrypt(data)
                return plain

    Note:
        See this **warning** on :ref:`sensitive data in memory <memory-warning>`.
    """

    def __init__(self, cipher):
        self.cipher = cipher

    def encrypt(self, data):
        raise NotImplementedError("Service class must implement 'encrypt' method")

    def decrypt(self, data):
        raise NotImplementedError("Service class must implement 'decrypt' method")
