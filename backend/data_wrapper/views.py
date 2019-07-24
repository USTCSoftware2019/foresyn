from django.views import View

from cobra_wrapper.models import CobraModel
from bigg_database.models import Model as DataModel
from django.http import JsonResponse


class AddDataModelToCobra(View):
    def post(self, request, database_pk):
        datamodel_object = DataModel.objects.get(pk=database_pk)
        cobramodel_object = CobraModel()
        # relationship
        cobramodel_object.identifier = datamodel_object.bigg_id
        cobramodel_object.name = datamodel_object.bigg_id

        datamodel_reactions = datamodel_object.reaction_set
        for i in datamodel_reactions.all():
            # waiting for test data...
            # TBD
            pass

        return JsonResponse("test")
