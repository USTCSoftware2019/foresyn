from django.shortcuts import render, redirect, reverse
from django.views.generic import View, DetailView
from share.models import ModelShare, ReactionShare, MetaboliteShare, CobraModel, CobraReaction, CobraMetabolite
from django.core.exceptions import ObjectDoesNotExist


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

    def create_link_for_metabolite(self, metabolite_id):
        cobra_metabolite = CobraMetabolite.objects.get(id=metabolite_id)
        try:
            return cobra_metabolite.metaboliteshare
        except CobraMetabolite.metaboliteshare.RelatedObjectDoesNotExist:
            return MetaboliteShare.objects.create(metabolite=cobra_metabolite,
                                                  public=self.public,
                                                  can_edit=self.can_edit,
                                                  owner=self.owner)

    def recursive_create_link_for_reaction(self, reaction_id):
        cobra_reaction = CobraReaction.objects.get(id=reaction_id)
        try:
            return cobra_reaction.reactionshare
        except CobraReaction.reactionshare.RelatedObjectDoesNotExist:
            shared_reaction_object = ReactionShare(reaction=cobra_reaction,
                                                   public=self.public,
                                                   can_edit=self.can_edit,
                                                   owner=self.owner)
            shared_reaction_object.save()
            for metabolite in cobra_reaction.metabolites.all():
                shared_reaction_object.metabolites.add(self.create_link_for_metabolite(metabolite.id))
            shared_reaction_object.save()
            return shared_reaction_object

    def recursive_create_link_for_model(self, model_id):
        cobra_model = CobraModel.objects.get(id=model_id)
        try:
            return cobra_model.modelshare
        except CobraModel.modelshare.RelatedObjectDoesNotExist:
            shared_model_object = ModelShare(model=cobra_model,
                                             public=self.public,
                                             can_edit=self.can_edit,
                                             owner=self.owner)
            shared_model_object.save()
            for reaction in cobra_model.reactions.all():
                shared_model_object.reactions.add(self.recursive_create_link_for_reaction(reaction.id))
            shared_model_object.save()
            return shared_model_object

    def post(self, request, *args, **kwargs):
        share_type = request.POST['type']
        self.public = request.POST.get('public')
        self.owner = request.user
        self.can_edit = request.POST.get('can_edit')

        if share_type == 'model':
            shared_object = self.recursive_create_link_for_model(request.POST['id'])
        elif share_type == 'reaction':
            shared_object = self.recursive_create_link_for_reaction(request.POST['id'])
        elif share_type == 'metabolite':
            shared_object = self.create_link_for_metabolite(request.POST['id'])
        else:
            # TODO
            # return an error page
            raise TypeError('The share_type must be one of model, reaction or metabolite')

        return redirect(reverse('share:shared_cobra_{}'.format(share_type)) + '?id={}'.format(shared_object.id))


class CustomDetailView(DetailView):
    def get_object(self, queryset=None):
        requested_id = self.request.GET['id']
        return self.model.objects.get(id=requested_id)


class ModelShareView(CustomDetailView):
    model = ModelShare


class MetaboliteShareView(CustomDetailView):
    model = MetaboliteShare


class ReactionShareView(CustomDetailView):
    model = ReactionShare
