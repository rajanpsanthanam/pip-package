#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import subprocess
import urllib.request

COMMON_ENV = 'common'
PIP_FREEZE_FAILURE = 'pip freeze command failed'
DEPENDENCIES_NOT_SPECIFIED = 'dependencies not specified'

actions = [
('commands', 'list the available commands'),
('unpack', 'unpack the dependencies and install them'),
('difference', 'list the packages not installed but mentioned'),
('check', 'check for the latest version availability of installed packages')
]

parser = argparse.ArgumentParser()
parser.add_argument(
    'action',
    help='action to perform.\n try "commands" action to know the list of commands available'
)
parser.add_argument(
    "-e",
    "--environment",
    default='development',
    dest='environment',
    help='environment in which to perform the action'
)

def read_config():
    fh = open('package.json')
    package_data = fh.read()
    data = json.loads(package_data)
    return data

def _get_pip_freeze():
    p = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE, universal_newlines=True)
    stdout, stderr = p.communicate()
    if stdout:
        installed = stdout.split('\n')  # installed requirements
        return filter(None, installed)
    return None

def check():
    installed_packages = _get_pip_freeze()
    if installed_packages:
        for item in installed_packages:
            package, version = item.split('==')
            url = 'https://pypi.python.org/pypi/{0}/json'.format(package)
            r = urllib.request.urlopen(url)
            data = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            latest_version = data.get('info').get('version')
            if version != latest_version:
                print('{0} {1} --> {2}'.format(package, version, latest_version))
    else:
        print(PIP_FREEZE_FAILURE)

def commands():
    print('\ncommands available to perform:\n')
    for action, description in actions:
        print(action, '----', description)

def difference(environment):
    data = read_config()
    dependencies = data.get('dependencies')
    if dependencies and dependencies.get(environment):
        common_packages = dependencies.get(COMMON_ENV)
        packages = dependencies.get(environment)
        packages.update(common_packages)
        listed = set([item.lower() for item in packages.keys()]) # listed requirements
        installed_packages = _get_pip_freeze()
        if installed_packages:
            installed = set([item.split('==')[0].lower() for item in installed_packages])
            differences = listed-installed
            if differences:
                print('\npackages yet to be installed:\n')
                for package in differences:
                    print(package)
                print('\nrun unpack command to install the missed dependencies\n')
            else:
                print('\nupdate to date. come back later\n')

        else:
            print(PIP_FREEZE_FAILURE)

    else:
        print(DEPENDENCIES_NOT_SPECIFIED)


def unpack(environment):
    data = read_config()
    dependencies = data.get('dependencies')
    if dependencies and dependencies.get(environment):
        common_packages = dependencies.get(COMMON_ENV)
        packages = dependencies.get(environment)
        packages.update(common_packages)
        for key, value in packages.items():
            if not value == '*':
                subprocess.call(["pip", "install", '{0}=={1}'.format(key, value)])
            else:
                subprocess.call(["pip", "install", key])
    else:
        print(DEPENDENCIES_NOT_SPECIFIED)


if __name__ == '__main__':
    args = parser.parse_args()
    action = args.action
    environment = args.environment
    if action == 'commands':
        commands()
    elif action == 'unpack':
        unpack(environment)
    elif action == 'difference':
        difference(environment)
    elif action == 'check':
        check()
    else:
        print('\ncommand not found\n')
        commands()
