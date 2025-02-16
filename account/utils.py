from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template.loader import render_to_string

from account.models import CV
from io import BytesIO
from weasyprint import HTML


def generate_pdf_cv(cv_id: int) -> bool:
    cv_obj = CV.objects.get(pk=cv_id)


    context = {
        "full_name": cv_obj.user.first_name + " " + cv_obj.user.last_name,
        "work_experiences": cv_obj.work_experience.split("(*)"),
        "address": cv_obj.address.split("(*)"),
        "skills": cv_obj.skill_sets.split("(*)"),
        "languages": cv_obj.languages.split("(*)"),
    }

    html_string = render_to_string("pdf/cvpdf.html", context)

    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    pdf_file.seek(0)

    pdf_content =ContentFile(pdf_file.getvalue(), name=f"user_{cv_obj.user.username}_cv.pdf")

    try:
        user = get_user_model().objects.get(pk=cv_obj.user.id)
        user.cv_file.save(pdf_content.name, pdf_content, save=True)

        return True
    except get_user_model().DoesNotExist:
        return False







