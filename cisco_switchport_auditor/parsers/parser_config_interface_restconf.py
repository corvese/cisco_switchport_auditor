
class ParserConfigInterfaceRestconf:
    """This class will parse interface specific RESTCONF configuration
    to obtain configuration details such as VLAN, interface name, description,
    etc. Those details are then added to the Interface object as attributes

    Args:
        Interface (obj): Interface object
        interface_config_restconf (dict): JSON data of RESTCONF interface configuration
    """
    def __init__(self, Interface, interface_config_restconf):

        self._interface = Interface
        self._interface_config_restconf = interface_config_restconf

        self._add_interface_restconf_config_to_interface_object()
        self._parse_interface_restconf_data()


    def _parse_interface_restconf_data(self):
        """Function that consolidates obtaining all the various
        interface configuration details
        """
        self._interface.name = self._determine_name()
        self._interface.description = self._determine_description()
        self._interface.admin_down = self._determine_if_admin_down()
        self._interface.vlan = self._determine_vlan()
        self._interface.voice_vlan = self._determine_voice_vlan()
        self._interface.is_access_port = self._determine_is_access_port()
        self._interface.is_trunk_port = self._determine_is_trunk_port()
        self._interface.vlan_name = self._correlate_vlan_id_to_name()
        self._interface.voice_vlan_name = self._correlate_voice_vlan_id_to_name()



    def _add_interface_restconf_config_to_interface_object(self):
        """Updates the interface object with the interface specific
        restconf configuration
        """
        self._interface.config_restconf = self._interface_config_restconf


    def _determine_name(self):
        """Combines interface type (e.g. GigabitEthernet) and interface name (0/1/1)
        to provide the actual interface name (e.g. GigabitEthernet0/1/1) to the
        interface_object

        Returns:
            str: Interface name
        """
        interface_name = f"{self._interface.type}{self._interface_config_restconf['name']}"
        return interface_name


    def _determine_description(self):
        """Obtains the interface description value from interface specific
        restconf configuration

        Returns:
            str: Interface's description
        """
        try:
            return self._interface_config_restconf['description']

        except KeyError:
            return None


    def _determine_if_admin_down(self):
        """Obtains the interface's administrative status from interface specific
        restconf configuration

        Returns:
            bool: Admin/shutdown status. True if shutdown
        """
        return 'shutdown' in self._interface_config_restconf.keys()


    def _determine_vlan(self):
        """Obtains the interface's access vlan value from interface specific
        restconf configuration

        Returns:
            str: Interface's access VLAN
        """
        try:
            return self._interface_config_restconf['switchport']['Cisco-IOS-XE-switch:access']['vlan']['vlan']
        except KeyError:
            return None

    def _determine_voice_vlan(self):
        """Obtains the interface's voice vlan value from interface specific
        restconf configuration

        Returns:
            int: Interface's voice VLAN
        """
        try:
            return self._interface_config_restconf['switchport']['Cisco-IOS-XE-switch:voice']['vlan']['vlan']
        except KeyError:
            return None

    def _determine_is_access_port(self):
        """Determines if the interface is an access port from interface specific
        restconf configuration

        Returns:
            bool: Is access port. True if access port
        """

        try:
            return "access" in self._interface_config_restconf['switchport']['Cisco-IOS-XE-switch:mode'].keys()

        except KeyError:
            self._interface.is_access_port = True


    def _determine_is_trunk_port(self):
        """Determines if the interface is a trunk from interface specific
        restconf configuration

        Returns:
            bool: Is trunk port. True if trunk port
        """
        try:
            return "trunk" in self._interface_config_restconf['switchport']['Cisco-IOS-XE-switch:mode'].keys()

        except KeyError:
            return False


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