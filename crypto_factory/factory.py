# -*- coding: utf-8 -*-
"""
factory
-------

This module is responsible of managing Crypto providers through the ``CryptoServicesManager`` class.
"""

# TODO: Need solution to import external Builder by name
# TODO: Create a dedicated class to manage tags
# TODO: Create a dedicated class to manage Builders index
# TODO: Create a class to detect built-in and user-defined Builders


__all__ = [
    'CryptoServicesManager',
]


import inspect
from attr_dict import LazyIndex
from .templates import CryptoBuilder
from .utils import CryptoUtils
from .exceptions import CryptoFactoryError


# class CryptoTagsUtility:
#     pass


# class CryptoIndex:
#     """Index for Crypto Services"""
#
#     def __init__(self):
#         self.__providers = LazyIndex()
#         self.__tags = LazyIndex()
#
#     @property
#     def providers(self):
#         return self.__providers.index
#
#     @property
#     def tags(self):
#         return self.__tags.index
#
#     def get_mode(self, sid):
#         """Get Crypto service instance by its identifier"""
#         if sid in self.providers:
#             return sid
#         raise CryptoFactoryError("Unknown or unavailable mode")
#
#     def get_mode_tag(self, sid):
#         """Get Crypto service tag by its identifier"""
#         return self.__providers.get_arg(sid, 'tag')
#
#     def get_tag_mode(self, tag):
#         """Get Crypto service identifier by its tag"""
#         return self.__tags.get_arg(tag, 'id')


# class DefinedBuilders:
#     """
#     DefinedBuilders:
#         Helper class to detect builders builtins in 'providers' module.
#
#     """
#
#     # _locals = [x for x in globals().keys() if x.endswith('Builder')]
#     # locals = {
#     #     'DummyServiceBuilder': DummyServiceBuilder(),
#     #     'AES1ServiceBuilder': AES1ServiceBuilder(),
#     #     'FernetServiceBuilder': FernetServiceBuilder(),
#     # }
#
#     def __init__(self):
#         self.builtins = self.get_builtins
#         self.locals = self.get_locals
#
#     @property
#     def get_builtins(self):
#         import crypto_factory.providers
#         builders = self.__get_builders(crypto_factory.providers)
#         return builders
#
#     @property
#     def get_locals(self):
#         # FIXME: get local builders (sys.modules[__name__] method is not working)
#         import sys
#         builders = self.__get_builders(sys.modules[__name__])
#         return builders
#
#     @staticmethod
#     def __get_builders(module):
#         builders = dict([m for m in inspect.getmembers(module, inspect.isclass)
#                          if m[1].__base__.__name__ == CryptoBuilder.__name__])
#         return builders


# def _get_caller():
#     stack = inspect.stack()
#     module = inspect.getmodule(stack[2][0])
#     return module


def _get_builtins():
    """Function to provide built-in Crypto services builders as a dict of <name>:<class>"""
    import crypto_factory.providers
    builders = dict([
        m for m in inspect.getmembers(crypto_factory.providers, inspect.isclass)
        if m[1].__base__.__name__ == CryptoBuilder.__name__
    ])
    return builders


class CryptoServicesManager:
    """
    CryptoServiceManager is the "factory" class which will manage the Crypto
    providers and will handle calls from the client interface.
    """
    def __init__(self):
        # Create entry-points using LazyIndex
        self.__providers = LazyIndex()
        self.__tags = LazyIndex()
        self.__builtins = LazyIndex()
        builtins = _get_builtins()
        for k, v in builtins.items():
            self.__builtins.set_key(k, v)

        # self._locals = DefinedBuilders().locals
        # self._builtins = DefinedBuilders().builtins
        self.__configs = {}

    @property
    def providers(self):
        """Index of active Crypto services"""
        return self.__providers.index

    @property
    def tags(self):
        """Index of current tags associated to a Crypto services"""
        return self.__tags.index

    @property
    def _builtins(self):
        """Index of available built-in Crypto providers"""
        return self.__builtins.index

    def get_mode(self, sid):
        """Get Crypto service instance by its identifier"""
        if sid in self.providers:
            return sid
        raise CryptoFactoryError("Unknown or unavailable mode")

    def get_mode_tag(self, sid):
        """Get Crypto service tag by its identifier"""
        return self.__providers.get_arg(sid, 'tag')

    def get_tag_mode(self, tag):
        """Get Crypto service identifier by its tag"""
        return self.__tags.get_arg(tag, 'id')

    def register(self, config=None, sid=None, builder=None, tag=None):
        """
        Register and initialize a Crypto service using its builder class.

        :param dict config:
            Crypto service parameters to initialize it (dict).
            Required keys/values are dependant to arguments needed by
            the Crypto service (ie: key, iv, ...). Can also have ``id``,
            ``builder`` and ``tag`` keys to replace following arguments.

        :param sid:
            Crypto service identifier to register with.
            (Equivalent to ``mode`` argument in client interface)
        :type sid: str or int

        :param builder:
            Crypto service builder as a child class of ``CryptoBuilder``.
            Class name as *str* also supported for built-in providers.

            .. Note::
                If ``builder=None``, a null entry will be created for this
                service identifier. This is the method to use to deregister
                a service.

        :type builder: class or str

        :param str tag:
            Crypto service tag as a string of characters (tag can be used as
            identifier on encrypted data). The tag will be formatted using
            ``normalize_tag`` method (from ``CryptoUtils`` class). "``$``"
            character is reserved as it is used as separator.
            (See :ref:`API <normalize-tag>` for details)

        :return: ``sid`` or ``None``
            Return ``sid`` if builder has been successfully registered and
            initialized as an available service.
            Return ``None`` if builder has not been initialized.

        :raises CryptoFactoryError:
            If the Crypto service is unable to register or initialize, an error
            is raised. Check error message for details.


        """

        # Check config
        if config and isinstance(config, dict):
            if sid is None:
                sid = config.get('sid') or config.get('id')
            builder = builder or config.get('builder')
            tag = tag or config.get('tag')

        if isinstance(sid, (str, int)):

            # Define builder
            if isinstance(builder, str):
                if self._builtins.get(builder):
                    builder = self._builtins[builder]
                else:
                    # builder = globals().get(builder)  # not working
                    raise CryptoFactoryError('Not a built-in Crypto builder')

            if isinstance(builder, type):
                # issubclass not working with external module, need alternate solution <class>.__base__ ?= CryptoBuilder
                # if issubclass(builder, CryptoBuilder):

                # if builder.__base__.__name__ == CryptoBuilder.__name__:
                # New check to support sub-child inheritance (templating an existing Builder)
                # if builder.__weakref__.__objclass__ == CryptoBuilder:
                if CryptoBuilder in builder.__mro__:
                    builder = builder()
            else:
                builder = None

            # Define tag
            tag = CryptoUtils.normalize_tag(tag) if tag else None

            # Check if tag already registered with a service id
            if self.get_tag_mode(tag) is not None:
                if builder:
                    # We are trying to register a service with an existing tag !!!
                    raise CryptoFactoryError('Tag already used by a registered provider')

            # Deregister a service when builder is None
            if not builder:
                # Remove tag entry before service
                registered_tag = self.get_mode_tag(sid)
                self.__tags.del_key(registered_tag)
                # Create a None entry in providers
                self.__providers.set_arg(sid, id=sid, builder=None, tag=None)

            # Register service
            else:
                # Record service in providers index
                self.__providers.set_arg(sid, id=sid, builder=builder, tag=tag)
                # Update tags index if tag
                if tag:
                    self.__tags.set_arg(tag, id=sid)
                # Record config (UNSAFE: Uncomment only for debug.)
                # self.__configs[sid] = config

            # Init service
            if builder and isinstance(config, dict):

                try:
                    builder(**config)
                    return sid
                except:
                    raise CryptoFactoryError('Unable to start provider')

        else:
            raise CryptoFactoryError('Unable to register provider, missing or wrong type argument(s)')

    def get(self, sid):
        """
        Call to a Crypto service instance

        This method is called by abstraction methods from the client interface
        and should not be used directly.

        :param sid:
            Crypto service identifier to call.
            (Equivalent to ``mode`` argument in client interface)
        :type sid: str or int

        :return: **Crypto service builder** class instance

        :raise CryptoFactoryError:
            If the Crypto service is not registered.
        """
        builder = self.__providers.get_arg(sid, 'builder')
        if builder:
            return builder()
        else:
            raise CryptoFactoryError('Service not registered: ', sid)


if __name__ == '__main__':
    None
