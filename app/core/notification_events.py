class NotificationEvent:

    # ==========================================
    # Problem
    # ==========================================

    PROBLEM = "PROBLEM"

    PROBLEM_CREATED = "CREATED"
    PROBLEM_ASSIGNED = "ASSIGNED"
    PROBLEM_UPDATED = "UPDATED"
    PROBLEM_STATUS_CHANGED = "STATUS_CHANGED"
    PROBLEM_COMPLETED = "COMPLETED"
    PROBLEM_CLOSED = "CLOSED"

    # ==========================================
    # Issue
    # ==========================================

    ISSUE = "ISSUE"

    ISSUE_CLARIFICATION_REQUESTED = (
        "CLARIFICATION_REQUESTED"
    )

    ISSUE_CLARIFICATION_RESPONDED = (
        "CLARIFICATION_RESPONDED"
    )

    # ==========================================
    # Improvement
    # ==========================================

    IMPROVEMENT = "IMPROVEMENT"

    IMPROVEMENT_CREATED = "CREATED"
    IMPROVEMENT_UPDATED = "UPDATED"
    IMPROVEMENT_ASSIGNED = "ASSIGNED"
    IMPROVEMENT_SUBMITTED = "SUBMITTED"
    IMPROVEMENT_APPROVED = "APPROVED"
    IMPROVEMENT_REJECTED = "REJECTED"
    IMPROVEMENT_IMPLEMENTED = "IMPLEMENTED"
    IMPROVEMENT_VERIFIED = "VERIFIED"
    IMPROVEMENT_COMPLETED = "COMPLETED"

    # ==========================================
    # Kaizen
    # ==========================================

    KAIZEN = "KAIZEN"

    KAIZEN_CREATED = "CREATED"
    KAIZEN_SUBMITTED = "SUBMITTED"
    KAIZEN_APPROVED = "APPROVED"
    KAIZEN_REJECTED = "REJECTED"
    KAIZEN_IMPLEMENTED = "IMPLEMENTED"
    KAIZEN_AWARDED = "AWARDED"

    # ==========================================
    # Module List
    # ==========================================

    MODULES = [
        PROBLEM,
        ISSUE,
        IMPROVEMENT,
        KAIZEN,
    ]

    # ==========================================
    # Events by Module
    # ==========================================

    EVENTS = {

        # --------------------------------------
        # Problem
        # --------------------------------------

        PROBLEM: [

            PROBLEM_CREATED,

            PROBLEM_ASSIGNED,

            PROBLEM_UPDATED,

            PROBLEM_STATUS_CHANGED,

            PROBLEM_COMPLETED,

            PROBLEM_CLOSED,
        ],

        # --------------------------------------
        # Issue
        # --------------------------------------

        ISSUE: [

            ISSUE_CLARIFICATION_REQUESTED,

            ISSUE_CLARIFICATION_RESPONDED,
        ],

        # --------------------------------------
        # Improvement
        # --------------------------------------

        IMPROVEMENT: [

            IMPROVEMENT_CREATED,

            IMPROVEMENT_UPDATED,

            IMPROVEMENT_ASSIGNED,

            IMPROVEMENT_SUBMITTED,

            IMPROVEMENT_APPROVED,

            IMPROVEMENT_REJECTED,

            IMPROVEMENT_IMPLEMENTED,

            IMPROVEMENT_VERIFIED,

            IMPROVEMENT_COMPLETED,
        ],

        # --------------------------------------
        # Kaizen
        # --------------------------------------

        KAIZEN: [

            KAIZEN_CREATED,

            KAIZEN_SUBMITTED,

            KAIZEN_APPROVED,

            KAIZEN_REJECTED,

            KAIZEN_IMPLEMENTED,

            KAIZEN_AWARDED,
        ],
    }

    # ==========================================
    # Validation
    # ==========================================

    @classmethod
    def is_valid_module(
        cls,
        module,
    ):

        return module in cls.MODULES

    @classmethod
    def is_valid_event(
        cls,
        module,
        event,
    ):

        if module not in cls.EVENTS:

            return False

        return event in cls.EVENTS[module]

    @classmethod
    def get_modules(cls):

        return cls.MODULES.copy()

    @classmethod
    def get_events(
        cls,
        module,
    ):

        return cls.EVENTS.get(
            module,
            [],
        ).copy()