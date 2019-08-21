# -*- coding: utf-8 -*-
"""
providers
---------

This module contains **built-in Crypto builders** and associated services.
"""

# TODO: Implement new built-in providers: full AES, PBKDF2, MultiFernet, ...


__all__ = [
    'DummyServiceBuilder',
    'FernetServiceBuilder',
    'AESServiceBuilder',
]


import base64
# import inspect
import string
from secrets import token_bytes, choice

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .templates import CryptoService, CryptoBuilder
from .utils import CryptoUtils
from .exceptions import CryptoFactoryError


class DummyService(CryptoService):
    """Dummy Service"""

    def __init__(self, cipher):
        super().__init__(cipher)
        self.label = '[' + cipher + ']'

    def encrypt(self, raw):
        raw = CryptoUtils.data_string(raw)

        if isinstance(raw, str) and len(raw) > 0:
            enc = ''.join((self.label, raw))
            return enc

    def decrypt(self, enc):
        enc = CryptoUtils.data_string(enc)

        if isinstance(enc, str):

            if len(enc) == 0:
                raise ValueError("Empty input string")

            try:
                out = enc.split(self.label, 1)[1]
                return out

            except IndexError:
                raise ValueError("Invalid key or string")


class DummyServiceBuilder(CryptoBuilder):
    """
    Builder for ``DummyService``:
        For illustration purpose only (do NOT use it in production !!!)

    specifications:
        - Surround data with ``label``
    """
    service = DummyService

    @staticmethod
    def initialize(label='UNSAFE_Dummy'):
        if label:
            return label.lower()


class FernetService(CryptoService):
    """Fernet Service"""

    def encrypt(self, raw):
        raw = CryptoUtils.data_bytes(raw)

        if isinstance(raw, bytes) and len(raw) > 0:
            enc = self.cipher.encrypt(raw)
            return enc.decode('utf-8')

    def decrypt(self, enc):
        enc = CryptoUtils.data_bytes(enc)

        if len(enc) == 0:
            raise ValueError("Empty input string")

        try:
            out = self.cipher.decrypt(enc)
            return out.decode('utf-8')

        except InvalidToken:
            raise ValueError("Invalid key or string")


class FernetServiceBuilder(CryptoBuilder):
    """
    Builder for ``FernetService``:
        Fernet implementation (secured)

    specifications:
        - AES / CBC mode / PKCS7 padding
        - HMAC authentication with SHA256
        - 256 bits ``key`` (used for AES & HMAC)
        - random 128-bit IV
        - urlsafe Base64 encoding
        - string to bytes conversion in UTF-8

    (https://cryptography.io/en/latest/fernet/)
    """
    service = FernetService

    @staticmethod
    def initialize(key=None):
        if key:
            try:
                cipher = Fernet(key)
                return cipher

            except (base64.binascii.Error, ValueError) as err:
                raise ValueError("Invalid key: {}".format(err))


class AESService(CryptoService):
    """AESService"""

    def __init__(self, kwargs):
        self.key = kwargs.get('key')
        self.iv = kwargs.get('iv')
        self.prefix = kwargs.get('prefix')
        self.salt = kwargs.get('salt')
        self.urlsafe = kwargs.get('urlsafe')
        self.encoding = kwargs.get('encoding')

    def encrypt(self, data):
        prefix = self.prefix
        # salt = ''.join(choice(string.printable) for i in range(self.salt))
        salt = CryptoUtils.generate_string(self.salt, chars=string.printable)
        data = ''.join((prefix, salt, data))

        data = CryptoUtils.data_bytes(data, self.encoding)

        if len(data) > 0:
            iv = self.iv or token_bytes(16)
            f = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            encryptor = f.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data)
            padded_data += padder.finalize()
            ct = encryptor.update(padded_data) + encryptor.finalize()
            if self.iv:
                data = ct
            else:
                data = iv + ct
            enc = CryptoUtils.b64encode(data, self.urlsafe)
            return enc

    def decrypt(self, enc):
        pos = len(self.prefix) + self.salt

        if len(enc) > pos + 16:
            try:
                enc = CryptoUtils.b64decode(enc, self.urlsafe)
                if self.iv:
                    iv = self.iv
                else:
                    iv = enc[:16]
                    enc = enc[16:]
                f = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
                decryptor = f.decryptor()
                unpadder = padding.PKCS7(128).unpadder()
                ct = decryptor.update(enc) + decryptor.finalize()
                unpadded_data = unpadder.update(ct)
                unpadded_data += unpadder.finalize()
                data = unpadded_data.decode(self.encoding, 'ignore')

                if data.startswith(self.prefix):
                    return data[pos:]

            except ValueError:
                pass

        raise CryptoFactoryError("Invalid key or string")


