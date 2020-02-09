from celery import task
from orders.scrapers import correios
from orders import models


@task
def manage_deliveries():
    pending_orders = models.Correios.objects.filter(delivered=False)
    
    if not pending_orders:
        return
    
    results = {}

    for order in pending_orders.iterator():
        result, need_cpf = correios.delivery_info(code=order.code)
        results[order.code] = result
        # TODO: Handle CPF registration

    for track_number, infos in results.items():
        order = pending_orders.get(code=track_number)
        order.last_update = infos[-1]['Date']
        order.save()
        for info in infos:
            models.CorreiosInfo.objects.get_or_create(
                order=order,
                date=info['Date'],
                place=info['Place'],
                status=info['Info']['Status'],
                info=info['Info']['Description']
            )
            if 'Objeto entregue ao destinatário' in info['Info']['Status']:
                order.delivered = True
                order.save()
