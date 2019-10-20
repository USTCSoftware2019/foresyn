from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import cobra.test

from .models import CobraModel, CobraFba
from .utils import dump_sbml

from backend.celery import app


class CobraWrapperViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123456')
        self.model = CobraModel.objects.create(name='example',
                                               sbml_content=dump_sbml(cobra.test.create_test_model()), owner=self.user)
        self.client.login(username='test', password='test123456')

    def test_models_list(self):
        response = self.client.get('/cobra/models/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_list.html')
        self.assertContains(response, self.model.name)
        self.assertContains(response, '/cobra/models/1/')

    def test_models_detail(self):
        response = self.client.get('/cobra/models/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_detail.html')
        self.assertContains(response, self.model.name)
        self.assertContains(response, '/cobra/models/1/delete/')
        self.assertContains(response, '/cobra/models/1/fba/')
        self.assertContains(response, '/cobra/models/1/fva/')

        response = self.client.get('/cobra/reactions/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_models_create(self):
        self.client.post('/cobra/models/create/', dict(
            cobra_id='test',
            name='test',
            objective='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/models/create/', dict(
            cobra_id='test',
            name='test',
            objective='test'))
        self.assertTemplateUsed('cobra_wrapper/cobramodel_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_list.html')
        self.assertRedirects(response, '/cobra/models/2/')

        response = self.client.get('/cobra/models/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/models/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'reactions', 'objective']:
            self.assertContains(response, comp)

        # test for change
        response = self.client.get('/cobra/models/2/')
        self.assertContains(response, 'the instance is created at')

    def test_models_update(self):
        response = self.client.post('/cobra/models/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/models/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/models/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test'))
        self.assertTemplateUsed('cobra_wrapper/cobramodel_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_detail.html')
        self.assertRedirects(response, '/cobra/models/1/')

        # test for change
        response = self.client.get('/cobra/models/1/')
        changed_data = 'cobra_id, reactions, objective'
        changed_data += ' is changed from example_model, co... to test'
        self.assertContains(response, changed_data)

        self.client.post('/cobra/models/1/update/', dict(
            cobra_id='test',
            name='test1',
            objective='test'))

        response = self.client.get('/cobra/models/1/')
        self.assertContains(response, 'name is changed from test to test1 at')

        response = self.client.get('/cobra/models/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'reactions', 'objective']:
            self.assertContains(response, comp)

    def test_models_delete(self):
        response = self.client.post('/cobra/models/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/models/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_confirm_delete.html')
        self.assertContains(response, '<p>Are you sure to delete: example_model[test]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)

        response = self.client.post('/cobra/models/1/delete/')
        self.assertRedirects(response, '/cobra/models/')

    def test_fba(self):
        # test for create
        response = self.client.get('/cobra/models/1/fba/create/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafba_create_form.html')
        for comp in ['desc']:
            self.assertContains(response, comp)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/">Return</a>', html=True)

        # real create
        self.client.post('/cobra/models/1/fba/create/', dict(
            desc='test'
        ))  # Create a fba from frontend

        model_object = CobraModel.objects.get(pk=1)
        fba = CobraFba.objects.create(desc='test', model=model_object)
        fba.save()
        cobra_model = model_object.build()
        result = app.send_task(
            'cobra_computation.tasks.cobra_fba',
            args=[fba.pk, cobra.io.to_json(cobra_model)],
            kwargs={},
            queue='cobra_feeds',
            routing_key='cobra_feed.fba'
        )
        fba.task_id = result.id
        fba.save()  # Create a fba from backend

        # test for list
        response = self.client.get('/cobra/models/1/fba/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafba_list.html')
        for comp in ['desc', 'start_time', 'status']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/fba/1/">Detail</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/create/">Create</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)

        # test for detail
        response = self.client.get('/cobra/models/1/fba/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafba_detail.html')
        for comp in ['id', 'description', 'start_time', 'model', 'Status']:
            self.assertContains(response, comp)
        for comp in ['1', 'test']:
            self.assertContains(response, comp)
        if b'OK' in response.content:
            for comp in ['objective_value', 'status', 'fluxes', 'shadow_price']:
                self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/fba/">Return</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/1/delete/">Delete</a>', html=True)

        # test for delete
        response = self.client.post('/cobra/models/1/fba/7777777/delete/')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/cobra/models/7777777/fba/1/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/models/1/fba/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrafba_confirm_delete.html')
        self.assertTemplateUsed('cobra_wrapper/cobrafba_list.html')
        self.assertContains(response, '<p>Are you sure to delete: test[fba]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/1/">Return</a>', html=True)

        response = self.client.post('/cobra/models/1/fba/1/delete/')
        self.assertRedirects(response, '/cobra/models/1/fba/')

    def test_fva(self):
        # test for create
        response = self.client.get('/cobra/models/1/fva/create/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafva_create_form.html')
        for comp in ['desc', 'reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor']:
            self.assertContains(response, comp)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/">Return</a>', html=True)
        # reaction_object = CobraReaction.objects.get(pk=1)
        #
        # # real create
        # self.client.post('/cobra/models/1/fva/create/', dict(
        #     desc='test',
        #     reaction_list=[reaction_object.pk],
        #     loopless='',
        #     fraction_of_optimum='1.0',
        #     pfba_factor='unknown'
        # ))  # Create a fva from frontend

        model_object = CobraModel.objects.get(pk=1)
        fva = CobraFba.objects.create(desc='test', model=model_object)
        fva.save()
        cobra_fva_kwargs = {
            # 'reaction_list': [reaction_object.cobra_id],
            'loopless': False,
            'fraction_of_optimum': 1.0,
            'pfba_factor': None
        }
        cobra_model = model_object.build()
        result = app.send_task(
            'cobra_computation.tasks.cobra_fva',
            args=[fva.pk, cobra.io.to_json(cobra_model)],
            kwargs=cobra_fva_kwargs,
            queue='cobra_feeds',
            routing_key='cobra_feed.fva'
        )
        fva.task_id = result.id
        fva.save()  # Create a fva from backend

        # test for list
        response = self.client.get('/cobra/models/1/fva/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafva_list.html')
        for comp in ['desc', 'start_time', 'status']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/fva/1/">Detail</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/create/">Create</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)

        # test for detail
        response = self.client.get('/cobra/models/1/fva/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrafva_detail.html')
        for comp in ['id', 'description', 'start_time', 'model', 'Status']:
            self.assertContains(response, comp)
        for comp in ['1', 'test']:
            self.assertContains(response, comp)
        for comp in ['reaction_list', 'loopless', 'fraction_of_optimum', 'pfba_factor']:
            self.assertContains(response, comp)
        for comp in ['3OAS140[3 oxoacyl acyl carrier protein synthase n C140]', 'False', '1.0', 'None']:
            self.assertContains(response, comp)
        if b'OK' in response.content:
            for comp in ['name', 'maximum', 'minimum']:
                self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/fva/">Return</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/1/delete/">Delete</a>', html=True)

        # test for delete
        response = self.client.post('/cobra/models/1/fva/7777777/delete/')
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/cobra/models/7777777/fva/1/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/models/1/fva/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrafva_confirm_delete.html')
        self.assertContains(response, '<p>Are you sure to delete: test[fva]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/1/">Return</a>')

        response = self.client.post('/cobra/models/1/fva/1/delete/')
        self.assertRedirects(response, '/cobra/models/1/fva/')
