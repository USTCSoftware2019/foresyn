from django.test import TestCase
from django.urls import reverse

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
        }, content_type='application/json')

        self.assertEqual(resp.url, '/share/metabolite/1')

        shared_object = MetaboliteShare.objects.get(id=1)
        cobra_object = CobraMetabolite.objects.get(id=1)
        self.assertEqual(shared_object, cobra_object.metaboliteshare_set.first())

    def test_create_share_reaction_link(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'reaction',
            'id': 1,
            'public': True,
            'can_edit': False
        }, content_type='application/json')

        self.assertEqual(resp.url, '/share/reaction/1')

        cobra_object = CobraReaction.objects.get(id=1)

        shared_object = ReactionShare.objects.get(id=1)
        self.assertEqual(shared_object.reaction.name, cobra_object.name)

        for shared_metabolite_object in shared_object.metabolites.all():
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
        }, content_type='application/json')
        self.assertEqual(resp.url, '/share/model/1')

        cobra_object = CobraModel.objects.get(id=1)
        modelshare = cobra_object.modelshare_set.first()
        self.assertEqual(modelshare.model.name, cobra_object.name)

        for shared_model_object in modelshare.reactions.all():
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
        }, content_type='application/json')

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
        }, content_type='application/json')

        resp = c.get(resp.url)

        self.assertContains(resp, '3 oxoacyl acyl carrier protein synthase n C140')
        self.assertContains(resp, 'Cell Envelope Biosynthesis')
        self.assertContains(resp, '-1.0 -1.0 -1.0 1.0 1.0 1.0')
        self.assertContains(resp, '( STM2378 or STM1197 )')

        self.assertContains(resp, '/share/metabolite/1')
        self.assertContains(resp, '/share/metabolite/2')
        self.assertContains(resp, '/share/metabolite/3')
        self.assertContains(resp, '/share/metabolite/4')
        self.assertContains(resp, '/share/metabolite/5')
        self.assertContains(resp, '/share/metabolite/6')

    def test_model_detail(self):
        c = self.client
        c.login(username='test', password='test123456')
        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': True,
            'can_edit': False
        }, content_type='application/json')

        resp = c.get(resp.url)

        self.assertContains(resp, 'test')
        self.assertContains(resp, '3OAS140')
        self.assertContains(resp, '/share/reaction/1')

    def test_password_required(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': False,
            'password': '123456',
            'can_edit': False,
        }, content_type='application/json')

        c.logout()

        url = resp.url
        resp = c.get(url)
        self.assertTemplateUsed(resp, 'share/password_confirm.html')

        resp = c.post(url, data={
            'password': '123456',
        })
        self.assertEqual(resp.url, url)

        resp = c.get(url)
        self.assertTemplateUsed(resp, 'share/modelshare_detail.html')

    def test_unusable_password(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': False,
            'can_edit': False,
        }, content_type='application/json')

        c.logout()

        url = resp.url
        resp = c.get(url)

        resp = c.post(url, data={})

        resp = c.get(url)
        self.assertTemplateNotUsed(resp, 'share/modelshare_detail.html')

    def test_access_child_reaction_without_password(self):
        c = self.client
        c.login(username='test', password='test123456')

        resp = c.post('/share/create', data={
            'type': 'model',
            'id': 1,
            'public': False,
            'password': '123456',
            'can_edit': False,
        }, content_type='application/json')

        c.logout()

        url = resp.url
        resp = c.get(url)
        resp = c.post(url, data={
            'password': '123456',
        })

        resp = c.get('/share/reaction/1')
        self.assertTemplateUsed(resp, 'share/reactionshare_detail.html')
