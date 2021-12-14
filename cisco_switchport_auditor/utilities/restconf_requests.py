from re import match
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def restconf_request(host, username, password, yang_model, yang_path, port=443, verify=False, timeout=15):
    """Makes a RESTCONF request

    Args:
        host (str): Hostname or IP address
        username (str): Username allowed to make RESTCONF requests
        password (str): Password of user allowed to make RESTCONF requests
        yang_model (str): YANG model to be queried (e.g. Cisco-IOS-XE-native)
        yang_path (str): YANG model path of resource to be queried
        port (int, optional): HTTPS port. Defaults to 443.
        verify (bool, optional): Validate certificate is trusted. Defaults to False.
        timeout (int, optional): Timeout before request is considered timed out. Defaults to 15.

    Returns:
        [dict]: If successful, JSON output from RESTCONF device is returned
    """
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
    headers = {"Accept": "application/yang-data+json"}

    url = f"https://{host}:{port}/restconf/data/{yang_model}{yang_path}"

    try: 
        restconf_data = requests.get(url=url, headers=headers, auth=(username, password), verify=verify, timeout=timeout)

        http_status_code = restconf_data.status_code

        if http_status_code == 200:
            return restconf_data.json()

        elif http_status_code == 204:
            print(f'{http_status_code} - No content was returned from: {host}')
            return False

        elif http_status_code == 400:
            print(f"400 - Bad HTTP request. Check if {host} is running restconf or your URL is correct")
            return False

        elif http_status_code == 401:
            print(f"401 - Credentials for {host} invalid")
            return False

        elif http_status_code == 403:
            print(f"403 - HTTP Forbidden. Check {username} has correct access rights on {host}")
            return False

        elif http_status_code == 404:
            print(f"404 - HTTP not found. Check if {host} is running restconf or your URL is correct")
            return False

        elif http_status_code == 405:
            print(f'405 - HTTP Method Not Allowed. Check if your request to {host} is correct')
            return False
   
    except requests.exceptions.Timeout as HTTP_Timeout:
        print(HTTP_Timeout)
        print(f"HTTP request timed out to {host} after {timeout} seconds")

    except requests.exceptions.ConnectionError as ConnectionError:
        print(ConnectionError)
        print(f"An HTTP connection error was experieced to {host}")

    except Exception as e:
        print(e)
        print(f"Catch-all exception for failed http request to {host}. Request failed")

def validate_yang_model_availability(host, username, password):
    """Checks if the YANG models that this project uses are supported on the device
    before making additional RESTCONF requests.

    If RESTCONF is supported but some modules are missing, it will provide feedback
    as to which models are available and which are unavailable

    Args:
        host (str): Hostname or IP address
        username (str): Username allowed to make RESTCONF requests
        password (str): Password of user allowed to make RESTCONF requests

    Returns:
        [bool]: If all models are found, returns True, else False if missing or request fails
    """    
        
    request = restconf_request(host, username, password, "netconf-state", "/capabilities")

    supported_YANG_models = ["Cisco-IOS-XE-native", "Cisco-IOS-XE-vlan-oper"]

    if request:

        potential_YANG_models = request["ietf-netconf-monitoring:capabilities"]["capability"]

        matched_YANG_models = []

        unmatched_YANG_models = []

        for supported_model in supported_YANG_models:
            for potential_model in potential_YANG_models:
                if supported_model in potential_model:
                    matched_YANG_models.append(supported_model)
                    break
            if supported_model not in matched_YANG_models:
                unmatched_YANG_models.append(supported_model)

        if len(unmatched_YANG_models) == 0:
            return True

        if len(unmatched_YANG_models) > 0:
            print("-" * 100)
            print(f"""Restconf unable to continue for {host} as not all of the YANG models this project utilises
    are supported by {host}.

    YANG Models suppported by {host}: {matched_YANG_models}
    YANG Models not supported by {host}: {unmatched_YANG_models}
    """)
            return False

    else:
        return False