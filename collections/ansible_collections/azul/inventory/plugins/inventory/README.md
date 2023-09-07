# Ansible inventory configuration file for EYE inventory plugin

For caching to work, set `cache` and `cache_plugin` below
See <https://docs.ansible.com/ansible/latest/plugins/cache.html>
For `jsonfile` cache, set `_uri` - see `ansible-doc -t cache jsonfile`:
`export ANSIBLE_CACHE_PLUGIN_CONNECTION=/tmp/ansible`


- <https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html>
- <https://docs.ansible.com/ansible/latest/plugins/inventory.html#plugin-list>
- <https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html>
	- <https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory/generator.py>
- <https://termlen0.github.io/2019/11/16/observations/>
	- <https://github.com/termlen0/custom-inventory-plugin/blob/master/inventory_plugins/my_csv_plugin.py>
# Test with:

```
ansible-inventory -i aix_inventory.yaml --playbook-dir . --list
ansible -i aix_inventory.yaml --playbook-dir . all --list-hosts
```
