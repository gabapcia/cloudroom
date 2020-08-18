from celery import task
from cloudroom.utils import mail, exceptions
from . import models
from .scrapers import correios
from .scrapers import exceptions as tracking_exceptions


@task
def manage_deliveries():
    pending_orders = models.Correios.objects.filter(delivered=False)

    if not pending_orders: return
    
    for order in pending_orders.iterator():
        try:
            result, need_cpf = correios.delivery_info(code=order.code)
        except tracking_exceptions.InvalidTrackingCode:
            order.delete()
            continue
        except tracking_exceptions.OrderNotShipped:
            continue

        if need_cpf and not order.cpf_registered:
            try:
                correios.register_cpf(order.code)
                order.cpf_registered = True
                order.save()
            except tracking_exceptions.DocumentAlreadyRegistered:
                order.cpf_registered = True
                order.save()
            except tracking_exceptions.OrderNotFound:
                pass

        order.last_update = result[-1]['Date']
        order.save()
        for info in result:
            _, is_created = models.CorreiosInfo.objects.get_or_create(
                order=order,
                date=info['Date'],
                place=info['Place'],
                status=info['Info']['Status'],
                info=info['Info']['Description']
            )

            if 'Objeto entregue ao destinatário' in info['Info']['Status']:
                order.delivered = True
                order.save()

            if info == result[-1] and is_created:
                send_email.delay(
                    track_number=order.code,
                    order_name=order.name,
                    status=info['Info']['Status'],
                    description=info['Info']['Description']
                )

@task(
    autoretry_for=(exceptions.MailError,), 
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=5
)
def send_email(track_number, order_name, status, description):
    template = (
        'Hello, Gabriel.\n'
        f'Your order "{track_number} - {order_name}" '
        f'status has been updated to "{status}"\n'
        f'Description: {description}.'
    )

    mail.send_message(
        subject=f'"{order_name}" delivery status has been updated!',
        template=template
    )
