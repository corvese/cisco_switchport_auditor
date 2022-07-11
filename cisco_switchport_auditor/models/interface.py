from typing import Optional, List
from pydantic import BaseModel

class Interface(BaseModel):

    """Interface object to correlate configuration information to object attributes"""

    admin_down: Optional[bool]
    config: Optional[str]
    config_restconf: Optional[dict]
    description: Optional[str]
    IPDT_policy: Optional[str]
    is_access_port: Optional[bool]
    is_trunk_port: Optional[bool]
    ise_compliant: Optional[bool]
    name: Optional[str]
    switch_hostname: Optional[str]
    switch_vlans: Optional[List]
    type: Optional[str]
    vlan: Optional[int]
    vlan_name: Optional[str]
    voice_vlan: Optional[int]
    voice_vlan_name: Optional[str]

    class Config:
        validate_assignment = True
