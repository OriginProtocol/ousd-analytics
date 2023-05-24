from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.channels.html_stripper import strip_tags

class Email():
    def __init__(self, summary, details):
        self.summary = summary
        self.plain_text_details = strip_tags(details)
        self.details = details

    def _is_configured(self):
        return (
            settings.DEFAULT_FROM_EMAIL is not None
            and settings.REPLY_TO_EMAIL is not None
            and settings.EMAIL_HOST is not None
            and settings.EMAIL_HOST_USER is not None
            and settings.EMAIL_HOST_PASSWORD is not None
        )

    def execute(self, recipients):
        if recipients[0] is None: 
            print("No recipient")
            return
        if self._is_configured():
            from_email = settings.DEFAULT_FROM_EMAIL
            reply_email = settings.REPLY_TO_EMAIL.split(",")

            email = EmailMultiAlternatives(
                self.summary,
                self.plain_text_details,
                from_email,
                recipients,
                reply_to=reply_email
            )
            email.attach_alternative(self.details, "text/html")

            return email.send(fail_silently=False)

            # msg = EmailMessage(
            #   from_email=settings.DEFAULT_FROM_EMAIL,
            #   to=['grabec@gmail.com'],
            # )
            # msg.template_id = "analytics_report_v2_email.html"
            # msg.dynamic_template_data = {
            #   "title": "title"
            # }
            # return msg.send(fail_silently=False)

            # return send_mail(
            #     self.summary,
            #     #self.plain_text_details,
            #     #settings.DEFAULT_FROM_EMAIL,
            #     "lalal@gmail.com",
            #     ['grabec@gmail.com'],
            #     fail_silently=False,
            #     #html_message=self.details
            # )

        else:
            # If we're not configured, don't die, but don't be silent
            print('E-mail not configured', settings.DEFAULT_FROM_EMAIL)