from import_export import resources
from victory.models import Route
 
class EmployeeResource(resources.ModelResource):
    class Meta:
        model = Route