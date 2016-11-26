#!/usr/bin/python

from __future__ import print_function
import argparse
import json
import subprocess

COMMON_ENV = 'common'

actions = [
('commands', 'list the available commands'),
('unpack', 'unpack the dependencies and install them'),
('difference', 'list the packages not installed but mentioned')
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

def commands():
    print('\ncommands available to perform:\n')
    for action, description in actions:
        print(action, '----', description)

def difference(environment):
    with open('package.json') as file:
        package_data = file.read()
        data = json.loads(package_data)
        dependencies = data.get('dependencies')
        if dependencies and dependencies.get(environment):
            common_packages = dependencies.get(COMMON_ENV)
            packages = dependencies.get(environment)
            packages.update(common_packages)
            listed = set([item.lower() for item in packages.keys()]) # listed requirements
            p = subprocess.Popen(['pip', 'freeze'], stdout=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if stdout:
                installed_ = stdout.split('\n')  # installed requirements
                installed = set([item.split('==')[0].lower() for item in installed_])
                differences = listed-installed
                if differences:
                    print('\npackages yet to be installed:\n')
                    for package in differences:
                        print(package)
                    print('\nrun unpack command to install the missed dependencies\n')
                else:
                    print('\nupdate to date. come back later\n')

            else:
                print('pip freeze command failed')

        else:
            print('dependencies not specified')


def unpack(environment):
    with open('package.json') as file:
        package_data = file.read()
        data = json.loads(package_data)
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
            print('dependencies not specified')


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
    else:
        print('\ncommand not found\n')
        commands()
