# EYE as Ansible inventory source

## Deprecated

*This code is no longer maintained publically*.

## About Ansible

About [Ansible](https://www.ansible.com/):

> Ansible is an open source community project sponsored by Red Hat, it's the simplest way to automate IT. Ansible is the only automation language that can be used across entire IT teams from systems and network administrators to developers and managers.

## Ansible Inventories

Ansible works against multiple systems in your infrastructure at the same time. It does this by selecting portions of systems listed in Ansible’s inventory file(s). Besides static inventory files, it also supports dynamic inventory from multiple sources: cloud providers, LDAP, Cobbler, and/or enterprise CMDB systems. Inventory scripts and plugins for various sources already exist, but you can also create your own.

## EYE As Inventory Source

You can use your EYE host list as such an inventory, with the help of an inventory script or plugin.

## Configuration

Once the plugin is installed, you need to configure Ansible to use it - details
[here](https://docs.ansible.com/ansible/latest/plugins/inventory.html) - most
easily done with the `auto` plugin.

To use an inventory plugin, you must provide an inventory source. Most of
the time this is a file containing host information or a YAML configuration
file with options for the plugin.

Example inventory configuration file:

```yaml
---
# Ansible inventory configuration file for EYE inventory plugin
#
# For caching to work, set "cache" and "cache_plugin" below
#   See https://docs.ansible.com/ansible/latest/plugins/cache.html
# For "jsonfile" cache, set "_uri" - see `ansible-doc -t cache jsonfile`:
#   export ANSIBLE_CACHE_PLUGIN_CONNECTION=/tmp/ansible
plugin: azul.inventory.eye
cache: False
cache_plugin: jsonfile
baseurl: "https://eye.example.com/"
group: AUTO_AIX,-AUTO_VIO
```

Some suggested `group` values:

- `All`: All hosts (default)
- `AUTO_AIX,-AUTO_VIO`: All AIX hosts (excluding VIO servers)
- `AUTO_VIO`: All VIO servers
- `AUTO_LINUX,-AUTO_HMC`: All Linux hosts (excluding HMCs)
- `AUTO_HMC`: All HMCs

Additional examples are available in `inventory/*.yml`.

Test with:

```
ansible all --playbook-dir . -i ./inventory/linux.yml --list
```
