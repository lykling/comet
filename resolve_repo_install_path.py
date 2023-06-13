#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""resolve git repo path
"""
import sys
import re
import urllib.parse
import validators


def resolve_install_path(uri: str):
    """resolve github repo install path
    """
    scheme_prefix = re.compile(r'[a-z]+://')
    login_prefix = re.compile(r'[a-z]+@')
    full_uri = uri
    if not scheme_prefix.search(uri):
        if ':' in uri:
            # scp like syntax
            service = uri.split(':')[0]
            path = uri.split(':')[1]
            install_service = login_prefix.sub('', service)
            install_path = path.replace('.git', '')
            return (f'{service}:{path}',
                    f'{install_service}/{install_path}')

        if not validators.domain(uri.split('/')[0]):
            # not service found, use github as default
            service = 'github.com'
            path = uri.replace('.git', '')
            return (f'git@{service}:{path}.git',
                    f'{service}/{path}')

        # no scheme, use ssh as default
        full_uri = f'ssh://{uri}'

    parse_result = urllib.parse.urlparse(full_uri)

    # trim login info
    service = login_prefix.sub('', parse_result.netloc)
    # trim service port
    service = service.split(':')[0]
    path = parse_result.path.replace('.git', '')
    return (full_uri, f'{service}{path}')


def main():
    """main entry
    """
    install_path = resolve_install_path(sys.argv[1].strip('"\''))
    print(' '.join(install_path))
    # sys.stderr.write('argv:\n')
    # sys.stderr.write('\n'.join(sys.argv))
    # sys.stderr.write('\n')


if __name__ == '__main__':
    main()
