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


class DetailViewTest(TestCase):
    fixtures = ['share/cobra_wrapper_data', 'share/user']

    def test_metabolite_detail(self):
        c = self.client
        c.login(username='test', password='test123456')
        resp = c.post('/share/create', data={
            'type': 'metabolite',
            'id': 1,
            'public': True,
            'can_edit': False
        })

        resp = c.get(resp.url)
        self.assertContains(resp, 'acyl-carrier-protein')
        self.assertContains(resp, 'C11H21N2O7PRS')

    def test_reaction_detail(self):
        c = self.client
        c.login(username='test', password='test123456')
        resp = c.post('/share/create', data={
            'type': 'reaction',
            'id': 1,
            'public': True,
            'can_edit': False
        })

        resp = c.get(resp.url)

        self.assertContains(resp, '3 oxoacyl acyl carrier protein synthase n C140')
        self.assertContains(resp, 'Cell Envelope Biosynthesis')
        self.assertContains(resp, '-1.0 -1.0 -1.0 1.0 1.0 1.0')
        self.assertContains(resp, '( STM2378 or STM1197 )')

        self.assertContains(resp, '/share/metabolite?=1')
        self.assertContains(resp, '/share/metabolite?=2')
        self.assertContains(resp, '/share/metabolite?=3')
        self.assertContains(resp, '/share/metabolite?=4')
        self.assertContains(resp, '/share/metabolite?=5')
        self.assertContains(resp, '/share/metabolite?=6')

    def test_model_detail(self):
        c = self.client
        c.login(username='test', password='test123456')
        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': True,
            'can_edit': False
        })

        resp = c.get(resp.url)

        self.assertContains(resp, 'test')
        self.assertContains(resp, '3OAS140')
        self.assertContains(resp, '/share/reaction?id=1')
