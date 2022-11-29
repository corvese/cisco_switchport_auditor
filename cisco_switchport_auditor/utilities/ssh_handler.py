import datetime
import os
import socket

from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

class ssh_handler:
    def __init__(self, host, username, password, secret=None, device_type='cisco_ios', port=22):
        """A SSH handler class that utilizes Netmko. Manages creating a log folder and
        basic send command functions. Support added to use with context management

        Args:
            host (str): Hostname or IP address of device to SSH into
            username (str): SSH device username
            password (str): SSH device password
            secret (str, optional): Enable password if required. Defaults to None.
            device_type (str, optional): Netmiko Device type. Defaults to 'cisco_ios'.
            port (int, optional): SSH Port. Defaults to 22.
        """        
        self.host = host
        self.username = username
        self.password = password
        self.secret = secret
        self.device_type = device_type
        self.port = port

        self._ssh_session = None
        self.hostname = None

    def __enter__(self):
        self._create_host_log_folder_if_missing()
        self.connect()
        return self
        
    def __exit__ (self, type, value, traceback):
        self.disconnect()

    def __del__(self):
        self.disconnect()

    def _create_host_log_folder_if_missing(self):
        """Checks if there is a folder called LOGS. If one is not present
        a LOGS folder will be created. Then creates a host specific folder
        within the logs folder equal to the IP or hostname of the host
        """        
        base_logs_dir = os.path.exists("LOGS")
        if base_logs_dir is True:
            pass
        if base_logs_dir is False:
            os.mkdir("LOGS")

        host_specific_dir = os.path.exists(f"LOGS/{self.host}/")
        if host_specific_dir is True:
            pass
        if host_specific_dir is False:
            os.mkdir(f"LOGS/{self.host}/")


    def connect(self):
        """Connects to a device via SSH using Netmiko and sets a 
        time-specific logging path

        Raises:
            NetmikoTimeoutException: See Netmiko docs
            NetmikoAuthenticationException: See Netmiko docs
        """        

        now = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

        try:
            self._ssh_session = ConnectHandler(
                ip = self.host,
                device_type = self.device_type,
                username = self.username,
                password = self.password,
                secret = self.secret,
                port = self.port,
                session_log = f"LOGS/{self.host}/{self.host}__{now}.log",
                banner_timeout = 45

            )
                        
            self._enter_enable_mode()

            self._get_hostname()

        except NetmikoTimeoutException:
            print(F'************* Attempt to connect to {self.host} timed out *****************')
            raise NetmikoTimeoutException

        except NetmikoAuthenticationException:
            print(F'************* Invalid credentials used on: {self.host} *****************')
            raise NetmikoAuthenticationException

    def _get_hostname(self):
        """Obtains the hostname of the device from netmiko setting base_prompt feature
        """
        self.hostname = self._ssh_session.base_prompt

    def _enter_enable_mode(self):
        """Enters enable mode in netmiko ssh session if an enable mode password was provided
        """
        if self.secret is not False:
            self._ssh_session.enable()


    def send_command(self, *args, **kwargs):
        """See Netmiko 'send_command' method

        Returns:
            str: Output from network device
        """        
        return self._ssh_session.send_command(*args, **kwargs)

    def send_command_timing(self, *args, **kwargs):
        """See Netmiko 'send_command_timing' method

        Returns:
            str: Output from network device
        """        
        return self._ssh_session.send_command_timing(*args, **kwargs)

    def disconnect(self):
        """Takes a Netmiko SSH session and gracefully disconnects
        """        
        try:
            self._ssh_session.disconnect()
        except (socket.error, OSError):
            pass
        except AttributeError:
            pass