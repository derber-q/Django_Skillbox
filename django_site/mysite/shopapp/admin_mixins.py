
import  csv
from django.db.models import QuerySet
from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse


class ExportAsCSVMixin:
    def export_csv(self, request:HttpRequest, queryset: QuerySet):
        meta: Options = self.model._meta
        fild_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename = {meta}-export.csv'

        csv_writer = csv.writer(response)
        csv_writer.writerow(fild_names)

        for obj in queryset:
            [getattr(obj, field) for field in fild_names]

        return response
    export_csv.short_description = 'Export as CSV'