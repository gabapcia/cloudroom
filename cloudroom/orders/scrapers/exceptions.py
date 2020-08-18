class OrderNotShipped(Exception):
    def __str__(self):
        return 'Order not shipped yet'

class InvalidTrackingCode(Exception):
    def __str__(self):
        return 'Invalid tracking code'

class OrderNotFound(Exception):
    def __str__(self):
        return 'Order not found on "Minhas Importações"'

class DocumentAlreadyRegistered(Exception):
    def __str__(self):
        return 'Document already registered for this order'
