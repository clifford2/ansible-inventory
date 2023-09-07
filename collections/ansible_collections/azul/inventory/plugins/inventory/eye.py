#!/usr/bin/env python3
# Ansible inventory plugin for EYE
# Data is provided by EYE front end "health/ansibleplugin" action
#
# Based on examples from:
# - https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html
# - https://termlen0.github.io/2019/11/16/observations/
# - https://github.com/termlen0/custom-inventory-plugin/blob/master/inventory_plugins/my_csv_plugin.py

DOCUMENTATION = '''
    name: azul.inventory.eye
    short_description: Returns Ansible inventory from EYE
    description:
        - Returns Ansible inventory from EYE
    options:
        plugin:
            description: token that ensures this is a source file for the 'eye' plugin
            required: true
            choices: ['azul.inventory.eye']
        cache:
            description: Should we cache results?
            required: false
        baseurl:
            description: URL for the EYE front end
            required: true
        group:
            description: EYE host group to include
            required: false
    extends_documentation_fragment:
        - inventory_cache
'''

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
# from ansible.errors import AnsibleError, AnsibleParserError
from ansible.errors import AnsibleParserError
from urllib.parse import urlparse
import urllib.request
import ssl
import json
# import sys


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'azul.inventory.eye'

    def verify_file(self, path):
        '''Return true/false if this is possibly a valid file for this plugin to consume'''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('.yaml', '.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        '''Return dynamic inventory from source'''
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Read the inventory YAML file
        config = self._read_config_data(path)
        # self.load_cache_plugin()
        cache_key = self.get_cache_key(path)
        try:
            # Store the options from the YAML file
            self.plugin = config['plugin']
            # self.cache = config['cache']
            self.baseurl = config['baseurl']
            self.group = config['group']
        except Exception as e:
            raise AnsibleParserError(
                'All correct options required: {}'.format(e))
        # validate baseurl
        parsedurl = urlparse(self.baseurl)
        if not parsedurl.scheme or not parsedurl.netloc:
            raise AnsibleParserError("'baseurl' doesn't appear to be a valid URL")

        # cache may be True or False at this point to indicate if the inventory is being refreshed
        # get the user's cache option too to see if we should save the cache if it is changing
        user_cache_setting = config['cache']

        # read if the user has caching enabled and the cache isn't being refreshed
        attempt_to_read_cache = user_cache_setting and cache
        # update if the user has caching enabled and the cache is being refreshed; update this value to True if the cache has expired below
        cache_needs_update = user_cache_setting and not cache

        # attempt to read the cache if inventory isn't being refreshed and the user has caching enabled
        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True

        if not user_cache_setting or cache_needs_update:
            results = self.get_inventory()

        if cache_needs_update:
            # set the cache
            self._cache[cache_key] = results

        if attempt_to_read_cache:
            self.set_cache_plugin()

        self.populate(results)

    def get_inventory(self):
        # Get host config data from EYE Front End /health/config URL, and filter appropriately
        if self.group:
            reqgroup = self.group
        else:
            reqgroup = 'All'

        # Create urllib.request context to ignore SSL validation error
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Get the JSON data
        url = self.baseurl + '/health/ansibleplugin/group/' + reqgroup
        with urllib.request.urlopen(url, context=ctx) as response:
            json_text = response.read()
        json_parsed = json.loads(json_text)
        # print(json.dumps(json_parsed));
        return json_parsed

    def populate(self, json_parsed):
        # Add hosts from /health/config/format/json data
        # knowngroups = {}
        # for host in json_parsed:
        #    if not host['groupname'] in knowngroups:
        #        self.inventory.add_group(host['groupname'])
        #        knowngroups[host['groupname']] = True
        #    self.inventory.add_host(host=host['uname_n'], group=host['groupname'])

        # Add hosts from /health/ansible data
        for group in json_parsed:
            if group != '_meta':
                self.inventory.add_group(group)
                for host in json_parsed[group]['hosts']:
                    self.inventory.add_host(host=host, group=group)
        for host in json_parsed['_meta']['hostvars']:
            for attrib in json_parsed['_meta']['hostvars'][host]:
                self.inventory.set_variable(host, attrib, json_parsed['_meta']['hostvars'][host][attrib])