class AESServiceBuilder(CryptoBuilder):
    """
    Builder for ``AESService``:
        AES-CBC-PKCS7 implementation

    specifications:
        - AES / CBC mode / PKCS7 padding
        - key of different sizes (128, 192 or 256 bits)
        - random of fixed IV (16 bytes) support
        - optional prefix (fixed string)
        - optional random salt addition (``salt_length`` in bytes)
        - standard or urlsafe base64 encoding
        - standard string encodings support

    string format:
        ``<random_IV: 16><prefix><salt><data>``
    """
    service = AESService
    # _defaults = {}
    _defaults = dict(
        iv=None,
        prefix=None,
        salt_length=None,
        urlsafe=None,
        encoding=None)

    @classmethod
    def _get_defaults(cls, value):
        return cls._defaults.get(value)

    def initialize(self, key, iv=None, prefix=None, salt_length=None, urlsafe=None, encoding=None):
        """
        AESServiceBuilder initialisation

        :param bytes key:
            key of 16, 24 or 32 bytes

        :param bytes iv:
            fixed IV of 16 bytes
            If None, a random IV will be generated on each call and added to
            encrypted data.

        :param str prefix:
            Optional string of data added to encrypted data.

        :param int salt_length:
            Optional random value of 'salt_length' bytes added to encrypted data.

        :param bool urlsafe:
            If True, use 'urlsafe' Base64 encoding. Else, use standard Base64.
            This apply to both key and iv values. Ensure same Base64 method has
            been used to generate them.

        :param str encoding:
            Any supported Python encoding to use for Str / Bytes conversion.
            (See `codecs <https://docs.python.org/3/library/codecs.html#
            standard-encodings>`_ for details)

        :return: dict of parameters for ``AESService``

        .. _provider-subclassing:
        .. Note::
            This provider can be sub-classed in order to define parameters
            default values. This would allow to design a specific AES
            implementation without the need to provide all parameters on each
            initialisation.

            These parameters can bet set in the ``_defaults`` class attribute
            (dict). ``key`` parameter cannot be defined as defaults as it should
            always be provided from client.

            example::

                class MyAESBuilder(AESServiceBuilder):
                    _defaults = dict(
                        iv= None,
                        prefix='MyAES-prefix',
                        salt_length=24,
                        urlsafe=False,
                        encoding='utf-16',
                    )

        """
        # get args or defaults (helper for subclassing)
        iv = iv or self._get_defaults('iv')
        prefix = prefix or self._get_defaults('prefix')
        salt_length = salt_length or self._get_defaults('salt_length')
        urlsafe = urlsafe if isinstance(urlsafe, bool) else self._get_defaults('urlsafe')
        encoding = encoding or self._get_defaults('encoding')

        # validate values
        if not isinstance(prefix, str):
            prefix = ''

        if not isinstance(salt_length, int):
            salt_length = 0

        if not isinstance(urlsafe, bool):
            urlsafe = True

        if not encoding:
            encoding = 'utf-8'

        if iv:
            iv = CryptoUtils.b64decode(iv, urlsafe)
            if len(iv) != 16:
                raise CryptoFactoryError('Invalid IV length (not 16 bytes)')

        # Init cipher if key is valid
        key = CryptoUtils.b64decode(key, urlsafe)
        if len(key) in (16, 24, 32):
            cipher = dict(key=key, iv=iv, prefix=prefix, salt=salt_length, urlsafe=urlsafe, encoding=encoding)
            return cipher
        else:
            raise CryptoFactoryError('Invalid key length')


if __name__ == '__main__':
    None
