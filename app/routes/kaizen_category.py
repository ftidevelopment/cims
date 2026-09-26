from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required
from app.services.kaizen_category_service import KaizenCategoryService
from io import BytesIO
from flask import send_file


kaizen_category_bp = Blueprint(
    "kaizen_category",
    __name__,
    url_prefix="/kaizen_categories",
)

service = KaizenCategoryService()


@kaizen_category_bp.route("/")
@login_required
def index():

    keyword = request.args.get("keyword", "").strip()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    sort_by = request.args.get(
        "sort",
        "kaizen_category_code"
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

    kaizen_categories = service.get_all(
        keyword=keyword,
        is_active=is_active,
        page=page,
        per_page=10,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return render_template(
        "kaizen_category/list.html",
        kaizen_categories=kaizen_categories,
        keyword=keyword,
        is_active=is_active_param,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@kaizen_category_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    if request.method == "GET":

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=None,
        )

    kaizen_category_code = request.form.get(
        "kaizen_category_code",
        ""
    ).strip()

    kaizen_category_name = request.form.get(
        "kaizen_category_name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.create(
            kaizen_category_code=kaizen_category_code,
            kaizen_category_name=kaizen_category_name,
            description=description,
        )

        flash(
            "Kaizen Category created successfully.",
            "success"
        )

        return redirect(
            url_for("kaizen_category.index")
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=None,
        )

    except Exception:

        flash(
            "Failed to create Kaizen Category.",
            "danger"
        )

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=None,
        )


@kaizen_category_bp.route(
    "/edit/<int:kaizen_category_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(kaizen_category_id):

    kaizen_category = service.get_by_id(
        kaizen_category_id
    )

    if not kaizen_category:

        flash(
            "Kaizen Category not found.",
            "danger"
        )

        return redirect(
            url_for("kaizen_category.index")
        )

    if request.method == "GET":

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=kaizen_category,
        )

    kaizen_category_name = request.form.get(
        "kaizen_category_name",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    try:

        service.update(
            kaizen_category=kaizen_category,
            kaizen_category_name=kaizen_category_name,
            description=description,
        )

        flash(
            "Kaizen Category updated successfully.",
            "success"
        )

        return redirect(
            url_for("kaizen_category.index")
        )

    except ValueError as e:

        flash(
            str(e),
            "danger"
        )

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=kaizen_category,
        )

    except Exception:

        flash(
            "Failed to update Kaizen Category.",
            "danger"
        )

        return render_template(
            "kaizen_category/form.html",
            kaizen_category=kaizen_category,
        )


@kaizen_category_bp.route(
    "/delete/<int:kaizen_category_id>",
    methods=["POST"]
)
@login_required
def delete(kaizen_category_id):

    kaizen_category = service.get_by_id(
        kaizen_category_id
    )

    if kaizen_category is None:

        flash(
            "Kaizen Category not found.",
            "danger",
        )

        return redirect(
            url_for("kaizen_category.index")
        )

    try:

        service.delete(
            kaizen_category
        )

        flash(
            "Kaizen Category deleted successfully.",
            "success",
        )

    except ValueError as ex:

        flash(
            str(ex),
            "danger",
        )

    except Exception as ex:

        flash(
            f"Failed to delete Kaizen Category. {ex}",
            "danger",
        )

    return redirect(
        url_for("kaizen_category.index")
    )


@kaizen_category_bp.route("/export")
@login_required
def export():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    sort_by = request.args.get(
        "sort",
        "kaizen_category_code"
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
        download_name="Kaizen_Category.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


@kaizen_category_bp.route(
    "/restore/<int:kaizen_category_id>",
    methods=["POST"]
)
@login_required
def restore(kaizen_category_id):

    result = service.restore(
        kaizen_category_id
    )

    flash(
        result.message,
        "success" if result.success else "danger"
    )

    return redirect(
        url_for("kaizen_category.index")
    )