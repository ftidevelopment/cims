from dataclasses import dataclass, field
from typing import Any


@dataclass
class ServiceResult:
    """
    Standard result object untuk seluruh service di CIMS.
    """

    success: bool = False
    message: str = ""
    data: Any = None

    errors: list = field(default_factory=list)