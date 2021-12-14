from collections import namedtuple

from models.interface import Interface
from parsers.parser_config_interface_restconf import ParserConfigInterfaceRestconf


class ParserConfigSwitchRestconf:
    """This class will parse a switch's configuration obtained via restconf
    to obtain configuration details such as hostname, interfaces, VLANs.
    Those details are then added to the Switch object as attributes

    Args:
        Switch (obj): Instantiated switch object
        switch_config_restconf (dict): JSON return from restconf of switch configuration
        switch_vlans_restconf (dict): JSON return from restconf of switch VLANs
    """
    def __init__(self, Switch, switch_config_restconf, switch_vlans_restconf):
        self._switch = Switch

        self.config_restconf = switch_config_restconf["Cisco-IOS-XE-native:native"]
        self._switch_vlans_restconf = switch_vlans_restconf["Cisco-IOS-XE-vlan-oper:vlans"]['vlan']
        self._switch_interfaces_config_restconf = switch_config_restconf["Cisco-IOS-XE-native:native"]["interface"]

        self._add_restconf_config_to_switch_object()
        self._parse_restconf_config_for_data()


    def _add_restconf_config_to_switch_object(self):
        """Updates the switch object with an object attribute that is based on the
        JSON return from the restconf request formatted based on YANG model Cisco-IOS-XE-native
        """
        self._switch.config_restconf = self.config_restconf

    def _parse_restconf_config_for_data(self):
        """Function that consolidates obtaining all the various
        switch configuration details
        """
        self._switch.hostname = self._get_hostname()
        self._switch.vlans = self._get_vlans()
        self._switch.interfaces = self._get_interfaces()

    def _get_hostname(self):
        """
        Obtains the hostname of a switch restconf config based on
        YANG model Cisco-IOS-XE-native

        Returns:
            str: Hostname of the switch (i.e. MY_SWITCH)
        """
        try:
            hostname = self.config_restconf['hostname']

        except IndexError:
            hostname = "Unknown"

        return hostname

    def _get_vlans(self):
        """
        Finds all VLANs present on a switch as well as the VLAN name. For each VLAN,
        an entry is made into a named tuple. The VLAN ID is accessed by the id name and
        the VLAN name is accessed via the name.

        E.g. vlan.id, vlan.name

        Returns:
            list: A list of named tuples
        """
        vlans = []

        for vlan in self._switch_vlans_restconf:
            vlan_tuple = namedtuple('vlan', ['id', 'name'])

            vlan_id = vlan['id']
            vlan_name = vlan["name"]

            vlan = vlan_tuple(vlan_id, vlan_name)

            vlans.append(vlan)

        return vlans


    def _get_interfaces(self):
        """Sorts and parses through JSON switch interface configuration. Only certain interface types
        defined in `interfaces_types_to_audit` are considered. For each interface, an interface object
        is instantiated, interface type and switch hostname are set as attributes as they are not
        available in the JSON interface configuration. The interface object is then passed to the
        restconf interface parser to have remaining configuration details assigned to the interface
        object

        Returns:
            [list]: List of updated interface objects is returned
        """

        interfaces = []

        interface_types_to_audit = ["FastEthernet", "GigabitEthernet", "TwoGigabitEthernet", "FiveGigabitEthernet", "TenGigabitEthernet"]

        for interface_type in self._switch_interfaces_config_restconf:
            if interface_type in interface_types_to_audit:
                for interface_config_restconf in self._switch_interfaces_config_restconf[interface_type]:
                    interface = Interface()
                    interface.type = interface_type
                    interface.switch_hostname = self._switch.hostname
                    interface.switch_vlans = self._switch.vlans
                    ParserConfigInterfaceRestconf(interface, interface_config_restconf)
                    interfaces.append(interface)

        return interfaces
        