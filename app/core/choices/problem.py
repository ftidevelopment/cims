# ==========================================
# Problem Priority
# ==========================================

class ProblemPriority:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


PROBLEM_PRIORITY = (
    (ProblemPriority.LOW, "Low"),
    (ProblemPriority.MEDIUM, "Medium"),
    (ProblemPriority.HIGH, "High"),
)


# ==========================================
# Problem Status
# ==========================================

class ProblemStatus:
    OPEN = "Open"
    IN_PROGRESS = "On Progress"
    COMPLETED = "Completed"
    CLOSED = "Closed"


PROBLEM_STATUS = (
    (ProblemStatus.OPEN, "Open"),
    (ProblemStatus.IN_PROGRESS, "On Progress"),
    (ProblemStatus.COMPLETED, "Completed"),
    (ProblemStatus.CLOSED, "Closed"),
)


# ==========================================
# Problem Source
# ==========================================

class ProblemSource:
    INTERNAL = "Internal"
    CUSTOMER = "Customer"
    AUDIT = "Audit"
    PRODUCTION = "Production"
    WAREHOUSE = "Warehouse"
    OTHER = "Other"


PROBLEM_SOURCE = (
    (ProblemSource.INTERNAL, "Internal"),
    (ProblemSource.CUSTOMER, "Customer"),
    (ProblemSource.AUDIT, "Audit"),
    (ProblemSource.PRODUCTION, "Production"),
    (ProblemSource.WAREHOUSE, "Warehouse"),
    (ProblemSource.OTHER, "Other"),
)


# ==========================================
# PIC Status
# ==========================================

class PICStatus:
    ASSIGNED = "Assigned"
    WORKING = "Working"
    COMPLETED = "Completed"


PIC_STATUS = (
    (PICStatus.ASSIGNED, "Assigned"),
    (PICStatus.WORKING, "Working"),
    (PICStatus.COMPLETED, "Completed"),
)