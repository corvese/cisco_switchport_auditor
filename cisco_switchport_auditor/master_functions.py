from getpass import getpass
import os

from models.switch import Switch
from parsers.parser_config_switch_regex import ParserRunningConfigSwitch
from parsers.parser_config_switch_restconf import ParserConfigSwitchRestconf
from utilities import excel_functions
from utilities.ssh_handler import ssh_handler
from utilities.restconf_requests import restconf_request, validate_yang_model_availability


def parse_from_restconf(list_of_hosts, save_to_excel=False):
    """Queries a list of switches via RESTCONF. YANG model data is returned as JSON
    and then parsed through to return a list of switch objects that can be iterated
    through to view configuration details. 
    
    There is an optional flag to export the interface configurations to an excel file.
    Interface configurations are saved to one excel file with each switch's interfaces
    grouped by sheet with the sheetname being the switch hostname the interface belongs
    to

    Note: Interface objects are also returned inside a list attribute of the switch
    class/object

    Args:
        list_of_hosts (list): list of hostnames or IP addresses

        save_to_excel (bool, optional): Set to True to export interface object
        data to excel. Defaults to False.

    Returns:
        list: list of Switch objects
    """     

    username = input('Username: ')
    password = getpass()

    switches = []

    for host in list_of_hosts:
        
        yang_model_check = validate_yang_model_availability(host, username, password)

        if yang_model_check is True:

            switch = Switch(ip_address=host)

            config_restconf = restconf_request(host, username, password, "Cisco-IOS-XE-native", ":native")
            vlans_restconf = restconf_request(host, username, password, "Cisco-IOS-XE-vlan-oper", ":vlans")

            ParserConfigSwitchRestconf(switch, config_restconf, vlans_restconf)
            
            switches.append(switch)

            if save_to_excel is True:
                output_switchport_info_to_excel(switches)

    print_total_switches_and_switchports_searched(switches)

    return switches


def parse_from_config_file(config_files_directory, save_to_excel=False):
    """Parses switch running-configs and returns a list of switch objects
    that can be iterated through to view configuration details. 
    
    There is an optional flag to export the interface configurations to an excel
    file. Interface configurations are saved to one file with each switch's interfaces
    grouped by sheet with the sheetname being the switch hostname the interface belongs
    to

    Note: Interface objects are also returned inside a list attribute of the switch
    class/object

    Args:
        config_files_directory (str): Path of location where running config files are

        save_to_excel (bool, optional): Set to True to export interface object
        data to excel. Defaults to False.

    Returns:
        list: list of Switch objects
    """

    switches = []

    for file in os.listdir(config_files_directory):
        switch = Switch(config_filename=file)

        with open(f'{config_files_directory}/{file}', 'r') as text_file:
            config = text_file.read()
            ParserRunningConfigSwitch(switch, config)
            switches.append(switch)

    if save_to_excel is True:
        output_switchport_info_to_excel(switches)

    print_total_switches_and_switchports_searched(switches)

    return switches

def parse_from_SSH_output(list_of_hosts, save_to_excel=False):
    """Logs into a list of switches via SSH, does "show running-config"
    and parses the switch running-configs and returns a list of switch objects
    that can be iterated through to view configuration details. There is
    an optional flag to export the interface configurations to an excel file.
    Interface configurations are saved to one file with each switch's interfaces
    grouped by sheet with the sheetname being the switch the interface belongs to

    Note: Interface objects are also returned inside a list attribute of the switch
    class/object

    Args:
        list_of_hosts (list): list of hostnames or IP addresses

        save_to_excel (bool, optional): Set to True to export interface object
        data to excel. Defaults to False.

    Returns:
        list: list of Switch objects
    """

    username = input('Username: ')
    password = getpass()

    switches = []

    for host in list_of_hosts:
        switch = Switch(ip_address=host)

        with ssh_handler(host=host, username=username, password=password) as ssh_session:
            running_config = ssh_session.send_command_timing('show running-config')

        ParserRunningConfigSwitch(switch, running_config)
        switches.append(switch)

    if save_to_excel is True:
        output_switchport_info_to_excel(switches)

    print_total_switches_and_switchports_searched(switches)

    return switches


def print_total_switches_and_switchports_searched(switch_objects):
    """Iterates through a list of switch objects and prints the
    total number of switches and total number of interfaces searched

    Args:
        switch_objects (list): list of switch objects

    Returns:
        None
    """

    number_of_switches = len(switch_objects)
    total_number_of_switchports = 0
    for switch in switch_objects:
        total_number_of_switchports += len(switch.interfaces)

    print(f"Searched - Total Switches: {number_of_switches} | Total Switchports: {total_number_of_switchports}")


def output_switchport_info_to_excel(switch_objects):
    """Creates a list of pandas DFs. Each DF is comprised of a switch's
    interface objects (which is a list attribute of the switch object).
    DFs are then written to an excel sheet. One DF per excel sheet and
    the excel sheet is named after the switch hostname


    Args:
        switch_objects (list): list of switch objects

    Returns:
        An excel file is written to the working directory
    """
    switch_interface_dfs = excel_functions.create_list_of_dfs_from_switch_interface_objects(
        switch_objects)
    excel_functions.write_dfs_to_excel_sheets(switch_interface_dfs)
