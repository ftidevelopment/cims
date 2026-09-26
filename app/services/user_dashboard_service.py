from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from app.models.problem import Problem
from app.models.improvement import Improvement
from app.models.kaizen import Kaizen
from app.models.kaizen_award_period import KaizenAwardPeriod

from app.core.choices.problem import ProblemStatus
from app.core.choices.kaizen import KAIZEN_STATUS
from app.services.authorization_service import AuthorizationService


class UserDashboardService:
    """
    Dashboard setelah user login.

    Dashboard ini berbeda dengan Public Dashboard.

    Public Dashboard:
        - Overall / company performance

    User Dashboard:
        - Personal activity user yang sedang login
        - 6 bulan terakhir
        - KPI Problem / Improvement / Kaizen / Award
        - Monthly activity untuk Problem / Improvement / Kaizen
        - Action Required

    Definisi My Problem:
        - reporter_employee_id = employee yang sedang login
        - is_active = True
        - problem_date berada dalam periode 6 bulan terakhir

    Definisi My Improvement:
        - owner_employee_id = employee yang sedang login
        - is_active = True
        - created_at berada dalam periode 6 bulan terakhir

    Definisi My Kaizen:
        - employee_id = employee yang sedang login
        - is_active = True
        - created_at berada dalam periode 6 bulan terakhir

    Definisi Action Required - Problem:
        - Problem.is_active = True
        - Problem.status = OPEN
        - User mempunyai hak untuk melakukan Assign Problem
        - Authorization menggunakan can_assign_problem()
    """

    def __init__(self):

        self.authorization_service = (
            AuthorizationService()
        )

    # ==========================================================
    # GET PERIOD
    # ==========================================================

    def get_period(self):

        today = date.today()

        # ------------------------------------------------------
        # Periode 6 bulan:
        # bulan berjalan + 5 bulan sebelumnya
        #
        # Contoh:
        # Jika sekarang September 2026:
        #
        # April 2026
        # Mei 2026
        # Juni 2026
        # Juli 2026
        # Agustus 2026
        # September 2026
        # ------------------------------------------------------

        start_date = (
            today.replace(day=1)
            - relativedelta(months=5)
        )

        end_date = today

        return {
            "start_date": start_date,
            "end_date": end_date
        }

    # ==========================================================
    # PROBLEM ACTION REQUIRED
    # ==========================================================

    def get_problem_action_required(self, user):
        """
        Get Problems that currently require
        the logged-in user's action.

        Current workflow:

            OPEN
              ↓
            Assign Problem
              ↓
            IN_PROGRESS

        A Problem is Action Required when:

            - Problem is active
            - Problem status is OPEN
            - Current user is authorized
              to assign the Problem

        Authorization is handled by:

            AuthorizationService.can_assign_problem()
        """

        # ------------------------------------------------------
        # Get all active OPEN Problems
        # ------------------------------------------------------

        problems = (
            Problem.query
            .filter(
                Problem.is_active.is_(True),

                Problem.status == ProblemStatus.OPEN
            )
            .order_by(
                Problem.problem_date.asc(),
                Problem.id.asc()
            )
            .all()
        )

        action_required = []

        # ------------------------------------------------------
        # Check authorization for each Problem
        # ------------------------------------------------------

        for problem in problems:

            can_assign = (
                self.authorization_service
                .can_assign_problem(
                    user=user,
                    problem=problem
                )
            )

            if can_assign:

                action_required.append(
                    {
                        "type": "problem",

                        "action": "assign",

                        "label": "Assign Problem",

                        "item": problem
                    }
                )

        return action_required

    # ==========================================================
    # MAIN DASHBOARD
    # ==========================================================

    def get_dashboard(
        self,
        employee_id,
        user=None
    ):

        period = self.get_period()

        start_date = period["start_date"]
        end_date = period["end_date"]

        # ======================================================
        # ACTION REQUIRED
        # ======================================================

        problem_action_required = []
        improvement_action_required = []
        kaizen_action_required = []

        if user is not None:

            problem_action_required = (
                self.get_problem_action_required(
                    user=user
                )
            )

            improvement_action_required = (
                self.get_improvement_action_required(
                    user=user
                )
            )

            kaizen_action_required = (
                self.get_kaizen_action_required(
                    user=user
                )
            )

        # ======================================================
        # MY PROBLEM
        # ======================================================

        my_problem_query = (
            Problem.query
            .filter(
                Problem.is_active.is_(True),

                Problem.reporter_employee_id == employee_id,

                Problem.problem_date >= start_date,

                Problem.problem_date <= end_date
            )
            .order_by(
                Problem.problem_date.desc(),
                Problem.id.desc()
            )
        )

        my_problem_count = (
            my_problem_query
            .count()
        )

        my_problems = (
            my_problem_query
            .limit(5)
            .all()
        )

        # ======================================================
        # MY IMPROVEMENT
        # ======================================================

        # Gunakan batas akhir exclusive.
        #
        # Contoh:
        # end_date = 2026-09-07
        #
        # Maka:
        # created_at < 2026-09-08 00:00:00
        #
        # sehingga seluruh data tanggal 07-09-2026
        # tetap ikut dihitung.

        end_date_improvement = (
            end_date + timedelta(days=1)
        )

        my_improvement_query = (
            Improvement.query
            .filter(
                Improvement.is_active.is_(True),

                Improvement.owner_employee_id == employee_id,

                Improvement.created_at >= start_date,

                Improvement.created_at < end_date_improvement
            )
            .order_by(
                Improvement.created_at.desc(),
                Improvement.id.desc()
            )
        )

        my_improvement_count = (
            my_improvement_query
            .count()
        )

        my_improvements = (
            my_improvement_query
            .limit(5)
            .all()
        )

        # ======================================================
        # MY KAIZEN
        # ======================================================

        # Gunakan batas akhir exclusive agar seluruh Kaizen
        # pada end_date ikut terhitung.

        end_date_kaizen = (
            end_date + timedelta(days=1)
        )

        my_kaizen_query = (
            Kaizen.query
            .filter(
                Kaizen.is_active.is_(True),

                Kaizen.employee_id == employee_id,

                Kaizen.created_at >= start_date,

                Kaizen.created_at < end_date_kaizen
            )
            .order_by(
                Kaizen.created_at.desc(),
                Kaizen.id.desc()
            )
        )

        my_kaizen_count = (
            my_kaizen_query
            .count()
        )

        my_kaizens = (
            my_kaizen_query
            .limit(5)
            .all()
        )

        # ======================================================
        # AWARD KPI
        # ======================================================

        award_count = (
            KaizenAwardPeriod.query
            .filter(
                KaizenAwardPeriod.is_active.is_(True),

                KaizenAwardPeriod.start_date <= end_date,

                KaizenAwardPeriod.end_date >= start_date
            )
            .count()
        )

        # ======================================================
        # MONTHLY ACTIVITY
        # ======================================================

        monthly_activity = []

        # ------------------------------------------------------
        # Loop 6 bulan
        #
        # Contoh September 2026:
        #
        # April 2026
        # May 2026
        # June 2026
        # July 2026
        # August 2026
        # September 2026
        # ------------------------------------------------------

        for i in range(6):

            month_date = (
                start_date
                + relativedelta(months=i)
            )

            next_month = (
                month_date
                + relativedelta(months=1)
            )

            # ==================================================
            # PROBLEM - MONTHLY
            # ==================================================

            # Problem menggunakan problem_date.
            #
            # Untuk bulan sebelumnya:
            #
            # month_date <= problem_date < next_month
            #
            # Untuk bulan berjalan:
            #
            # month_date <= problem_date <= end_date
            #
            # agar tanggal setelah hari ini tidak ikut dihitung.

            if month_date.year == end_date.year and \
               month_date.month == end_date.month:

                monthly_problem_count = (
                    Problem.query
                    .filter(
                        Problem.is_active.is_(True),

                        Problem.reporter_employee_id == employee_id,

                        Problem.problem_date >= month_date,

                        Problem.problem_date <= end_date
                    )
                    .count()
                )

            else:

                monthly_problem_count = (
                    Problem.query
                    .filter(
                        Problem.is_active.is_(True),

                        Problem.reporter_employee_id == employee_id,

                        Problem.problem_date >= month_date,

                        Problem.problem_date < next_month
                    )
                    .count()
                )

            # ==================================================
            # IMPROVEMENT - MONTHLY
            # ==================================================

            # Improvement menggunakan created_at (datetime).

            monthly_improvement_end = next_month

            # Untuk bulan berjalan, batasi sampai besok
            # agar seluruh data hari ini ikut dihitung,
            # tetapi data future tidak ikut.

            if month_date.year == end_date.year and \
               month_date.month == end_date.month:

                monthly_improvement_end = (
                    end_date + timedelta(days=1)
                )

            monthly_improvement_count = (
                Improvement.query
                .filter(
                    Improvement.is_active.is_(True),

                    Improvement.owner_employee_id == employee_id,

                    Improvement.created_at >= month_date,

                    Improvement.created_at < monthly_improvement_end
                )
                .count()
            )

            # ==================================================
            # KAIZEN - MONTHLY
            # ==================================================

            # Kaizen menggunakan created_at (datetime).

            monthly_kaizen_end = next_month

            # Untuk bulan berjalan, batasi sampai besok.

            if month_date.year == end_date.year and \
               month_date.month == end_date.month:

                monthly_kaizen_end = (
                    end_date + timedelta(days=1)
                )

            monthly_kaizen_count = (
                Kaizen.query
                .filter(
                    Kaizen.is_active.is_(True),

                    Kaizen.employee_id == employee_id,

                    Kaizen.created_at >= month_date,

                    Kaizen.created_at < monthly_kaizen_end
                )
                .count()
            )

            # ==================================================
            # APPEND MONTHLY DATA
            # ==================================================

            monthly_activity.append(
                {
                    "month": month_date.strftime("%b %Y"),

                    "problem": monthly_problem_count,

                    "improvement": monthly_improvement_count,

                    "kaizen": monthly_kaizen_count
                }
            )

        # ======================================================
        # RETURN
        # ======================================================

        return {

            # --------------------------------------------------
            # PERIOD
            # --------------------------------------------------

            "period": {

                "start_date": start_date,

                "end_date": end_date

            },

            # --------------------------------------------------
            # KPI
            # --------------------------------------------------

            "kpi": {

                "problem": my_problem_count,

                "improvement": my_improvement_count,

                "kaizen": my_kaizen_count,

                "award": award_count

            },

            # --------------------------------------------------
            # MY PROBLEM
            # --------------------------------------------------

            "my_problem": {

                "total": my_problem_count,

                "items": my_problems

            },

            # --------------------------------------------------
            # MY IMPROVEMENT
            # --------------------------------------------------

            "my_improvement": {

                "total": my_improvement_count,

                "items": my_improvements

            },

            # --------------------------------------------------
            # MY KAIZEN
            # --------------------------------------------------

            "my_kaizen": {

                "total": my_kaizen_count,

                "items": my_kaizens

            },

            # --------------------------------------------------
            # MONTHLY ACTIVITY
            # --------------------------------------------------

            "monthly_activity": monthly_activity,

            # --------------------------------------------------
            # ACTION REQUIRED
            # --------------------------------------------------

            "action_required": {
                "problem": problem_action_required,

                "improvement": improvement_action_required,

                "kaizen": kaizen_action_required,

                "total": (
                    len(problem_action_required)
                    + len(improvement_action_required)
                    + len(kaizen_action_required)
                ),
            }

        }

    def get_improvement_action_required(self, user):

        improvements = (
            Improvement.query
            .filter(
                Improvement.is_active.is_(True),
                Improvement.approved_by_employee_id.is_(None),
                Improvement.verification_result.isnot(None),
            )
            .order_by(
                Improvement.created_at.asc(),
                Improvement.id.asc(),
            )
            .all()
        )

        action_required = []

        for improvement in improvements:

            can_approve = (
                self.authorization_service
                .can_approve_improvement(
                    user,
                    improvement,
                )
            )

            if can_approve:

                action_required.append(
                    {
                        "type": "improvement",
                        "action": "approve",
                        "label": "Approve Improvement",
                        "item": improvement,
                    }
                )

        return action_required

    # ==========================================================
    # KAIZEN ACTION REQUIRED
    # ==========================================================

    def get_kaizen_action_required(self, user):
        """
        Get Kaizen that currently require
        the logged-in user's approval.

        Current workflow:

            PROPOSAL
            ↓
            Approve / Reject
            ↓
            APPROVED / REJECTED

        A Kaizen is Action Required when:

            - Kaizen is active
            - Kaizen status is Proposal
            - Current user is authorized
            to approve the Kaizen

        Authorization is handled by:

            AuthorizationService.can_approve_kaizen()
        """

        kaizens = (
            Kaizen.query
            .filter(
                Kaizen.is_active.is_(True),

                Kaizen.status == KAIZEN_STATUS[1][0]
            )
            .order_by(
                Kaizen.created_at.asc(),
                Kaizen.id.asc()
            )
            .all()
        )

        action_required = []

        # ------------------------------------------------------
        # Check authorization for each Kaizen
        # ------------------------------------------------------

        for kaizen in kaizens:

            can_approve = (
                self.authorization_service
                .can_approve_kaizen(
                    user=user,
                    kaizen=kaizen
                )
            )

            if can_approve:

                action_required.append(
                    {
                        "type": "kaizen",

                        "action": "approve",

                        "label": "Approve Kaizen",

                        "item": kaizen
                    }
                )

        return action_required