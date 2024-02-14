from subprocess import Popen, PIPE, STDOUT
from colorama import init as colorama_init
from colorama import Style, Fore
from pygit2 import Repository
import configparser
import pandas as pd
import threading
import hashlib
import signal
import sys
import os
import re

colorama_init()

import locale

locale.setlocale(locale.LC_ALL, '')

db_name = os.environ.get('DBNAME')
proj_name = os.environ.get('PROJECT_NAME')
config = os.environ.get('CONFIG_FILE') or os.environ.get('CONFIG_PATH')
module = os.environ.get('MODULE')
install = os.environ.get('INSTALL')
enterprise = os.environ.get('ENTERPRISE_PATH')
dev = os.environ.get('DEV')
is_shell = os.environ.get('SHELL')
warning = os.environ.get('WARNING')
odoo_path = os.environ.get('ODOO_PATH')
version = os.environ.get('VERSION')
envs = os.environ.get('ENVS')
github_path = os.environ.get('GITHUB') or os.environ.get('GITHUB_PATH') or ''
additional_args = os.environ.get('ARGS', '')
test_db = os.environ.get('DEMO')
demo = os.environ.get('TEST')
idk = os.environ.get('IDK')

CWD = os.path.dirname(os.path.realpath(__file__))
mods = pd.read_csv(CWD + '/modules.csv')

# tmp_cfg = CWD + '/odoo-conf.cfg'
tmp_cfg = os.path.expanduser('~/.odoorc')
if demo and demo == 'True':
    tmp_cfg = CWD + '/odoo-demo-conf.cfg'

config_parser = configparser.ConfigParser()
config_parser.read(config)

if not version and (not test_db or test_db == 'False'):
    try:
        version = list(mods[mods['DBNAME'] == proj_name]['VERSION'])[0]
    except:
        version = str(Repository(odoo_path).head.shorthand)

ADDON_VARS = {
    '${GITHUB}': github_path,
    '${VERSION}': str(version) if idk != 'True' else 'src',
    '${ODOO}': odoo_path,
    '${ENTERPRISE}': enterprise,
    '${PROJECT_NAME}': proj_name,
}

ADDON_VARS = dict((re.escape(k), v) for k, v in ADDON_VARS.items())
pattern = re.compile("|".join(ADDON_VARS.keys()))

if proj_name:
    proj_name = pattern.sub(
        lambda m: ADDON_VARS[re.escape(m.group(0))], proj_name)
    config_parser.set('options', 'proj_name', proj_name)

if idk and idk == 'True':
    config_parser.set('options', 'VERSION', 'src')
elif version:
    version = pattern.sub(
        lambda m: ADDON_VARS[re.escape(m.group(0))], str(version))
    config_parser.set('options', 'VERSION', str(version))

if test_db == 'True':
    db_name = f'psae-demo-{version}'
elif not db_name:
    db_name = proj_name

if db_name:
    db_name = pattern.sub(lambda m: ADDON_VARS[re.escape(m.group(0))], db_name)
    config_parser.set('options', 'db_name', db_name)

addons_paths = config_parser['options']['addons_path']
if addons_paths:
    addons_paths = pattern.sub(
        lambda m: ADDON_VARS[re.escape(m.group(0))], addons_paths)
    config_parser.set('options', 'addons_path', addons_paths)

with open(tmp_cfg, 'w+') as tmp:
    config_parser.write(tmp)

mods = pd.read_csv(CWD + '/modules.csv')
proj_path = '/home/abwa/ODOO/src/odoo-psae/' + db_name + '/'
modules = module
if not module or module == 'False' or module != 'NONE':
    try:
        modules = ','.join([name for name in os.listdir(proj_path) if os.path.isdir(
            os.path.join(proj_path, name)) and 'git' not in name])
    except:
        pass

db_post_fix = int(hashlib.sha256(
    modules.encode('utf-8')).hexdigest(), 16) % 10**8

warned = False

command = [sys.executable]

odoo_path = odoo_path or f'/home/abwa/ODOO/{str(version) if idk != "True" else "src"}/odoo'

command.append(odoo_path + '/odoo-bin')

if config:
    command += ['-c', tmp_cfg]
if db_name:
    command += ['-d', db_name]

arg = '-u'
if install and install == 'True':
    arg = '-i'

if module and module != 'False':
    command += [arg, module]
elif not module or module != 'NONE':
    command += [arg, modules]

if dev:
    command += ['--dev=%s' % dev]

