from ciscoconfparse import CiscoConfParse

class ParserRunningConfigInterface:
    def __init__(self, Interface, interface_config):
        """This class will parse interface specific configuration to obtain
        configuration details such as VLAN, interface name, description, etc.
        Those details are then added to the Interface object as attributes

        Args:
            Interface (obj): Interface object
            interface_config (str): interface specific configuration
        """
        self._interface = Interface

        self._interface_config = interface_config
        self._add_config_to_interface_object()

        self._config_split = self._format_config_for_CiscoConfParse()
        self._parser = self._add_interface_config_to_parser()
        self._interface_config_lines = self._obtain_interface_specific_line_config_objects()
        
        self._parse_config_for_data()



    def _format_config_for_CiscoConfParse(self):
        """CiscoConfParse requires input into the parser as a list
        rather than a string. This method splits the running
        configuration into a list. One entry per line

        Returns:
            list: interface configuration as a list. one line per entry
        """
        return self._interface_config.splitlines()

    def _add_interface_config_to_parser(self):
        """Initializes the CiscoConfParse parse object to parse
        the interface specific running-config to obtain config
        parameters/details to update the interface object with

        Returns:
            object: CiscoConfParse parse object
        """
        return CiscoConfParse(self._config_split, syntax='ios')

    def _obtain_interface_specific_line_config_objects(self):
        """Uses CiscoConfParse to generate cfgline objects to
        be iterated through to obtain specific configuration details
        such as VLAN, description, etc.

        Returns:
            list: list of CiscoConfParse IOSCfgLine Objects
        """
        return self._parser.find_objects(r'^interface.*$')[0]

    def _add_config_to_interface_object(self):
        """Updates the interface object with an object attribute
        equal to the running-config as a string for use if ever
        required
        """        
        self._interface.config = self._interface_config
    

    def _parse_config_for_data(self):
        """Function that consolidates obtaining all the various
        interface configuration details
        """
        self._interface.name = self._determine_name()
        self._interface.type = self._determine_type()
        self._interface.description = self._determine_description()
        self._interface.admin_down = self._determine_if_admin_down()
        self._interface.vlan = self._determine_vlan()
        self._interface.voice_vlan = self._determine_voice_vlan()
        self._interface.is_access_port = self._determine_is_access_port()
        self._interface.vlan_name = self._correlate_vlan_id_to_name()
        self._interface.voice_vlan_name = self._correlate_voice_vlan_id_to_name()
        self._interface.ise_compliant = self._ise_compliance_check()



    def _check_if_config_line_present(self, regex):
        """Searches CiscoConfParse IOSCfgLine objects that match the entire regex (group 0)
        If found, return True, else False

        Args:
            regex (str): regex
        """        
        return bool(self._interface_config_lines.re_match_iter_typed(regex, default=bool(), untyped_default=True, group=0))


    def _obtain_config_data_from_regex_group(self, regex, no_match_value=None):
        """Returns regex group 1 value. If there is no match, the value specified
        in no_match_value is returned

        Args:
            regex (str): Regex of the string you want to match
            no_match_value (bool, str): A value to return if no match is found
        """        
        return self._interface_config_lines.re_match_iter_typed(regex, default=no_match_value, untyped_default=True)


    def _determine_is_access_port(self):
        """Uses CiscConfParse to ascertain if an interface is an access port
        by using regexes against an interface's configuration

        Note: Sometimes switchport mode access is not present despite a VLAN
        being configured. The extra conditional check accounts for this scenario

        Note: Ensure this method is AFTER _determine_vlan in _parse_config_for_data

        Returns:
            bool: Returns true if is an access port, else False
        """

        if self._check_if_config_line_present('^\s*switchport\smode\saccess$'):
            return True
        elif self._interface.vlan != None:
            return True
        else:
            return False

   
    def _determine_if_admin_down(self):
        """Uses CiscConfParse to ascertain if an interface is an admin down
        by using regexes against an interface's configuration

        Returns:
            bool: Returns true if is shutdown/admin down, else False
        """
        return self._check_if_config_line_present('^\s+shutdown$')


    def _determine_type(self):
        """Uses CiscConfParse to ascertain an interface's media type (e.g. 
        GigabitEthernet, FastEthernet, etc)

        Returns:
            str: Interface type (e.g. GigabitEthernet)
        """
        return self._parser.re_match_iter_typed(r'^interface\s*([A-Za-z]+)\d\S+$', default='')
    
    def _determine_name(self):
        """Uses CiscConfParse to ascertain an interface's name

        Returns:
            str: Interface name (e.g. GigabitEthernet1/0/14)
        """
        return self._parser.re_match_iter_typed(r'^interface\s*(\S+)$', default='')

    def _determine_description(self):
        """Uses CiscConfParse to ascertain an interface's description

        Returns:
            str: Interface description (e.g. Access Point)
        """

        return self._obtain_config_data_from_regex_group('^\s*description\s*(.*)$', None)


    def _determine_vlan(self):
        """Uses CiscConfParse to ascertain an interface's VLAN id

        Returns:
            str: VLAN ID (e.g. 549)
        """
        return self._obtain_config_data_from_regex_group('^\s*switchport\saccess\svlan\s+(\d+)$', None)

    def _determine_voice_vlan(self):
        """Uses CiscoConfParse to ascertain an interface's voice VLAN id

        Returns:
            str: VLAN ID (e.g. 349)
        """
        return self._obtain_config_data_from_regex_group('^\s*switchport\svoice\svlan\s+(\d+)$', None)

    def _correlate_vlan_id_to_name(self):
        """Tries to correlate a VLAN id to a VLAN name. Will only execute if
        interface.switch_vlans is not None and the interface is configured
        with a VLAN ID (set in `self._determine_vlan`)

        Returns:
            str: VLAN name (e.g. DATA_VLAN)
        """
        if self._interface.switch_vlans is not None:
            for vlan in self._interface.switch_vlans:
                if vlan.id == self._interface.vlan:
                    return vlan.name
                else:
                    continue
        else:
            return None

    def _correlate_voice_vlan_id_to_name(self):
        """Tries to correlate a VLAN id to a VLAN name. Will only execute if
        interface.switch_vlans is not None and the interface is configured
        with a voice VLAN ID (set in `self._determine_voice_vlan`)

        Returns:
            str: voice VLAN name (e.g. VOICE_VLAN)
        """
        if self._interface.switch_vlans is not None:
            for vlan in self._interface.switch_vlans:
                if vlan.id == self._interface.voice_vlan:
                    return vlan.name
                else:
                    continue
        else:
            return None


    def _check_config_subset(self, subset_of_commands):
        """Input is a subset of configuration commands with 1 line per entry in a list. 
        If all entries in the list of commands are present in the interface's configuration,
        the result is True, else it is false

        Therefore, if in compliance, will return True, if not, False, which indicates commands
        are missing from the interface's configuration

        Args:
            subset_of_commands (list): a list of configuration commands. 1 line per entry

        Returns:
            bool: Returns true if all commands found in an interface's configuration, else False
        """
        
        return all(item in self._config_split for item in subset_of_commands)

    def _ise_compliance_check(self):
        '''
        Input is the switchport configuration with 1 line per entry in a list. 
        Similar to the ise_configuration below

        If in compliance will return True, if not, False
        '''

        ise_configuration = [
            ' authentication priority dot1x mab',
            ' authentication port-control auto',
            ' mab',
            ]

        return self._check_config_subset(ise_configuration)