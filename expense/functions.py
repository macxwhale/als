import os
from django.utils import timezone
import datetime

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def upload_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s_%s_%s.%s" % (timezone.now(), instance.station.name, instance.created_by, ext)
    return os.path.join('uploads/receipts/', filename)




            
