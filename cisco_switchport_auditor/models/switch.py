from typing import Optional, List
from pydantic import BaseModel

class Switch(BaseModel):

    """Switch object to correlate configuration information to object attributes"""

    config: Optional[str]
    config_filename: Optional[str]
    config_restconf: Optional[dict]
    hostname: Optional[str]
    interfaces: Optional[List]
    ip_address: Optional[str]
    vlans: Optional[List]

    class Config:
        validate_assignment = True