if additional_args:
    command += additional_args.split(' ')

def colored(text, color, attrs=None):
    color = getattr(Fore, color.upper())
    final = color or ''
    if attrs:
        if 'bold' in attrs:
            final += Style.BRIGHT
        if 'concealed' in attrs:
            final += Style.DIM
    final += text + Style.RESET_ALL
    return final

print('\r\n')
buffer_line = ''.join(
    ['#' for c in '#### RUNNING COMMAND:     ' + ' '.join(command)])
text1 = colored(buffer_line, 'yellow')
print(text1)
text2 = colored('#### RUNNING COMMAND:     ', 'yellow') + colored(''.join(p + ' ' for p in command), 'green',
                                                                  attrs=['bold'])
print(text2)
text3 = colored(buffer_line, 'yellow')
print(text3)

text = colored('#### CONFIG   : ', 'yellow') + colored(config, 'green', attrs=['bold']) + colored(
    '   -----  USING BUFFER:  ' + tmp_cfg, 'white', attrs=['concealed', 'dark'])
print(text)
if db_name:
    text = colored('#### DATABASE : ', 'yellow') + \
        colored(db_name, 'green', attrs=['bold'])
    print(text)
if module:
    text = colored('#### MODULE   : ', 'yellow') + \
        colored(module, 'green', attrs=['bold'])
    print(text)
if install and install == 'True':
    text = colored('#### INSTALL  : ', 'yellow') + \
        colored("YES", 'green', attrs=['bold'])
    print(text)
if dev:
    text = colored('#### DEV      : ', 'yellow') + \
        colored(dev, 'green', attrs=['bold'])
    print(text)

info = sys.version_info
text = colored('#### PYTHON   : ', 'yellow') + colored("%s.%s.%s" % (info[0], info[1], info[2]), 'green',
                                                       attrs=['bold'])
print(text)
print('\r\n')


def printwarning():
    if warned:
        return
    t = threading.Timer(60.0, printwarning)
    t.daemon = True
    t.start()
    text = colored(
        "Warning: you are running odoo with the following parameters: ", 'green')
    if db_name:
        text += colored(' DB: ' + db_name + ' ', 'red',
                        'on_blue', attrs=['bold']) + ' '
    if module:
        text += colored(' MODULE: ' + module + ' ', 'red',
                        'on_blue', attrs=['bold']) + ' '
    if install and install == 'True':
        text += colored(' INSTALL: YES ', 'red',
                        'on_yellow', attrs=['bold']) + ' '
    if dev:
        text += colored(' DEV: ' + dev + ' ', 'red',
                        'on_blue', attrs=['bold']) + ' '
    print(text)


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True


if __name__ == '__main__':
    killer = GracefulKiller()
    try:
        if version and str(version) != str(Repository(odoo_path).head.shorthand):
            cmd = [CWD + '/clean-change-branch.sh', str(version)]
            if test_db == 'True':
                db_to_drop = db_name
                with Popen(['dropdb', db_name], cwd=odoo_path, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
                    print(colored(f'Dropping db {db_to_drop}', 'yellow'))
                    process.wait()

            with Popen(cmd, cwd=odoo_path, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
                print(colored('#### Switching branches from ', 'yellow') + colored(str(Repository(odoo_path).head.shorthand),
                      'green', attrs=['bold']) + colored(' -> ', 'yellow') + colored(str(version), 'green', attrs=['bold']))
                while True:
                    line = process.stdout.readline().decode('utf8').rstrip()
                    text = colored(line, 'white')
                    print(text)
                    if not line:
                        break
        with Popen(command, cwd=odoo_path, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as process:
            in_traceback = False  # State to track if we're currently processing a traceback block
            while not killer.kill_now:
                stripped_line = process.stdout.readline().decode('utf8').rstrip()
                color = 'blue' if not in_traceback else 'red'
                if ' ? odoo' in stripped_line:
                    color = 'cyan'
                elif ' INFO ' in stripped_line:
                    color = 'blue'
                elif ' WARNING ' in stripped_line or 'FileNotFoundError:' in stripped_line:
                    color = 'yellow'
                elif ' ERROR ' in stripped_line:
                    color = 'red'
                    in_traceback = True
                in_traceback = color == 'red'
                text = colored(stripped_line, color)
                print(text)
                warned = False
    except Exception as e:
        error = colored("Could not execute command %r" % command[0], 'yellow')
        print(error)
