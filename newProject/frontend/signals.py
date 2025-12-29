from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Booking

@receiver(post_save, sender=Booking)
def booking_email_sender(sender, instance, created, **kwargs):
    context = {
        'fname': instance.first_name,
        'lname': instance.last_name,
        'email': instance.email,
        'phone': instance.phone,
        'property_name': instance.property_name,
        'date': instance.date,
        'time': instance.time,
        'status': instance.status,
        'reason': instance.reason,
    }

    # New Booking
    if created:
        html_message = render_to_string('frontend/email_receive_tamplates.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=f'Booking Confirmation - {instance.property_name}',
            message=plain_message,
            from_email='no-reply@purplehousing.com',
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=False,
        )
    # Status update
    else:
        if instance.status == 'Approved':
            html_template = 'frontend/email_show_template.html'
            recipients = [instance.email]
            subject = f'Booking Approved - {instance.property_name}'
        elif instance.status == 'Disapproved':
            html_template = 'frontend/email_show_template.html'
            recipients = [instance.email, 'admin@purplehousing.com']
            subject = f'Booking Disapproved - {instance.property_name}'
        else:
            return

        html_message = render_to_string(html_template, context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email='no-reply@purplehousing.com',
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )
