# -*- coding: utf-8 -*-
"""
interface
---------

This module owns the client interface within the main class ``CryptoFactory``.
"""

# TODO: Check Crypto service 'features' to ensure method is implemented

import logging
from .factory import CryptoServicesManager
from .utils import CryptoUtils
from .exceptions import CryptoFactoryError
from .templates import CryptoBuilder, CryptoService

__all__ = [
    'CryptoFactory',
]

# Create library logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CryptoFactory:
    """
    Client **interface** for Crypto-Factory.

    It provides following features access:

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
    """
    def __init__(self):
        self.__services = CryptoServicesManager()
        self.__utils = CryptoUtils
        self.CryptoBuilder = CryptoBuilder
        self.CryptoService = CryptoService
        # self._caller = _get_caller()

    @property
    def services(self):
        """entry-point to **Crypto services manager**
        (See ``CryptoServicesManager`` class for details.)
        """
        return self.__services

    @property
    def utils(self):
        """entry-point to **Crypto utilities**
        (See ``CryptoUtils`` class for details.)
        """
        return self.__utils

    def __add_tag(self, value, mode):
        """Add tag to string"""
        tag = self.__services.get_mode_tag(mode)
        if tag:
            return '$'.join((tag, value))

    def __compare_tag(self, value, mode):
        """Compare tag from string to defined Crypto service tag"""
        tag = self.__services.get_mode_tag(mode)
        return self.__utils.compare_tag(value, tag)

    def __del_tag(self, value):
        """Remove tag from string"""
        return self.__utils.remove_tag(value)

    def encrypt(self, data, mode, tag=True):
        """
        Abstraction method for **symmetric encryption**.

        Call ``encrypt`` method of selected Crypto service.
        Will add a 'tag' to encrypted 'data' before returning result if ``tag=True``.

        :param data:
            Plain data (to encrypt).
        :type data: str or bytes

        :param mode:
            Crypto service identifier ('sid' in ``factory``).
        :type mode: str or int

        :param bool tag:
            Add the Crypto service tag to 'data' if *True* (default).
            If Crypto service has tagging disabled (no 'tag' on ``register``),
            this parameter will be skipped (set to *False*).

        :return: **encrypted data** as *str*

        :raises CryptoFactoryError:
            An exception is raised if an error occurs. Check error message for details.
        """
        # Check args
        if not isinstance(data, (str, bytes)):
            raise CryptoFactoryError('Supported data format is string or bytes')
        # if tag and not self.__services.get_mode_tag(mode):
        #     raise CryptoFactoryError('No defined tag for this Crypto service (tag=True)')

        # Disable tag if not defined in provider
        if not self.__services.get_mode_tag(mode):
            tag = False

        # data as str
        data = self.__utils.data_string(data)

        mode = self.__services.get_mode(mode)

        if data:
            try:
                enc_data = self.__services.get(mode).encrypt(data)
                enc_data = self.__utils.data_string(enc_data)
            except Exception as err:
                logger.exception("Unable to encrypt with Crypto service '{}': {}".format(mode, err))
                raise CryptoFactoryError("Unable to encrypt: {}".format(err))

            if tag:
                enc_data = self.__add_tag(enc_data, mode)

            return enc_data

    def decrypt(self, data, mode=None, tag_strict=False):
        """
        Abstraction method for **symmetric decryption**.

        Check if tag is matching selected Crypto service 'mode' (if 'tag_strict' enabled).
        Remove tag before calling  ``decrypt`` method of selected Crypto service.

        :param data:
            Encrypted data (to decrypt).
        :type data: str or bytes

        :param mode:
            Crypto service identifier ('sid' in ``factory``).
        :type mode: str or int

        :param bool tag_strict:
            Enforce tag validation (*False* by default).
            If *True*, compare data tag with Crypto service tag.

        :return: **decrypted data** as *str*

        :raises CryptoFactoryError:
            An exception is raised if an error occurs. Check error message for details.
        """
        # Check args
        if not isinstance(data, (str, bytes)):
            raise CryptoFactoryError('Supported data format is string or bytes')
        if tag_strict:
            if mode is None:
                raise CryptoFactoryError('Crypto service mode required (tag_strict enabled)')
            elif not self.__services.get_mode_tag(mode):
                raise CryptoFactoryError('No tag defined for this Crypto service (tag_strict enabled)')
        # data as str
        data = self.__utils.data_string(data)

        # Define mode
        if mode is None:
            # retrieve from tag if not provided
            tag = self.__utils.get_tag(data)
            mode = self.__services.get_tag_mode(tag)
        mode = self.__services.get_mode(mode)

        # Check matching tag in data
        if tag_strict:
            if not self.__compare_tag(data, mode):
                raise CryptoFactoryError('Tag mismatch found (tag_strict enable)')

        # Remove tag (if any)
        data = self.__del_tag(data)

        if data:
            try:
                plain_data = self.__services.get(mode).decrypt(data)
            except Exception as err:
                logger.exception("Unable to decrypt with Crypto service '{}': {}".format(mode, err))
                raise CryptoFactoryError("Unable to decrypt: {}".format(err))

            return self.__utils.data_string(plain_data)

    def rotate(self, data=None, from_modes=None, to_mode=None, tag_strict=False, tag=True):
        """
        Advanced method to **'rotate' encrypted data** from one or more Crypto
        services to a target one. It can be used for keys rotation, migration of
        existing data to a new Crypto service, ...

        Based on decrypt and encrypt methods, will provide same tag options.

        :param data:
            Encrypted data (to rotate).
        :type data: str or bytes

        :param from_modes:
            Source Crypto service identifier(s).
        :type from_modes: str or list

        :param to_mode:
            Target Crypto service identifier.
        :type to_mode: str or int

        :param bool tag_strict:
            Enforce tag validation (see ``decrypt`` method).

        :param bool tag:
            Add the Crypto service tag (see ``encrypt`` method).

        :return: **encrypted data** as *str* (to target Crypto service format)

        :raises CryptoFactoryError:
            An exception is raised if an error occurs. In particular when
            no 'from_modes' methods are able to decrypt data.
            Check error message for details.
        """
        if data:
            modes_list = []
            if isinstance(from_modes, (str, int)):
                modes_list.append(from_modes)
            elif isinstance(from_modes, (list, tuple)):
                modes_list = from_modes

            for mode in modes_list:
                try:
                    tmp_data = self.decrypt(data, mode, tag_strict)
                    break
                except CryptoFactoryError:
                    pass
            else:
                raise CryptoFactoryError("Unable to rotate data with provided list of Crypto services")

            enc_data = self.encrypt(tmp_data, to_mode, tag)
            return enc_data


if __name__ == '__main__':
    None
