# Cisco Switchport Auditor

## Table of Contents
- [Cisco Switchport Auditor](#cisco-switchport-auditor)
  - [Table of Contents](#table-of-contents)
- [Project Summary](#project-summary)
- [Motivation for this tool](#motivation-for-this-tool)
- [How it works](#how-it-works)
  - [Obtaining the data](#obtaining-the-data)
  - [Parsing the data](#parsing-the-data)
  - [Structuring/Managing Parsed Data](#structuringmanaging-parsed-data)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating switch objects from running-configs:](#generating-switch-objects-from-running-configs)
    - [1. SSH into a switch to obtain its running-config](#1-ssh-into-a-switch-to-obtain-its-running-config)
    - [2. Importing a directory of configuration files](#2-importing-a-directory-of-configuration-files)
    - [3. Using RESTCONF to obtain data](#3-using-restconf-to-obtain-data)
  - [Using Switch & Interface Objects](#using-switch--interface-objects)
    - [Switch Objects Attributes](#switch-objects-attributes)
    - [Interface Object Attributes:](#interface-object-attributes)
    - [Find switchports that are access ports without NAC (network access control) configuration](#find-switchports-that-are-access-ports-without-nac-network-access-control-configuration)
    - [Find switchports that do not have an interface description and are access ports and in VLAN 350](#find-switchports-that-do-not-have-an-interface-description-and-are-access-ports-and-in-vlan-350)
    - [Find which switches have VLAN 948 configured](#find-which-switches-have-vlan-948-configured)
  - [Exporting to Excel](#exporting-to-excel)
- [Modifying the project for your specific usage](#modifying-the-project-for-your-specific-usage)
  - [Modifying to obtain new interface configuration details - regex/text based output](#modifying-to-obtain-new-interface-configuration-details---regextext-based-output)
    - [Interface configuration value check](#interface-configuration-value-check)
    - [Check if configuration line/command is present in interface config](#check-if-configuration-linecommand-is-present-in-interface-config)
    - [Check if a subset of configuration lines/commands are present in the interface config](#check-if-a-subset-of-configuration-linescommands-are-present-in-the-interface-config)
  - [Modifying to obtain new interface configuration details - RESTCONF](#modifying-to-obtain-new-interface-configuration-details---restconf)
- [SSH considerations](#ssh-considerations)
- [Potential Improvements](#potential-improvements)
- [Credits](#credits)


# Project Summary
Parses Cisco switch configuration into Switch & Interface objects to access configuration details of the aforementioned in a programatic manner. Works with SSH, RESTCONF, or with running/start-up config files.

# Motivation for this tool
I wanted to develop a tool to review Cisco switchport/interface configurations in a programable way. I found I was making a lot of custom scripts and wanted something that made the data obtained easy to work with and was scalable. Network programability is also a strong interest of mine. I hope someone else will be able to find use out of it as I have.
<br />
<br />

# How it works

## Obtaining the data

* By using SSH to log into a device and using the output of the command `show running-config` 
* By providing a directory that contains text files of the running-configs/startup-configs 
* By using RESTCONF to obtain YANG model data

## Parsing the data

Once the data has been obtained, it must be parsed to be stored and used programmatically. 

For textual outputs of the configuraiton that have been obtained over SSH or via a configuration file, I utilitized a project called [CiscoConfParse](https://github.com/mpenning/ciscoconfparse). Essentially, what this does is use regex logic to find relevant configuration information.

For output returned via RESTCONF -- JSON is returned so that can be iterated and parsed by using python dictionaries. 

The parsers can be found in the `/parsers` directory. The parsers are responsibile for obtaining and then assigning the parsed data to models which will be explained in the following section.

## Structuring/Managing Parsed Data

There are two classes (`Switch` & `Interface`) in the `/models` directory. All configuration details (e.g. interface names, VLAN ids, hostnames, etc) that are parsed are added to these objects as attributes so they can be iterated through and reviewed/audited. `Interface` objects are found within each `Switch` object inside a list attribute. Greater explanation (with examples) is shown in the [Using Switch & Interface Objects section](#using-switch--interface-objects).



# Installation
1. Git clone this project and change your working directory to its downloaded location
2. Execute in terminal `pip install -r requirements.txt`

# Usage

Navidate to the `cisco_switchport_auditor/cisco_switchport_auditor` directory

## Generating switch objects from running-configs:
<br />

### 1. SSH into a switch to obtain its running-config

```python
from master_functions import parse_from_SSH_output

hosts = ['10.0.0.1', '10.0.0.2']

switches = parse_from_SSH_output(hosts, save_to_excel=False)
```
<br />


### 2. Importing a directory of configuration files

```python
from master_functions import parse_from_config_file

config_files = '/home/myuser/configs'

switches = parse_from_config_file(config_files, save_to_excel=False)
```
<br />

### 3. Using RESTCONF to obtain data

```python
from master_functions import parse_from_restconf

hosts = ['10.0.0.1', '10.0.0.2']

switches = parse_from_restconf(hosts, save_to_excel=False)
```

## Using Switch & Interface Objects

Once a list of switch objects have been instantiated and the configuration parsed, you can use the switch (and attached interface objects) to evaluate object attributes for auditing purposes. Two examples have been provided below.

I have personally used this tool to audit a network that was comprised of roughly 25,000 access ports. Evaluating network configuration in an automated and programmatic way is very scalable, less prone to human-error, and can be executed on demand if configured as a service on a schedule or callable by some type of API. Essentially, your ability to be creative is your limitation.

The information obtained with this tool can be used in a variety of ways. A couple of examples are to write the information to a database, an excel file or send notifications. 

As a final note, there isn't parity in the model/object attributes obtained via the various methods/parsers (i.e. SSH, restconf). What is available for each method is tracked in the table below. Support may eventually be added in the future to add more attributes or achieve greater parity

<br />

### Switch Objects Attributes

Attribute | Type | Description | Example | SSH Support | Config File Support | RESTCONF Support
| :--- | :---: | --- | --- | :---: | :---: | :---: | 
config | str | Switch's running-config | N/A | :heavy_check_mark: | :heavy_check_mark: | :x: |
config_filename | str | Switch's config file name | myswitch.conf | :x: | :heavy_check_mark: | :x: |
config_restconf | dict | Switch's running-config as JSON | N/A | :x: | :x: | :heavy_check_mark: |
hostname | str | The Switch's hostname | MY_SWITCH | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
interfaces | list | A list of interface objects | N/A | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
ip_address (optional) | str | Switch's management IP | 10.0.0.1 | :heavy_check_mark: | :x: | :heavy_check_mark: |
vlans | list | A list of named tuples that contains <br> the VLAN name and VLAN ID | [vlan(id=300, name='Test_VLAN_300'), <br> vlan(id=400, name='Test_VLAN_400') | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |

### Interface Object Attributes:

Attribute | Type | Description | Example | SSH Support | Config File Support | RESTCONF Support
| :--- | :---: | --- | --- | :---: | :---: | :---: | 
admin_down | bool | Returns True if admin shutdown | True OR False  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
config | str | Interface specific running config | ...<br> description Test Description <br> switchport access vlan 10 <br> switchport mode access <br> switchport port-security <br> ... | :heavy_check_mark: | :heavy_check_mark: | :x: |
config_restconf | dict | Interface's running-config as JSON | N/A | :x: | :x: | :heavy_check_mark: |
description | str | Interface's description | Test Description  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
is_access_port | bool | Returns True if access Port | True OR False | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
is_trunk_port | bool | Returns True if trunk Port | True OR False | :x: | :x: | :heavy_check_mark: |
ise_compliant | bool | Matches a subset of commands <br> see the method for more details | True OR False  | :heavy_check_mark: | :heavy_check_mark: | :x: |
name | str | The interface's name | GigabitEthernet2/0/1 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
switch_hostname | str | The Switch's hostname| MY_SWITCH  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
switch_vlans | list | A list of named tuples that contains <br> the VLAN name and VLAN ID | [vlan(id=300, name='Test_VLAN_300'), <br> vlan(id=400, name='Test_VLAN_400')] | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
type | str | Interface media type | GigabitEthernet  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
vlan | int | VLAN ID of the interface | 345  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
vlan_name | str | VLAN name of the interface | TEST_VLAN  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
voice_vlan | int | Voice VLAN ID | 250  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
voice_vlan_name | str | Voice VLAN name | TEST_VOICE_VLAN  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |




### Find switchports that are access ports without NAC (network access control) configuration
```python
for switch in switches:
    for interface in switch.interfaces:
        if interface.is_access_port == True and interface.ise_compliant != True:
             # Write to database
             # Write to excel file
             # Send notification to network team
             # Your cool idea here!
```
   
### Find switchports that do not have an interface description and are access ports and in VLAN 350
```python
for switch in switches:
    for interface in switch.interfaces:
        if not interface.description and interface.is_access_port == True and interface.vlan == 350:
             # Write to database
             # Write to excel file
             # Send notification to network team
             # Your cool idea here!
```

### Find which switches have VLAN 948 configured
```python
for switch in switches:
    for vlan in switch.vlans:
        if vlan.id == 948:
             # Write to database
             # Write to excel file
             # Send notification to network team
             # Your cool idea here!
```

## Exporting to Excel

I've added in functionality to the main functions mentioned at the beginning of the [usage](#usage) section. Setting the arg `save_to_excel` to `True` will generate an excel file in the directory the program is run in. 1 excel file will be created with a new excel worksheet created for each switch (named after the switch's hostname). Inside each worksheet will be entries for each interface found on the switch referenced in the worksheet name.

# Modifying the project for your specific usage

I've endeavoured to write this project in a way where adding new configuration checks can be done easily for myself in the future. I've documented the process so when I come back in 6 months I won't forget. Hopefully others can benefit from this as well! :) After following the instructions below you can use your new object attribute in the same manner described in the [usage](#usage) section of this document. As this project is focused on interface configuration/details, I have only included instructions on how to modify interface-related details. Below are instructions to modify both the regex (SSH & file-based textual conf) and RESTCONF parsers.

As a further note, I am using the [pydantic](https://github.com/samuelcolvin/pydantic) project that allows you to define what the type value is for the attributes you are adding. This also enforces that no extra attributes are added or no attributes can be updated with incorrect type definitions. See the `Interface` class in `/models/interface.py` for examples. Keep this in mind when creating new object attributes referenced in the instructions below.


## Modifying to obtain new interface configuration details - regex/text based output

-----
### Interface configuration value check
<br />

Extract a specific value from a line of configuration. In example, say we wanted to obtain `300` from `switchport access vlan 300`.

* Step 1: In `/parsers/parser_config_interface_regex.py`, create a new method that uses the method `_obtain_config_data_from_regex_group` method. See the method `_determine_vlan` for an example.

* Step 2: `_obtain_config_data_from_regex_group` requires a couple of args. One is a regex with a group match (i.e. `^\s*switchport\saccess\svlan\s+(\d+)$`). The other is a `no_match_value` which is a value to set VLAN to if nothing is found in the configuration while parsing. It could be a bool or a string of `N/A` - whatever your preference.

* Step 3: Create a new class attribute in `models/interface.py` (i.e. `vlan: Optional[int]`). See the file for examples.

* Step 4: Add your method (created in Step 1) to `_parse_config_for_data` in  `/parsers/parser_config_interface_regex.py`. There will be some examples there for your reference.

* Step 5 (Optional): Update the `README.md` file with your new attribute information in the table documenting the various object attributes
<br />
<br />

-------
### Check if configuration line/command is present in interface config
<br />

Checks if a line of configuration is present in the interface specific running-config. An example of this is if the interface is administraively shutdown. Will return `True` if there is a match and `False` if there is no match...

* Step 1: In `/parsers/parser_config_interface_regex.py`, create a new method that uses the method `_check_if_config_line_present` method. See the method `_determine_if_admin_down` for an example.

* Step 2: `_check_if_config_line_present` requires one arg - a regex with no group. In this example, to find an administratively shtudown interface, `^\s+shutdown$` was used

* Step 3: Create a new class attribute in `models/interface.py` (i.e. `admin_down: Optional[bool]`). See the file for examples.

* Step 4: Add your method (created in Step 1) to `_parse_config_for_data` in  `/parsers/parser_config_interface_regex.py`. There will be some examples there for your reference.

* Step 5 (Optional): Update the `README.md` file with your new attribute information in the table documenting the various object attributes
<br />
<br />

-------
### Check if a subset of configuration lines/commands are present in the interface config
<br />

Similar to [here](#check-if-configuration-linecommand-is-present-in-interface-config), but checks if an entire command/configuration subset is in the interface configuration.

Example, if you wanted to see if a switchport had ALL the AAA/ISE configuration commands present in it for switchport security compliance, this functionality would check this. If all the ISE/AAA switchport commands are present in the interface specific running configuration, the result of `True` will be returned but if ANY are missing a result of `False` will be returned

* Step 1: In `/parsers/parser_config_interface_regex.py`, create a new method that uses the method `_check_config_subset` method. See the method `_ise_compliance_check` for an example.

* Step 2: `_check_config_subset` requires one arg, which is a list of commands. Review `_ise_compliance_check` in `/parsers/parser_config_interface_regex.py` for an example of a configuration/command subset to provide `_check_config_subset`

* Step 3: Create a new class attribute in `models/interface.py` (i.e. `ise_compliant: Optional[bool]`). See the file for examples.

* Step 4: Add your method (created in Step 1) to `_parse_config_for_data` in  `/parsers/parser_config_interface_regex.py`. There will be some examples there for your reference.

* Step 5 (Optional): Update the `README.md` file with your new attribute information in the table documenting the various object attributes

## Modifying to obtain new interface configuration details - RESTCONF

* Step 1: In `parsers/parser_config_interface_restconf.py`, create a new method that searches and parses the JSON data from one of the YANG models queried. See the existing methods in the file for examples
* Step 2: Add your new method to the `_parse_interface_restconf_data` method. Your method (created in step 1) should return the value you want to assign to an attribute of the interface object/model.
* Step 3: Create a new class attribute in `models/interface.py` (i.e. `admin_down: Optional[bool]`). See the file for examples.
* Step 4 (Optional): Update the `README.md` file with your new attribute information in the table documenting the various object attributes

# SSH considerations
* The only SSH command entered is `show running-configuration` to obtain the running-config to be parsed
* By default, session logs will be saved for each switch logged into
* The session log files will be saved inside a host specific subfolder
* The subfolder will be saved in a `/LOGS` folder. If a `/LOGS` folder is not present one will be created in the same working directory the program is executed in
* If a device is not logged into as a result of a connection failure or invalid credentials, the script will continue but will print an error message into the terminal

# Potential Improvements
* Obtain interface live operational data over SSH (e.g. switchport operational statuses, switchport operational duplex status, switchport input/output errors)
* Expand functionality to obtain more than basic switch information. For my purposes, I developed this to search interfaces

# Credits

Thanks to [mpenning](https://github.com/mpenning) and all the contributers from the [ciscoconfparse](https://github.com/mpenning/ciscoconfparse) project!