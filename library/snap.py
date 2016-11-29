#!/usr/bin/python
#
# docs
#
DOCUMENTATION = '''
---
module: snap
short_description: Manages snap packages
description:
  - Manages snap packages for Ubuntu Linux.
options:
  name:
    description:
      - A package name, like C(foo).
    required: false
    default: null
  state:
    description:
      - Indicates the desired package state.
      - C(present) ensures the package is present.
      - C(absent) ensures the package is absent.
      - C(latest) ensures the package is present and the latest version.
    required: false
    default: present
    choices: [ "present", "absent", "latest" ]
  upgrade:
    description:
      - Upgrade all installed packages to their latest version.
    required: false
    default: no
    choices: [ "yes", "no" ]
'''

EXAMPLES = '''
# Remove "foo" package
- snap: name=foo state=absent

# Install the package "foo"
- snap: name=foo state=present

# Update package "foo" to latest version
- snap: name=foo state=latest update_cache=yes

# Update all installed packages to the latest versions
- snap: upgrade=yes
'''

import os
import re

SNAP_PATH="/usr/bin/snap"

def query_package(module, name):
    cmd = "%s list %s" % (SNAP_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc == 0:
        return True
    else:
        return False

def query_latest(module, name):
    cmd = "%s list %s" % (SNAP_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    search_pattern = "(%s)-[\d\.\w]+-[\d\w]+\s+(.)\s+[\d\.\w]+-[\d\w]+\s+" % (name)
    match = re.search(search_pattern, stdout)
    if match and match.group(2) == "<":
        return False
    return True

def upgrade_packages(module):
    if module.check_mode:
        cmd = "%s refresh" % (SNAP_PATH)
    else:
        cmd = "%s refresh" % (SNAP_PATH)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc != 0:
        module.fail_json(msg="failed to upgrade packages")
    if re.search('^OK', stdout):
        module.exit_json(changed=False, msg="packages already upgraded")
    module.exit_json(changed=True, msg="upgraded packages")

def install_package(module, name, state):
    upgrade = False
    installed = query_package(module, name)
    latest = query_latest(module, name)
    if state == 'latest' and not latest:
        upgrade = True
    if installed and not upgrade:
        module.exit_json(changed=False, msg="package already installed")
    if upgrade:
            cmd = "%s install %s" % (SNAP_PATH, name)
    else:
            cmd = "%s install %s" % (SNAP_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc != 0:
        module.fail_json(msg="failed to install %s" % (name))
    module.exit_json(changed=True, msg="installed %s package" % (name))

def remove_package(module, name):
    installed = query_package(module, name)
    if not installed:
        module.exit_json(changed=False, msg="package already removed")
    if module.check_mode:
		cmd = "%s remove %s" % (SNAP_PATH, name)
    else:
		cmd = "%s remove %s" % (SNAP_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc != 0:
        module.fail_json(msg="failed to remove %s" % (name))
    module.exit_json(changed=True, msg="removed %s package" % (name))

# ===================================
# Main control flow

def main():
    module = AnsibleModule(
        argument_spec = dict(
            state = dict(default='present', choices=['present', 'installed', 'absent', 'removed', 'latest']),
            name = dict(type='str'),
            upgrade = dict(default='no', choices=BOOLEANS, type='bool'),
        ),
        required_one_of = [['name', 'upgrade']],
        supports_check_mode = True
    )

    if not os.path.exists(SNAP_PATH):
        module.fail_json(msg="cannot find snap, looking for %s" % (SNAP_PATH))

    # Set LANG env since we parse stdout
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    p = module.params

    # normalize the state parameter
    if p['state'] in ['present', 'installed']:
        p['state'] = 'present'

    if p['state'] in ['absent', 'removed']:
        p['state'] = 'absent'

    if p['upgrade']:
        upgrade_packages(module)

    if p['state'] in ['present', 'latest']:
        install_package(module, p['name'], p['state'])

    if p['state'] in ['enabled']:
        install_package(module, p['name'], p['state'])

    elif p['state'] == 'absent':
        remove_package(module, p['name'])

# Import module snippets.
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()

