from celery import task
from orders.scrapers import correios
from orders import models
from util import mail, exceptions
import orders.scrapers.util.exceptions as request_exceptions


@task
def manage_deliveries():
    pending_orders = models.Correios.objects.filter(delivered=False)

    if not pending_orders:
        return
    
    results = {}

    for order in pending_orders.iterator():
        try:
            result, need_cpf = correios.delivery_info(code=order.code)
        except request_exceptions.InvalidTrackingCode:
            order.delete()

        results[order.code] = result
        # TODO: Handle CPF registration

    for track_number, infos in results.items():
        order = pending_orders.get(code=track_number)
        order.last_update = infos[-1]['Date']
        order.save()
        for info in infos:
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

            if info == infos[-1] and is_created:
                send_email.delay(
                    track_number=track_number,
                    order_name=order.name,
                    status=info['Info']['Status'],
                    description=info['Info']['Description']
                )


@task(autoretry_for=(exceptions.MailError,), retry_backoff=True)
def send_email(track_number:str, order_name:str, status:str, description:str):
    mail.send_message(
        subject=f'Your {order_name} delivery status has been updated!',
        template=(f'Gabriel, your order "{track_number} - {order_name}" status has ' + \
            f'been updated to "{status}"<br>Decription: {description}.')
    )
