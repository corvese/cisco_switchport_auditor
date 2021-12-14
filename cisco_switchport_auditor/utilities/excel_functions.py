import pandas as pd
from datetime import datetime

def set_df_name(df, switch):
    """Gives a pandas DF a df_name attribute and names it
    after the switch's hostname

    Args:
        df (object): Pandas DataFrame Object
        switch (object): Switch object

    Returns:
        None
    """    
    df.df_name = switch.hostname

def create_list_of_dfs_from_switch_interface_objects(list_of_switch_objects):
    """A list of switch objects is iterated through. For each switch, all
    switch interfaces objects in the switch.interfaces list attributes are
    added to a pandas DataFrame

    Args:
        list_of_switch_objects (list): list of Switch objects

    Returns:
        list: List of switch specific DFs comprised of switch specific interface objects. 
    """    
    list_of_switch_specific_interface_dfs = []

    for switch in list_of_switch_objects:
        list_of_switch_interface_dicts = [interface.__dict__ for interface in switch.interfaces]
        df = pd.DataFrame(list_of_switch_interface_dicts)
        set_df_name(df, switch)
        list_of_switch_specific_interface_dfs.append(df)
 
    return list_of_switch_specific_interface_dfs

def write_dfs_to_excel_sheets(list_of_switch_specific_interface_dfs):
    """Each DataFrame is comprised of switch specific interface objects. 
    All DFs are written to 1 excel file. Each DF is written to its own 
    excel sheet with the name of the sheet being the switch's hostname 
    that the interfaces in the DF are associated with. The excel file is 
    named after the current date and time and then saved to the current
    working directory

    Args:
        list_of_switch_specific_interface_dfs (list): A list of pandas DataFrames

    Returns:
        None
    """    

    now = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
    writer = pd.ExcelWriter(f'{now}__switchport_audit.xlsx', engine='xlsxwriter')
    for df in list_of_switch_specific_interface_dfs:
        if df.df_name is None:
            continue
        df.to_excel(writer, sheet_name=df.df_name, index=False)
    writer.save()
    print(f'An excel file ({now}__switchport_audit.xlsx) has been saved')

