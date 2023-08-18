"""tests
"""

import argparse
from . import commands


class TestCommandsCrypt:
    """TestCommandsCrypt
    """

    def test_encrypt(self):
        """test_commands
        """
        args = argparse.Namespace(
            command='crypt',
            encrypt=True,
            decrypt=False,
            text='helloworld',
            profile='default',
            file=None,
            aes_key=None,
            aes_iv=None,
            aes_length=None,
            algorithm=None,
        )
        params = commands.crypt.get_crypt_params_from_args(args)
        text = commands.crypt.get_text_from_args(args)

        result = 'AAAAAAAAAAAAAAAAAAAAAJqEKl6oG2eIc/U7wi9I6c0='
        assert result == commands.crypt.encrypt(text, **params)

    def test_decrypt(self):
        """test_commands
        """
        args = argparse.Namespace(
            command='crypt',
            encrypt=False,
            decrypt=True,
            text='AAAAAAAAAAAAAAAAAAAAAJqEKl6oG2eIc/U7wi9I6c0=',
            profile='default',
            file=None,
            aes_key=None,
            aes_iv=None,
            aes_length=None,
            algorithm=None,
        )
        params = commands.crypt.get_crypt_params_from_args(args)
        text = commands.crypt.get_text_from_args(args)

        result = 'helloworld'
        assert result == commands.crypt.decrypt(text, **params)
