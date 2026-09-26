# ==========================================================
# CIMS - Issue Management Choices
# ==========================================================

# ----------------------------------------------------------
# MODULE
# ----------------------------------------------------------
# Module yang dapat dilaporkan melalui Issue Management
ISSUE_MODULES = [
    ("KAIZEN", "Kaizen"),
    ("PROBLEM", "Problem"),
    ("IMPROVEMENT", "Improvement"),
]


# ----------------------------------------------------------
# CATEGORY
# ----------------------------------------------------------
# Jenis issue yang dapat dilaporkan
ISSUE_CATEGORIES = [
    ("BUG_ERROR", "Bug / Error"),
    ("DATA_ISSUE", "Data Issue"),
    ("SYSTEM_IMPROVEMENT", "System Improvement"),
    ("NEW_FEATURE", "New Feature"),
    ("REPORT_ISSUE", "Report Issue"),
    ("OTHER", "Other"),
]


# ----------------------------------------------------------
# PRIORITY
# ----------------------------------------------------------
ISSUE_PRIORITIES = [
    ("HIGH", "High"),
    ("MEDIUM", "Medium"),
    ("LOW", "Low"),
]


# ----------------------------------------------------------
# STATUS
# ----------------------------------------------------------
# Workflow:
#
# OPEN
#   ↓
# IN_PROGRESS
#   ↓
# FINISH
#   ↓
# CLOSE
#
# Jika requestor menyatakan issue masih terjadi:
#
# FINISH
#   ↓
# IN_PROGRESS
#
ISSUE_STATUS = [
    ("OPEN", "Open"),
    ("IN_PROGRESS", "In Progress"),
    ("FINISH", "Finish"),
    ("CLOSE", "Close"),
]