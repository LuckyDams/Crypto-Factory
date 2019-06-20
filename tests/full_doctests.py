# -*- coding: utf-8 -*-

"""
Crypto Factory full example:
(Can also be used as doctest)

# Import library
>>> from crypto_factory import *

# Initialise an instance
>>> cf = CryptoFactory()

# Define your Crypto providers configuration
>>> conf_Dummy = {'id': 'dummy',
...               'builder': 'DummyServiceBuilder',
...               'label': "secret",
...               'tag': 'DUMMY'
...               }
>>> conf_AES = {'id'      : 'weak',
...             'builder': 'AESServiceBuilder',
...             'tag'     : 'WEAK_TAG',
...             'key'     : b'WkqHg8m9RwmE1iPQJAbuJRKmh72vLvUNFepIWrOldKg=',
...             'iv'      : b'vdU1T6NvAZJIlnznSe8gbQ==',
...             }
>>> conf_Fernet = {'id'      : 'good',
...                'builder': 'FernetServiceBuilder',
...                'tag'     : 'FERNET_TAG',
...                'key'     : b'ESzO9JifDC8OsBhpPa_h7crdciXyacVF_6J2c8Hsi_0=',
...                }

# Helper to generate keys
>>> cf.utils.generate_key(256)                                       # doctest: +ELLIPSIS
b'...='

# Helpers for built-in providers
>>> cf.services._builtins                                            # doctest: +ELLIPSIS
{'AESServiceBuilder': <class 'crypto_factory.providers.AESServiceBuilder'>,\
 'DummyServiceBuilder': <class 'crypto_factory.providers.DummyServiceBuilder'>,\
 'FernetServiceBuilder': <class 'crypto_factory.providers.FernetServiceBuilder'>}


# # Details on associated service                                 # removed from impl.
# >>> cf.services._builtins['AES1ServiceBuilder'].args_in_fct
# ['key', 'iv']
>>> cf.services._builtins['AESServiceBuilder'].service
<class 'crypto_factory.providers.AESService'>
>>> print(cf.services._builtins['AESServiceBuilder'].__doc__)        # doctest: +ELLIPSIS
<BLANKLINE>
    Builder for ``AESService``:
        AES-CBC-PKCS7 implementation
<BLANKLINE>
    specifications:
        - AES / CBC mode / PKCS7 padding
        - key of different sizes (128, 192 or 256 bits)
        - random of fixed IV (16 bytes) support
        - optional prefix (fixed string)
        - optional random salt addition (``salt_length`` in bytes)
        - standard or urlsafe base64 encoding
        - standard string encodings support
<BLANKLINE>
    string format:
        ``<random_IV: 16><prefix><salt><data>``
<BLANKLINE>
>>> help(providers.FernetServiceBuilder)                            # doctest: +ELLIPSIS
Help on class FernetServiceBuilder in module crypto_factory.providers...

# Register providers
>>> cf.services.register(conf_Dummy, 0)
0
>>> cf.services.register(conf_AES, sid=1, tag="AES_TAG")
1
>>> cf.services.register(conf_Fernet, 2)
2

>>> cf.services.providers                   # doctest: +ELLIPSIS
{0: {'id': 0, 'builder': <crypto_factory.providers.DummyServiceBuilder ...}}

# Helpers on providers (registered services)
>>> cf.services.providers[1].builder.service
<class 'crypto_factory.providers.AESService'>

>>> cf.services.providers[1].builder.args_in_fct
['key', 'iv', 'prefix', 'salt_length', 'urlsafe', 'encoding']

>>> cf.services.providers[1].builder.features
['decrypt', 'encrypt']

>>> cf.services.providers[1].builder.args_present
['id', 'builder', 'tag', 'key', 'iv']


# Encrypt data
>>> test0 = cf.encrypt('My_Secret', mode=0)

>>> test0
'DUMMY$<secret>My_Secret</secret>'
>>> test1 = cf.encrypt('My_Secret', mode=1)

>>> test1                                                           # doctest: +ELLIPSIS
'AES_TAG$...='
>>> test2 = cf.encrypt('My_Secret', mode=2)

>>> test2                                                           # doctest: +ELLIPSIS
'FERNET_TAG$g...=='

# Decrypt data
>>> cf.decrypt(test0, mode=0)
'My_Secret'
>>> cf.decrypt(test1, mode=1)
'My_Secret'
>>> cf.decrypt(test2, mode=2)
'My_Secret'

# Decrypt wrong hash
>>> cf.decrypt(test2, mode=1)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Unable to decrypt with Crypto service: 1

# Display registered TAGs
>>> cf.services.tags
{'DUMMY': {'id': 0}, 'AES_TAG': {'id': 1}, 'FERNET_TAG': {'id': 2}}

# Enforced Tag validation
>>> test1_bad = test1.replace('AES_TAG', 'BAD_TAG')
>>> cf.decrypt(test1_bad, mode=1, tag_strict=True)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Tag mismatch found (tag_strict enable)

# No Tag test
>>> test1_notag = cf.encrypt('My_Secret', mode=1, tag=False)
>>> test1_notag.find('$')
-1
>>> cf.decrypt(test1_notag, mode=1)
'My_Secret'
>>> cf.decrypt(test1_notag, mode=1, tag_strict=True)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Tag mismatch found (tag_strict enable)

# Decrypt based on tag
# Since data have been tagged, we can decrypt without providing a service
>>> cf.decrypt(test0)
'My_Secret'
>>> cf.decrypt(test1)
'My_Secret'
>>> cf.decrypt(test2)
'My_Secret'

# However for enforced tag validation, a service must be provided
>>> cf.decrypt(test1, tag_strict=True)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Crypto service mode required (tag_strict enabled)

# Obviously, it is not possible to decrypt untagged data without a service
>>> cf.decrypt(test1_notag)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Unknown or unavailable mode


# Rotate cipher from modes as list:
>>> test1_new = cf.rotate(test1, from_modes=[1, 2], to_mode=2)
>>> test1_new                                                       # doctest: +ELLIPSIS
'FERNET_TAG$...=='

# Rotate cipher from single mode as str
>>> test1_new = cf.rotate(test1, from_modes=1, to_mode=2, tag_strict=True)
>>> test1_new                                                       # doctest: +ELLIPSIS
'FERNET_TAG$...=='

# Rotate error if no provider are able to decrypt (from_modes):
>>> test1_new = cf.rotate(test1, from_modes=[2], to_mode=2)
Traceback (most recent call last):
  ...
crypto_factory.exceptions.CryptoFactoryError: Unable to rotate data with provided list of Crypto services


# Rotate all keys to a new provider (HOWTO)
>>> cf.services.register( config = {'key': cf.utils.generate_key(256),
... 'builder': 'FernetServiceBuilder'} , sid=3, tag='TARGET')
3
>>> ciphers = [test0, test1, test2]
>>> new_ciphers = []
>>> for cipher in ciphers:
...    new = cf.rotate(cipher, from_modes=[0, 1, 2], to_mode=3, tag=True)
...    new_ciphers.append(new)
...
>>> new_ciphers                                                     # doctest: +ELLIPSIS
['TARGET$g...==', 'TARGET$g...==', 'TARGET$g...==']

# Deregister old providers
>>> cf.services.register(sid=0)
>>> cf.services.register(sid=1)
>>> cf.services.register(sid=2)
>>> cf.services.providers                                           # doctest: +ELLIPSIS
{0: {'id': 0, 'builder': None, 'tag': None},\
 1: {'id': 1, 'builder': None, 'tag': None},\
 2: {'id': 2, 'builder': None, 'tag': None},\
 3: {'id': 3, 'builder': <...FernetServiceBuilder object at 0x...>, 'tag': 'TARGET'}}
>>> cf.services.tags
{'TARGET': {'id': 3}}

# TEST exception on register
>>> cf.services.register({'key': b'BAD_KEY'}, sid='test',
... builder='FernetServiceBuilder', tag='TAG')
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Unable to start provider

# Implementing exception
>>> from crypto_factory.exceptions import CryptoFactoryError
>>> try:
...     cf.decrypt('BAD_DATA', mode=3)
... except CryptoFactoryError as err:
...     print("CryptoFactory error: {0}".format(err))
...
CryptoFactory error: Unable to decrypt with Crypto service: 3

# TEST new AES provider params
>>> config_1 = {
...     'id': 'user_1',
...     'builder': 'AESServiceBuilder',
...     'tag': 'MY_TAG1',
...     'key': cf.utils.generate_key(192, urlsafe=False),
...     'urlsafe': False,
...     'encoding': 'utf-16',
...     'prefix': 'User_1-prefix',
...     'salt_length': 24
... }
>>> mode = cf.services.register(config_1)
>>> cf.decrypt(cf.encrypt('My_Secret', mode))
'My_Secret'

# TEST templating built-in AES provider
>>> from crypto_factory.providers import AESServiceBuilder
>>> class User1Builder(AESServiceBuilder):
...     _defaults = dict(
...         prefix='User_1-prefix',
...         salt_length=24,
...         urlsafe=False,
...         encoding='utf-16',
...     )
...
>>> new_config_1 = {
...     'id': 'new_1',
...     'builder': User1Builder,
...     'tag': 'MY_NEW1',
...     'key': config_1['key'],
... }
>>> mode = cf.services.register(new_config_1)
>>> cf.decrypt(cf.encrypt('My_Secret', mode))
'My_Secret'

# Ensure both are equivalent
>>> cf.decrypt(cf.encrypt('My_Secret', 'user_1'), 'new_1')
'My_Secret'
>>> cf.decrypt(cf.encrypt('My_Secret', 'new_1'), 'user_1')
'My_Secret'

# However tag_strict detect wrong tag
>>> cf.decrypt(cf.encrypt('My_Secret', 'new_1'), 'user_1', tag_strict=True)
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Tag mismatch found (tag_strict enable)

# TEST disable tagging at provider level
>>> cf.services.register(dict(key=cf.utils.generate_key()), sid='notag', builder='FernetServiceBuilder')
'notag'
>>> cf.encrypt('MySecret', mode='notag')                    # doctest: +ELLIPSIS
'gAAAAAB...=='

# Even with tag=True, tagging is disabled
>>> cf.encrypt('MySecret', mode='notag', tag=True)          # doctest: +ELLIPSIS
'gAAAAAB...=='

# Detecting mode from tag on decrypt is not working
>>> cf.decrypt(cf.encrypt('MySecret', 'notag'))
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Unknown or unavailable mode

# Need to provide mode on decrypt
>>> cf.decrypt(cf.encrypt('MySecret', 'notag'), 'notag')
'MySecret'

# Enabling strict_tag is also not working with tag disabled at provider level
>>> cf.decrypt(cf.encrypt('MySecret', 'notag'), 'notag', tag_strict=True)
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: No tag defined for this Crypto service (tag_strict enabled)

# TEST Tag validation (utils.normalize_tag)
>>> cf.utils.normalize_tag('tag')
'TAG'
>>> cf.utils.normalize_tag('123')
'123'
>>> cf.utils.normalize_tag({'tag': 'TAG'})
'TAG'
>>> cf.utils.normalize_tag('')
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Null or invalid tag
>>> cf.utils.normalize_tag({})
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Null or invalid tag
>>> cf.utils.normalize_tag(None)
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Invalid tag type
>>> cf.utils.normalize_tag([])
Traceback (most recent call last):
...
crypto_factory.exceptions.CryptoFactoryError: Invalid tag type

# TEST random string (utils.generate_string)
>>> cf.utils.generate_string()                              # doctest: +ELLIPSIS
'...'

# string of 3 chars
>>> cf.utils.generate_string(3)                             # doctest: +ELLIPSIS
'...'

# valid string for tag
>>> cf.utils.generate_string(tag=True)                      # doctest: +ELLIPSIS
'...'

# string from chars
>>> cf.utils.generate_string(chars='123456ABCD')            # doctest: +ELLIPSIS
'...'

>>> cf.utils.generate_string(chars='1')
'11111111'
>>> import string
>>> cf.utils.generate_string(chars=string.ascii_letters)    # doctest: +ELLIPSIS
'...'

"""

if __name__ == '__main__':
    import doctest
    # doctest.testmod()
    doctest.testmod(verbose=True)
