import json

from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView, FormView, View

from share.models import (CobraMetabolite, CobraModel, CobraReaction,
                          MetaboliteShare, ModelShare, ReactionShare,
                          ShareAuthorization)

from .forms import PasswordConfirmForm

from .common import OneTimeShareLinkManager


class CreateShareLinkView(View):
    http_method_names = ['post']

    share_type_map = {
        'model': ModelShare,
        'reaction': ReactionShare,
        'metabolite': MetaboliteShare
    }
    cobra_type_map = {
        'model': CobraModel,
        'reaction': CobraReaction,
        'metabolite': CobraMetabolite
    }

    def create_share_auth(self):
        auth = ShareAuthorization.objects.create(public=self.public)
        if not self.public:
            # if password is None, it will be an unusable password
            auth.set_password(self.password)
            auth.save()
        return auth

    def create_link_for_metabolite(self, metabolite_id, auth=None):
        cobra_metabolite = CobraMetabolite.objects.get(id=metabolite_id)

        if auth is None:
            auth = self.create_share_auth()

        return MetaboliteShare.objects.create(metabolite=cobra_metabolite,
                                              can_edit=self.can_edit,
                                              owner=self.owner,
                                              auth=auth)

    def recursive_create_link_for_reaction(self, reaction_id, auth=None):
        cobra_reaction = CobraReaction.objects.get(id=reaction_id)

        if auth is None:
            auth = self.create_share_auth()

        shared_reaction_object = ReactionShare.objects.create(reaction=cobra_reaction,
                                                              can_edit=self.can_edit,
                                                              owner=self.owner,
                                                              auth=auth)
        for metabolite in cobra_reaction.metabolites.all():
            shared_reaction_object.metabolites.add(self.create_link_for_metabolite(metabolite.id, auth))
        shared_reaction_object.save()
        return shared_reaction_object

    def recursive_create_link_for_model(self, model_id, auth=None):
        cobra_model = CobraModel.objects.get(id=model_id)

        if auth is None:
            auth = self.create_share_auth()

        shared_model_object = ModelShare.objects.create(model=cobra_model,
                                                        can_edit=self.can_edit,
                                                        owner=self.owner,
                                                        auth=auth)
        for reaction in cobra_model.reactions.all():
            shared_model_object.reactions.add(self.recursive_create_link_for_reaction(reaction.id, auth))
        shared_model_object.save()
        return shared_model_object

    def post(self, request, *args, **kwargs):
        request_dict = json.loads(request.body)

        try:
            share_type = request_dict['type']
            self.public = request_dict['public']
            self.can_edit = request_dict['can_edit']
            object_id = request_dict['id']
        except KeyError:
            return JsonResponse({
                'err': 1,
                'msg': 'Field public, can_edit and id is required'
            })

        self.owner = request.user
        self.password = request_dict.get('password')

        if share_type == 'model':
            shared_object = self.recursive_create_link_for_model(object_id)
        elif share_type == 'reaction':
            shared_object = self.recursive_create_link_for_reaction(object_id)
        elif share_type == 'metabolite':
            shared_object = self.create_link_for_metabolite(object_id)
        else:
            return JsonResponse({
                'err': 2,
                'msg': 'The share_type must be one of model, reaction or metabolite'
            })

        return JsonResponse({
            'err': 0,
            'link': reverse('share:shared_cobra_{}'.format(share_type), args=(shared_object.id,))
        })


class PasswordRequiredDetailView(DetailView):
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        authorized = request.session.setdefault('authorized', [])

        self.object = self.get_object()
        auth = self.object.auth

        if auth is None or auth.public or auth.id in authorized:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

        share_type = 'model' if hasattr(self, 'model') else ('reaction' if hasattr(self, 'reaction') else 'metabolite')
        if OneTimeShareLinkManager.check_key(request.GET.get('key'), share_type, kwargs['pk']):
            self.request.session['authorized'].append(auth.id)
            self.request.session.save()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

        return PasswordConfirmView.as_view()(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        authorized = request.session.setdefault('authorized', [])

        self.object = self.get_object()
        auth = self.object.auth

        if auth is None or auth.public or auth.id in authorized:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

        share_type = 'model' if hasattr(self, 'model') else ('reaction' if hasattr(self, 'reaction') else 'metabolite')
        if OneTimeShareLinkManager.check_key(request.GET.get('key'), share_type, kwargs['pk']):
            self.request.session['authorized'].append(auth.id)
            self.request.session.save()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

        kwargs['expect_password'] = auth.password
        kwargs['auth_id'] = auth.id

        return PasswordConfirmView.as_view()(request, *args, **kwargs)


class ModelShareView(PasswordRequiredDetailView):
    model = ModelShare


class MetaboliteShareView(PasswordRequiredDetailView):
    model = MetaboliteShare


class ReactionShareView(PasswordRequiredDetailView):
    model = ReactionShare


class PasswordConfirmView(FormView):
    form_class = PasswordConfirmForm
    template_name = 'share/password_confirm.html'

    def get_success_url(self):
        return self.request.get_full_path()

    def form_valid(self, form):
        raw_password = form.cleaned_data['password']
        if check_password(raw_password, self.kwargs['expect_password']):
            self.request.session['authorized'].append(self.kwargs['auth_id'])
            self.request.session.save()

        return super().form_valid(form)
