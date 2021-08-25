class Interface:
    def __init__(self, running_config=None, switch_name=None, switch_vlans=None):
        """Interface object to correlate configuration information to object attributes
        
        
        Args:
            switch_name (str, optional): Switch hostname. Defaults to None.
            running_config (str, optional): Switch running-config. Defaults to None.
            switch_vlans (list, optional): List of named_tuples. Entries include 
                                           vlan ID and vlan name. Defaults to None.
        """        
        self.running_config = running_config
        self.switch_name = switch_name
        self.switch_vlans = switch_vlans
        self.name = None
        self.type = None
        self.description = None
        self.is_access_port = None
        self.vlan = None
        self.vlan_name = None
        self.admin_down = None
        self.ise_compliant = None