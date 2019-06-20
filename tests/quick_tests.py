

import sys, inspect
from pprint import pprint
from crypto_factory import CryptoFactory
from crypto_factory.templates import CryptoBuilder

# Init
cf = CryptoFactory()

# configs
config_Dummy = {
    'id': 0,
    'builder': 'DummyServiceBuilder',
    'label': 'secret',
    'tag': 'DUMMY'
}

config_Fernet = {
    'id' : 'fernet',
    'builder': 'FernetServiceBuilder',
    'tag': 'FERNET_TAG',
    'key': b'ESzO9JifDC8OsBhpPa_h7crdciXyacVF_6J2c8Hsi_0='
}

config_AES1 = {
    'id': 'aes1',
    'builder': 'AESServiceBuilder',
    'tag': 'AES1',
    'key': cf.utils.generate_key(256, urlsafe=False),
    'iv': cf.utils.generate_key(128, urlsafe=False),
    'urlsafe': False,
    'encoding': 'utf-16',
}

config_AES2 = {
    'id': 'aes2',
    'builder': 'AESServiceBuilder',
    'tag': 'AES2',
    'key': cf.utils.generate_key(128, urlsafe=False),
    'urlsafe': False,
    'prefix': 'I_w@$-N0T_Th3r3!',
    'salt_length': 32,
}

config_1 = {
    'id': 'user_1',
    'builder': 'AESServiceBuilder',
    'tag': 'MY_TAG1',
    'key': cf.utils.generate_key(192, urlsafe=False),
    'urlsafe': False,
    'encoding': 'utf-16',
    'prefix': 'User_1-prefix',
    'salt_length': 24
}

# Template a built-in provider
from crypto_factory.providers import AESServiceBuilder


class User1Builder(AESServiceBuilder):
    _defaults = dict(
        prefix='Usernew_1-prefix',
        salt_length=24,
        urlsafe=False,
        encoding='utf-16',
    )


new_config_1 = {
    'id': 'new_1',
    'builder': User1Builder,
    'tag': '',
    'key': config_1['key'],
}

# Register Crypto Service(s)
cf.services.register(config_Dummy)
cf.services.register(config_Fernet)
cf.services.register(config_AES1)
cf.services.register(config_AES2)

cf.services.register(config_1)
# cf.services.register(config_2)
# cf.services.register(config_3)
cf.services.register(new_config_1)


print('\n*** Registered providers (active): ')
pprint(cf.services.providers)

print('\n*** Local providers: ')
test = dict([m for m in inspect.getmembers(sys.modules[__name__], inspect.isclass) if not m[0].startswith('__') and issubclass(m[1], CryptoBuilder)])
pprint(test)

print('\n*** Built-in providers')
pprint(cf.services._builtins)

print('\n** Encrypt/Decrypt tests: ')
num = 10
for mode in cf.services.providers.keys():
    print('> Testing mode: ', str(mode).upper())
    i = 0
    while True:
        print(cf.decrypt(cf.encrypt('My_Secret_' + str(i), mode), mode), end=' | ')
        i += 1
        if i == num:
            print('')
            break

print('\n** Check config/class interop: ')
test1 = cf.encrypt('My_Secret', 'user_1')
test2 = cf.encrypt('My_Secret', 'new_1')
equ1 = False
try:
    equ1 = cf.decrypt(test2, 'user_1') == cf.decrypt(test1, 'new_1')
except:
    pass
print('> Testing user_1 == new_1: ', str(equ1).upper())
print()

if not equ1:
    print('DIFF (<value> : <class>, <config>):')
    for k, v in User1Builder._defaults.items():
        if v != config_1.get(k):
            print('   ', str(k).upper(), ': ', v, ', ', config_1.get(k))

cf.services.register(sid='user_1')