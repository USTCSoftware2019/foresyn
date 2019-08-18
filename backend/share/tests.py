from django.test import TestCase

from .models import MetaboliteShare, ModelShare, ReactionShare, CobraMetabolite, CobraModel, CobraReaction


class CreateShareLinkTest(TestCase):
    fixtures = ['share/cobra_wrapper_data', 'share/user']

    def test_create_share_metabolite_link(self):
        c = self.client
        c.login(username='test', password='test123456')
        resp = c.post('/share/create', data={
            'type': 'metabolite',
            'id': 1,
            'public': True,
            'can_edit': False
        })

        self.assertEqual(resp.url, '/share/metabolite?id=1')

        shared_object = MetaboliteShare.objects.get(id=1)
        cobra_object = CobraMetabolite.objects.get(id=1)
        self.assertEqual(shared_object, cobra_object.metaboliteshare)

    def test_create_share_reaction_link(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'reaction',
            'id': 1,
            'public': True,
            'can_edit': False
        })

        self.assertEqual(resp.url, '/share/reaction?id=1')

        cobra_object = CobraReaction.objects.get(id=1)
        self.assertEqual(cobra_object.reactionshare.reaction.name, cobra_object.name)

        for shared_metabolite_object in cobra_object.reactionshare.metabolites.all():
            self.assertTrue(shared_metabolite_object.metabolite.name in [
                            o.name for o in cobra_object.metabolites.all()])

    def test_create_share_model_link(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': True,
            'can_edit': False
        })
        self.assertEqual(resp.url, '/share/model?id=1')

        cobra_object = CobraModel.objects.get(id=1)
        self.assertEqual(cobra_object.modelshare.model.name, cobra_object.name)

        for shared_model_object in cobra_object.modelshare.reactions.all():
            self.assertTrue(shared_model_object.reaction.name in [o.name for o in cobra_object.reactions.all()])
