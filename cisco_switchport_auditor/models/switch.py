class Switch:
    def __init__(self, running_config=None, ip_address=None):
        """Switch object to correlate configuration information to object attributes

        Args:
            running_config (str, optional): A switch's running/startup config. Defaults to None.
            ip_address (stri, optional): Switch's management IP address. Defaults to None.
        """
        
        self.running_config = running_config
        self.ip_address = ip_address
        self.hostname = None
        self.vlans = []
        self.interfaces = []