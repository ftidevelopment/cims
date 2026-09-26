from flask import Blueprint, render_template,request,redirect,flash,url_for
from flask_login import login_required
from app.services.problem_category_service import ProblemCategoryService
from io import BytesIO
from flask import send_file

problem_category_bp = Blueprint(
    "problem_category",
    __name__,
    url_prefix="/problem_categories",
)

service = ProblemCategoryService()


@problem_category_bp.route("/")
@login_required
def index():

    keyword = request.args.get("keyword", "").strip()

    page = request.args.get("page", 1, type=int)

    sort_by = request.args.get(
        "sort",
        "problem_category_code"
    )

    sort_order = request.args.get(
        "order",
        "asc"
    )

    is_active_param = request.args.get(
        "is_active",
        "true"
    ).lower()

    if is_active_param == "true":
        is_active = True
    elif is_active_param == "false":
        is_active = False
    else:
        is_active = None

    problem_categories = service.get_all(
        keyword=keyword,
        is_active=is_active,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "problem_category/list.html",
        problem_categories=problem_categories,
        keyword=keyword,
        is_active=is_active_param,       
        sort_by=sort_by,
        sort_order=sort_order
        
    )

@problem_category_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():

    if request.method == "GET":

        return render_template(
            "problem_category/form.html",
            problem_category=None,
        )

    problem_category_code = request.form.get(
        "problem_category_code"
    ).strip()

    problem_category_name = request.form.get(
        "problem_category_name"
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.create(
            problem_category_code=problem_category_code,
            problem_category_name=problem_category_name,
            description=description,
        )

        flash(
            "Problem Category created successfully.",
            "success"
        )

        return redirect(
            url_for("problem_category.index")
        )

    except ValueError as e:

        flash(str(e), "danger")

        return render_template(
            "problem_category/form.html",
            problem_category=None,
        )

    except Exception:

        flash(
            "Failed to create problem_category.",
            "danger"
        )

        return render_template(
            "problem_category/form.html",
            problem_category=None,
        )


@problem_category_bp.route("/edit/<int:problem_category_id>", methods=["GET", "POST"])
@login_required
def edit(problem_category_id):

    problem_category = service.get_by_id(problem_category_id)

    if not problem_category:

        flash(
            "Problem Category not found.",
            "danger"
        )

        return redirect(
            url_for("problem_category.index")
        )

    if request.method == "GET":

        return render_template(
            "problem_category/form.html",
            problem_category=problem_category,
        )

    problem_category_name = request.form.get(
        "problem_category_name"
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.update(
            problem_category=problem_category,
            problem_category_name=problem_category_name,
            description=description,
        )

        flash(
            "Problem Category updated successfully.",
            "success"
        )

        return redirect(
            url_for("problem_category.index")
        )

    except Exception:

        flash(
            "Failed to update Problem Category.",
            "danger"
        )

        return render_template(
            "problem_category/form.html",
            problem_category=problem_category,
        )


@problem_category_bp.route("/delete/<int:problem_category_id>", methods=["POST"])
@login_required
def delete(problem_category_id):

    problem_category = service.get_by_id(problem_category_id)

    if problem_category is None:

        flash(
            "Problem Category not found.",
            "danger",
        )

        return redirect(
            url_for("problem_category.index")
        )

    try:

        service.delete(problem_category)

        flash(
            "Problem Category deleted successfully.",
            "success",
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger",
        )

    except Exception as ex:

        flash(
            f"Failed to delete problem_category. {ex}",
            "danger",
        )

    return redirect(
        url_for("problem_category.index")
    )


@problem_category_bp.route("/export")
@login_required
def export():

    keyword = request.args.get("keyword", "").strip()

    sort_by = request.args.get(
        "sort",
        "problem_category_code"
    )

    sort_order = request.args.get(
        "order",
        "asc"
    )

    is_active_param = request.args.get(
        "is_active",
        "true"
    ).lower()

    if is_active_param == "true":
        is_active = True
    elif is_active_param == "false":
        is_active = False
    else:
        is_active = None

    workbook = service.export_excel(
        keyword=keyword,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Problem_Category.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@problem_category_bp.route(
    "/restore/<int:problem_category_id>",
    methods=["POST"]
)
@login_required
def restore(problem_category_id):

    result = service.restore(problem_category_id)

    flash(
        result.message,
        "success" if result.success else "danger"
    )

    return redirect(url_for("problem_category.index"))