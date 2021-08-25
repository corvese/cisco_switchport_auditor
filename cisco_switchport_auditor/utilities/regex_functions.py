import re

def regex_search(regex, configuration):
    """Searches a list for a match based on a regex capture group

    Args:
        regex (str): String representation of a regex with 1 capture group
        configuration (list): A list of strings

    Returns:
        If a match is found in the list of strings, the value of the first 
        capture group is returned
    """    
    for entry in configuration:
        if re.search(regex, entry):
            match = re.search(regex, entry).group(1)
            return match
        else:
            continue
    
    return False