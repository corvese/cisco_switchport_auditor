from collections import namedtuple
from ciscoconfparse import CiscoConfParse

from models.interface import Interface
from parsers.parser_running_config_interface import ParserRunningConfigInterface
from utilities.regex_functions import regex_search

class ParserRunningConfigSwitch:
    def __init__(self, Switch, running_config):
        """This class will a switch's configuration to obtain 
        configuration details such hostname, interfaces, VLANs.
        Those details are then added to the Switch object as attributes

        Args:
            Switch (class): Switch object
            running_config (str): A Cisco switch's running/startup config
        """        
                
        self._switch = Switch
        self._running_config = running_config
        self._running_config_split = self._format_running_config_for_CiscoConfParse()

        self._parser = self._add_running_config_to_parser()

        self._add_running_config_to_switch_object()
        self._parse_running_config_for_data()

    def _format_running_config_for_CiscoConfParse(self):
        """CiscoConfParse requires input into the parse the configuration
        as a list rather than a string. This method Splits the running 
        configuration into a list. One entry per line

        Returns:
            list: switch configuration as a list. one line per entry
        """
        return self._running_config.splitlines()

    def _add_running_config_to_parser(self):
        """Initializes the CiscoConfParse parse object to parse
        the switch running-config to obtain config
        parameters/details to update the switch object with

        Returns:
            object: CiscoConfParse parse object
        """     
        return CiscoConfParse(self._running_config_split, syntax='ios')

    def _add_running_config_to_switch_object(self):
        """Updates the switch object with an object attribute
        equal to the running-config as a string for use if ever
        required
        """      
        self._switch.running_config = self._running_config   

    def _parse_running_config_for_data(self):
        """Function that consolidates obtaining all the various
        switch configuration details
        """                
        self._switch.hostname = self._get_hostname()
        self._switch.vlans = self._get_vlans()
        self._switch.interfaces = self._get_interfaces()

    def _get_hostname(self):
        """Obtains the hostname of a switch via regex from the config

        Returns:
            str: Hostname of the switch (i.e. MY_SWITCH)
        """        
        global_obj = self._parser.find_objects(r'^hostname')[0]
        hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='')

        return hostname
    
    def _get_vlans(self):
        """Finds all VLANs present on a switch as well as the VLAN name. For each VLAN,
        an entry is made into a named tuple. The VLAN ID is accessed by the id name and
        the VLAN name is accessed via the name.

        E.g. vlan.id, vlan.name

        Returns:
            list: A list of named tuples
        """        
        vlans = []

        for vlan_parse_object in self._parser.find_objects_w_child('^vlan\s+\d+$', '^\s+name\s+\S+$'):
            vlan_tuple = namedtuple('vlan', ['id', 'name'])
            vlan_id_regex = "^vlan\s+(\d+)$"
            vlan_name_regex = "^\s+name\s+(\S+)$"

            vlan_id = regex_search(vlan_id_regex, vlan_parse_object.ioscfg)
            vlan_name = regex_search(vlan_name_regex, vlan_parse_object.ioscfg)

            vlan = vlan_tuple(vlan_id, vlan_name)

            vlans.append(vlan)

        return vlans


    def _get_interfaces(self):
        """Finds all interfaces that are FastEthernet, GigabitEthernet, TwoGigabitEthernet and TenGigabitEthernet
        on the switch

        For each interface, an interface object is initialized, config details parsed, and then a list of these 
        interface objects is set to the switch object's attribute `interfaces`

        Returns:
            list: A list of interface objects
        """        
        interfaces = []

        for interface_parse_object in self._parser.find_objects('^interface\s(GigabitEthernet|TenGigabitEthernet|TwoGigabitEthernet|FastEthernet)'):
            interface = Interface()
            parse_interface = ParserRunningConfigInterface(interface, "\n".join(interface_parse_object.ioscfg), self._switch.hostname, self._switch.vlans)
            interfaces.append(interface)

        return interfaces