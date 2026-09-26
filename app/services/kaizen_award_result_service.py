from datetime import datetime, time, timedelta

from sqlalchemy import func

from app.extensions import db

from app.models.kaizen import Kaizen
from app.models.kaizen_award_score import KaizenAwardScore
from app.models.kaizen_award_period import KaizenAwardPeriod

from app.services.base_service import BaseService
from app.core.service_result import ServiceResult


class KaizenAwardResultService(BaseService):
    """
    Service untuk menampilkan hasil Kaizen Award
    berdasarkan Award Period yang sudah CLOSED.

    Halaman ini bersifat READ ONLY.
    """

    # =========================================================
    # INITIALIZE
    # =========================================================

    def __init__(self):

        pass


    # =========================================================
    # GET CLOSED AWARD PERIODS
    # =========================================================

    def get_closed_periods(self):

        return (
            KaizenAwardPeriod.query
            .filter(
                KaizenAwardPeriod.is_active.is_(True),

                KaizenAwardPeriod.status == "Closed"
            )
            .order_by(
                KaizenAwardPeriod.start_date.desc()
            )
            .all()
        )


    # =========================================================
    # GET AWARD PERIOD
    # =========================================================

    def get_period(self, award_period_id):

        return (
            KaizenAwardPeriod.query
            .filter(
                KaizenAwardPeriod.id == award_period_id,

                KaizenAwardPeriod.is_active.is_(True),

                KaizenAwardPeriod.status == "Closed"
            )
            .first()
        )


    # =========================================================
    # GET RESULT
    # =========================================================

    def get_result(
        self,
        award_period_id,
        page=1,
        per_page=10
    ):
        """
        Mengambil ranking Kaizen berdasarkan total score
        dari seluruh Judges pada Award Period tertentu.
        """

        # -----------------------------------------------------
        # Get Closed Period
        # -----------------------------------------------------

        award_period = self.get_period(
            award_period_id
        )

        if not award_period:

            return ServiceResult(
                success=False,
                message="Closed award period not found.",
                data=None
            )


        # -----------------------------------------------------
        # Date Range
        # -----------------------------------------------------

        start_datetime = datetime.combine(
            award_period.start_date,
            time.min
        )

        end_datetime = datetime.combine(
            award_period.end_date + timedelta(days=1),
            time.min
        )


        # -----------------------------------------------------
        # Score Summary
        # -----------------------------------------------------

        query = (

            db.session.query(

                Kaizen,

                func.count(
                    KaizenAwardScore.id
                ).label(
                    "judges_scored"
                ),

                func.coalesce(
                    func.sum(
                        KaizenAwardScore.score
                    ),
                    0
                ).label(
                    "total_score"
                ),

                func.coalesce(
                    func.avg(
                        KaizenAwardScore.score
                    ),
                    0
                ).label(
                    "average_score"
                )

            )

            # -------------------------------------------------
            # LEFT JOIN SCORE
            # -------------------------------------------------

            .outerjoin(

                KaizenAwardScore,

                (
                    KaizenAwardScore.kaizen_id
                    == Kaizen.id
                )

                &

                (
                    KaizenAwardScore.award_period_id
                    == award_period_id
                )

                &

                (
                    KaizenAwardScore.is_active.is_(True)
                )

                &

                (
                    KaizenAwardScore.scored_at.isnot(None)
                )

            )

            # -------------------------------------------------
            # KAIZEN FILTER
            # -------------------------------------------------

            .filter(

                Kaizen.is_active.is_(True),

                Kaizen.approved_at.isnot(None),

                Kaizen.approved_at >= start_datetime,

                Kaizen.approved_at < end_datetime

            )

            # -------------------------------------------------
            # GROUP
            # -------------------------------------------------

            .group_by(
                Kaizen.id
            )

            # -------------------------------------------------
            # RANKING
            # -------------------------------------------------

            .order_by(

                func.coalesce(
                    func.sum(
                        KaizenAwardScore.score
                    ),
                    0
                ).desc(),

                Kaizen.kaizen_no.asc()

            )
        )


        # -----------------------------------------------------
        # Pagination
        # -----------------------------------------------------

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        # -----------------------------------------------------
        # Prepare Result
        # -----------------------------------------------------

        results = []


        for rank, item in enumerate(
            pagination.items,
            start=((page - 1) * per_page) + 1
        ):

            kaizen = item[0]

            results.append({

                "rank": rank,

                "kaizen": kaizen,

                "judges_scored": item[1],

                "total_score": item[2],

                "average_score": item[3]

            })


        # -----------------------------------------------------
        # Return
        # -----------------------------------------------------

        return ServiceResult(

            success=True,

            message="Kaizen award result retrieved successfully.",

            data={
                "award_period": award_period,

                "results": results,

                "pagination": pagination
            }
        )


    # =========================================================
    # GET KAIZEN RESULT DETAIL
    # =========================================================

    def get_detail(
        self,
        award_period_id,
        kaizen_id
    ):
        """
        Mengambil detail satu Kaizen beserta score
        dari seluruh Judges.
        """

        # -----------------------------------------------------
        # Get Closed Period
        # -----------------------------------------------------

        award_period = self.get_period(
            award_period_id
        )

        if not award_period:

            return ServiceResult(
                success=False,
                message="Closed award period not found.",
                data=None
            )


        # -----------------------------------------------------
        # Get Kaizen
        # -----------------------------------------------------

        kaizen = (
            Kaizen.query
            .filter(
                Kaizen.id == kaizen_id,

                Kaizen.is_active.is_(True),

                Kaizen.approved_at.isnot(None)
            )
            .first()
        )


        if not kaizen:

            return ServiceResult(
                success=False,
                message="Kaizen not found.",
                data=None
            )


        # -----------------------------------------------------
        # Validate Approval Date
        # -----------------------------------------------------

        start_datetime = datetime.combine(
            award_period.start_date,
            time.min
        )

        end_datetime = datetime.combine(
            award_period.end_date + timedelta(days=1),
            time.min
        )


        if (

            kaizen.approved_at < start_datetime

            or

            kaizen.approved_at >= end_datetime

        ):

            return ServiceResult(
                success=False,
                message="Kaizen is outside the selected award period.",
                data=None
            )


        # -----------------------------------------------------
        # Get Judges Scores
        # -----------------------------------------------------

        scores = (

            KaizenAwardScore.query

            .filter(

                KaizenAwardScore.award_period_id
                == award_period_id,

                KaizenAwardScore.kaizen_id
                == kaizen_id,

                KaizenAwardScore.is_active.is_(True),

                KaizenAwardScore.scored_at.isnot(None)

            )

            .order_by(

                KaizenAwardScore.score.desc()

            )

            .all()

        )


        # -----------------------------------------------------
        # Calculate Summary
        # -----------------------------------------------------

        judges_scored = len(
            scores
        )


        total_score = sum(

            float(score.score or 0)

            for score in scores

        )


        average_score = (

            total_score / judges_scored

            if judges_scored > 0

            else 0

        )


        # -----------------------------------------------------
        # Return
        # -----------------------------------------------------

        return ServiceResult(

            success=True,

            message="Kaizen award result detail retrieved successfully.",

            data={

                "award_period": award_period,

                "kaizen": kaizen,

                "scores": scores,

                "judges_scored": judges_scored,

                "total_score": total_score,

                "average_score": average_score

            }
        )


    # =========================================================
    # GET SCORE SUMMARY WITHOUT PAGINATION
    # =========================================================

    def get_all_results(
        self,
        award_period_id
    ):
        """
        Mengambil seluruh hasil score.
        Berguna untuk export/report jika diperlukan.
        """

        result = self.get_result(
            award_period_id=award_period_id,
            page=1,
            per_page=10000
        )


        if not result.success:

            return result


        return ServiceResult(

            success=True,

            message=result.message,

            data=result.data["results"]

        )