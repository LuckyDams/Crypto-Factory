# -*- coding: utf-8 -*-
"""
utilities
---------

This module provides the ``CryptoUtils`` class available within the Crypto-Factory
interface through the ``utils`` property.
"""
import os
import base64
import string
import secrets
import uuid
import logging
from .exceptions import CryptoFactoryError

__all__ = [
    'CryptoUtils',
]

# Create library logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class CryptoUtils:
    valid_tag_chars = "!#(),-.:;<>?@[]_{|}%s%s" % (string.ascii_letters, string.digits)

    @classmethod
    def normalize_tag(cls, tag):
        """
        .. _normalize-tag:

        **Normalize tag** value

        If tag is type *int*, will return its string representation (*str*).

        If tag is type *dict*, will look for 'tag' key value ; then will
        validate string  as *str*.

        If tag is type *str*, will check if its characters are valid then return
        a normalized tag in upper format:

            - Valid characters are ascii letters, digits and punctuation in
              "``!#(),-.:;<>?@[]_{|}``".

            - "`$`" (used as separator), and other characters will be removed.

        :param tag: Value to normalize as 'tag'.
        :type tag: str or int or dict

        :return: **normalized tag** (upper `str`) OR `None`
        """

        if isinstance(tag, int):
            return str(tag)

        if isinstance(tag, dict):
            tag = tag.get('tag', '')

        if isinstance(tag, str):
            tag = ''.join(c for c in tag if c in cls.valid_tag_chars)
            if len(tag):
                return tag.upper()
            else:
                raise CryptoFactoryError('Null or invalid tag')

        else:
            raise CryptoFactoryError('Invalid tag type')

    @classmethod
    def get_tag(cls, value):
        """**Get tag** from string (encrypted data)"""
        value = cls.data_string(value)
        return value[:value.find('$')]

    @classmethod
    def remove_tag(cls, value):
        """**Remove tag** from string (encrypted data)"""
        value = cls.data_string(value)
        pos = value.find('$') + 1
        return value[pos:]

    @classmethod
    def compare_tag(cls, value, tag):
        """**Compare tag**.
        Return `True` if tag in string (encrypted data), else `False`.
        """
        if tag == cls.get_tag(value):
            return True

    @staticmethod
    def generate_key(size=256, urlsafe=True):
        """
        Generate **random keys** (as *bytes*) of 128, 192, 256, or 512 bits size.
        (standard or urlsafe ``base64`` encoded.)
        """
        if size in (128, 192, 256, 512):
            rand = os.urandom(size // 8)
            if urlsafe:
                # either are working :-)
                return base64.urlsafe_b64encode(rand)
                # return ''.join((secrets.token_urlsafe(size // 8), '=')).encode()
            else:
                return base64.b64encode(rand)
        else:
            raise CryptoFactoryError('Invalid key size')

    @staticmethod
    def generate_tag():
        """Generate a **unique tag** (return a standard ``uuid4`` as *str*)"""
        return str(uuid.uuid4())

    @classmethod
    def generate_string(cls, length=8, chars=None, tag=False):
        """
        Generate a **random string** value of 'n' valid characters.

        :param int length:
            Number of characters to return.

        :param str chars:
            Valid characters tu use. If *None*, will use any charaters from
            ascii_letters, digits & punctuation (from ``string`` library).

        :param bool tag:
            If *True*, will use valid characters for tag.
            (take precedence on `chars` argument)

        :return: str
            (None if length is not int)
        """
        if isinstance(length, int):
            valid_chars = "%s%s%s" % (string.ascii_letters, string.digits, string.punctuation)

            if chars and isinstance(chars, str):
                valid_chars = chars

            if tag:
                valid_chars = cls.valid_tag_chars

            return ''.join(secrets.choice(valid_chars) for i in range(length))

    @staticmethod
    def data_string(data, encoding='utf-8', errors='strict'):
        """Convert **data** to `str` using  standard encoding values if data is `bytes`."""
        return data.decode(encoding, errors) if isinstance(data, bytes) else data

    @staticmethod
    def data_bytes(data, encoding='utf-8', errors='strict'):
        """Convert **data** to `bytes` using  standard encoding values if data is `str`."""
        return data.encode(encoding, errors) if isinstance(data, str) else data

    @staticmethod
    def b64encode(s, urlsafe=True):
        if urlsafe:
            return base64.urlsafe_b64encode(s)
        else:
            return base64.b64encode(s)

    @staticmethod
    def b64decode(s, urlsafe=True):
        try:
            if urlsafe:
                return base64.urlsafe_b64decode(s)
            else:
                return base64.b64decode(s)

        except base64.binascii.Error as err:
            logger.exception("b64decode error: {}".format(err))
            raise CryptoFactoryError("Invalid base64-encoded string")
