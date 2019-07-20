import json

from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from .models import CobraModel, CobraReaction, CobraMetabolite


def get_required_params(params, required_params):
    return {param: params[param] for param in required_params}


class CobraModelApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            reactions = [
                CobraReaction.objects.get(id=reaction_id)
                for reaction_id in params['reactions']
            ]
            model = CobraModel(**get_required_params(params, [
                'identifier', 'objective'
            ]))
            model.full_clean()
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200021,
                'message': error.messages
            }, status=400)
        except AttributeError as error:
            return JsonResponse({
                'code': 200011,
                'message': error.args
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages
            }, status=400)
        model.save()
        model.reactions.set(reactions)
        model.save()
        return JsonResponse({'id': model.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        dreaction_base = request.POST['dreaction_base']
        try:
            dreaction = CobraReaction.get(base=dreaction_base)
            dreaction.delete()
            return JsonResponse({'code': 200, 'message': 'success'})
            # HTTP 状态码不要放到 body 里，应当这样
        except:
            # Do not use bare 'except' 用 except 时一定要明确指出想要
            # except 的 exception
            return JsonResponse({'code': 403, 'message': "can't find CobraReaction"})

    def patch(self, request):
        params = json.loads(request.body)
        try:
            model = CobraModel.objects.get(id=params['id'])
            if 'reactions' in params.keys():
                reactions = [
                    CobraReaction.objects.get(id=reaction_id)
                    for reaction_id in params['reactions']
                ]
                model.reactions.set(reactions)
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200021,
                'message': error.messages
            }, status=400)
        for field in [
            'identifier', 'objective'
        ]:
            if field in params.keys():
                setattr(model, field, params[field])
        try:
            model.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages
            }, status=400)
        model.save()
        return JsonResponse({'id': model.id}, status=200)


class CobraReactionApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolites = [
                CobraMetabolite.objects.get(id=metabolite_id)
                for metabolite_id in params['metabolites']
            ]
            reaction = CobraReaction(**get_required_params(params, [
                'identifier', 'name', 'subsystem', 'lower_bound',
                'upper_bound', 'gene_reaction_rule'
            ]))
            reaction.coefficients = ' '.join(
                map(lambda num: str(num), params['coefficients']))
            reaction.full_clean()
        except AttributeError as error:
            return JsonResponse({
                'code': 200022,
                'message': error.args
            }, status=400)
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200012,
                'message': error.messages
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200002,
                'message': error.messages
            }, status=400)
        reaction.save()
        reaction.metabolites.set(metabolites)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        dmetabolite_base = request.POST['dmetabolite_base']
        try:
            dmetabolite = CobraMetabolite.get(base=dmetabolite_base)
            dmetabolite.delete()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'code': 403, 'message': "can't find CobraMetabolite"})

    def patch(self, request):
        params = json.loads(request.body)
        try:
            reaction = CobraReaction.objects.get(id=params['id'])
            if 'metabolites' in params.keys():
                metabolites = [
                    CobraMetabolite.objects.get(id=metabolite_id)
                    for metabolite_id in params['metabolites']
                ]
                reaction.metabolites.set(metabolites)
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200021,
                'message': error.messages
            }, status=400)
        for field in [
            'identifier', 'name', 'subsystem', 'lower_bound', 'upper_bound',
            'gene_reaction_rule'
        ]:
            if field in params.keys():
                setattr(reaction, field, params[field])
        if 'coefficients' in params.keys():
            reaction.coefficients = ' '.join(
                map(lambda num: str(num), params['coefficients']))
        try:
            reaction.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages
            }, status=400)
        reaction.save()
        return JsonResponse({'id': reaction.id}, status=200)


class CobraMetaboliteApi(View):
    def post(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite(**get_required_params(params, [
                'identifier', 'formula', 'name', 'compartment'
            ]))
            metabolite.full_clean()
        except AttributeError as error:
            return JsonResponse({
                'code': 200013,
                'message': error.args
            }, status=400)
        except ValidationError as error:
            return JsonResponse({
                'code': 200003,
                'message': error.messages
            }, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=201)

    def get(self, request):
        pass

    def delete(self, request):
        dmodel_base = request.POST['dmodel_base']
        try:
            dmodel = CobraModel.get(base=dmodel_base)
            dmodel.delete()
            return JsonResponse({'code': 200, 'status': 'success'})
        except:
            return JsonResponse({'code': 403, 'message': "can't find CobraModel"})

    def patch(self, request):
        params = json.loads(request.body)
        try:
            metabolite = CobraMetabolite.objects.get(id=params['id'])
        except ObjectDoesNotExist as error:
            return JsonResponse({
                'code': 200021,
                'message': error.messages
            }, status=400)
        for field in [
            'identifier', 'formula', 'name', 'compartment'
        ]:
            if field in params.keys():
                setattr(metabolite, field, params[field])
        try:
            metabolite.full_clean()
        except ValidationError as error:
            return JsonResponse({
                'code': 200001,
                'message': error.messages
            }, status=400)
        metabolite.save()
        return JsonResponse({'id': metabolite.id}, status=200)
