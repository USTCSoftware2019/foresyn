from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import cobra

from .models import CobraModel, CobraReaction, CobraMetabolite, CobraFba, CobraFva

from backend.celery import app


class CobraWrapperViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test123456')
        self.metabolites = [
            CobraMetabolite.objects.create(
                cobra_id='ACP_c',
                formula='C11H21N2O7PRS',
                name='acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=self.user
            ),
            CobraMetabolite.objects.create(
                cobra_id='3omrsACP_c',
                formula='C25H45N2O9PRS',
                name='3-Oxotetradecanoyl-acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=self.user
            ),
            CobraMetabolite.objects.create(
                cobra_id='co2_c',
                formula='CO2',
                name='CO2',
                compartment='c',
                charge='1',
                owner=self.user
            ),
            CobraMetabolite.objects.create(
                cobra_id='malACP_c',
                formula='C14H22N2O10PRS',
                name='Malonyl-acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=self.user
            ),
            CobraMetabolite.objects.create(
                cobra_id='h_c',
                formula='H',
                name='H',
                compartment='c',
                charge='1',
                owner=self.user
            ),
            CobraMetabolite.objects.create(
                cobra_id='ddcaACP_c',
                formula='C23H43N2O8PRS',
                name='Dodecanoyl-ACP-n-C120ACP',
                compartment='c',
                charge='1',
                owner=self.user
            )
        ]

        self.reaction = CobraReaction.objects.create(
            cobra_id='3OAS140',
            name='3 oxoacyl acyl carrier protein synthase n C140',
            subsystem='Cell Envelope Biosynthesis',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='( STM2378 or STM1197 )',
            owner=self.user
        )
        self.reaction.metabolites.set(self.metabolites)

        self.metabolites.append(
            CobraMetabolite.objects.create(
                cobra_id='useless',
                formula='U',
                name='test',
                compartment='c',
                charge='1',
                owner=self.user
            ))

        self.model = CobraModel.objects.create(
            cobra_id='example_model',
            name='test',
            objective='3OAS140',
            owner=self.user
        )
        self.model.reactions.set([self.reaction])
        self.client.login(username='test', password='test123456')

    def test_metabolites_list(self):
        response = self.client.get('/cobra/metabolites/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrametabolite_list.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        for comp in ['1', 'ACP_c', 'acyl-carrier-protein']:
            self.assertContains(response, comp)
        for comp in ['2', '3omrsACP_c', '3-Oxotetradecanoyl-acyl-carrier-protein']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/metabolites/1/">Detail</a>')

    def test_reactions_list(self):
        response = self.client.get('/cobra/reactions/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrareaction_list.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        for comp in ['1', '3OAS140', '3 oxoacyl acyl carrier protein synthase n C140']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/reactions/1/">Detail</a>')

    def test_models_list(self):
        response = self.client.get('/cobra/models/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_list.html')
        # for comp in ['id', 'cobra_id', 'name']:
        #     self.assertContains(response, comp)
        # for comp in ['1', 'example_model', 'test']:
        #     self.assertContains(response, comp)
        for comp in ['example_model', 'test']:
            self.assertContains(response, comp)
        # self.assertContains(response, '<a href="/cobra/models/1/">Detail</a>')
        self.assertContains(response, '/cobra/models/1/')

    def test_metabolites_detail(self):
        response = self.client.get('/cobra/metabolites/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrametabolite_detail.html')
        for comp in ['id', 'cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)
        for comp in ['1', 'ACP_c', 'acyl-carrier-protein', 'C11H21N2O7PRS', '1', 'c']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/metabolites/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/1/update/">Edit</a>', html=True)

        response = self.client.get('/cobra/metabolites/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_reactions_detail(self):
        response = self.client.get('/cobra/reactions/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrareaction_detail.html')
        for comp in ['id', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                     'metabolites and coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)
        for comp in ['1', '3OAS140', '3 oxoacyl acyl carrier protein synthase n C140', 'Cell Envelope Biosynthesis',
                     0, 1000, '( STM2378 or STM1197 )']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/reactions/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/1/update/">Edit</a>', html=True)

        response = self.client.get('/cobra/reactions/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_models_detail(self):
        response = self.client.get('/cobra/models/1/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_detail.html')
        for comp in ['id', 'cobra_id', 'name', 'objective', 'reactions']:
            self.assertContains(response, comp)
        for comp in ['1', 'example_model', 'test', '3OAS140']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/">FBA</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/">FVA</a>', html=True)

        response = self.client.get('/cobra/reactions/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_metabolites_create(self):
        # TODO(myl7): Get a form, input it, post the form and be redirected to detail. Need an example.
        # TODO(lbc12345): Redirect test past, don't know is it OK?
        self.client.post('/cobra/metabolites/create/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='test',
            compartment='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/metabolites/create/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='1',
            compartment='test'))
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_list.html')
        self.assertRedirects(response, '/cobra/metabolites/8/')

        response = self.client.get('/cobra/metabolites/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)

        # test for change
        response = self.client.get('/cobra/metabolites/8/')
        self.assertContains(response, 'the instance is created at')

    def test_reactions_create(self):
        self.client.post('/cobra/reactions/create/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='test'))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/reactions/create/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            coefficients='',
            gene_reaction_rule='test'))
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_list.html')
        self.assertRedirects(response, '/cobra/reactions/2/')

        response = self.client.get('/cobra/reactions/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                     'metabolites', 'coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)

        # test for change
        response = self.client.get('/cobra/reactions/2/')
        self.assertContains(response, 'the instance is created at')

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

    def test_metabolites_update(self):
        response = self.client.post('/cobra/metabolites/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='test',
            compartment='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='0',
            compartment='test'
        ))
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_detail.html')
        self.assertRedirects(response, '/cobra/metabolites/1/')

        # test for change
        response = self.client.get('/cobra/metabolites/1/')
        changed_data = 'cobra_id, name, formula, charge, compartment'
        changed_data += ' is changed from ACP_c, acyl-carri... to test, test, test,... at'
        self.assertContains(response, changed_data)

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='1',
            compartment='test'
        ))
        response = self.client.get('/cobra/metabolites/1/')
        self.assertContains(response, 'charge is changed from 0.0 to 1.0 at')

        response = self.client.get('/cobra/metabolites/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)

    def test_reactions_update(self):
        response = self.client.post('/cobra/reactions/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/reactions/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='test'))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/reactions/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            coefficients='',
            gene_reaction_rule='test'))
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_detail.html')
        self.assertRedirects(response, '/cobra/reactions/1/')

        # test for change
        response = self.client.get('/cobra/reactions/1/')
        changed_data = 'cobra_id, name, subsystem, metabolites, coefficients, gene_reaction_rule'
        changed_data += ' is changed from 3OAS140, 3 oxoacy... to test, test, test,... at'
        self.assertContains(response, changed_data)

        self.client.post('/cobra/reactions/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=1,
            upper_bound=1000,
            coefficients='',
            gene_reaction_rule='test'))
        response = self.client.get('/cobra/reactions/1/')
        self.assertContains(response, 'lower_bound is changed from 0.0 to 1.0 at')

        response = self.client.get('/cobra/reactions/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                     'metabolites', 'coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)

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

    def test_metabolites_delete(self):
        # TODO(lbc12345): Does this satisfy the requirement?
        response = self.client.post('/cobra/metabolites/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/metabolites/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_confirm_delete.html')
        self.assertContains(response, '<p>You can not delete the metabolite!</p>', html=True)

        response = self.client.get('/cobra/metabolites/7/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_confirm_delete.html')
        self.assertContains(response, '<p>Are you sure to delete: useless[test]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)

        response = self.client.post('/cobra/metabolites/1/delete/')
        self.assertRedirects(response, '/cobra/metabolites/')

    def test_reactions_delete(self):
        response = self.client.post('/cobra/reactions/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/reactions/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_confirm_delete.html')
        self.assertContains(response, '<p>You can not delete the reaction!</p>', html=True)

        response = self.client.post('/cobra/reactions/1/delete/')
        self.assertRedirects(response, '/cobra/reactions/')

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
        reaction_object = CobraReaction.objects.get(pk=1)

        # real create
        self.client.post('/cobra/models/1/fva/create/', dict(
            desc='test',
            reaction_list=[reaction_object.pk],
            loopless='',
            fraction_of_optimum='1.0',
            pfba_factor='unknown'
        ))  # Create a fva from frontend

        model_object = CobraModel.objects.get(pk=1)
        fva = CobraFba.objects.create(desc='test', model=model_object)
        fva.save()
        cobra_fva_kwargs = {
            'reaction_list': [reaction_object.cobra_id],
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

# Unused code

        # metabolite_0_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='ACP_c',
        #     formula='C11H21N2O7PRS',
        #     name='acyl-carrier-protein',
        #     compartment='c'))
        # self.assertEqual(metabolite_0_response.status_code, 302)
        # metabolite_1_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='3omrsACP_c',
        #     formula='C25H45N2O9PRS',
        #     name='3-Oxotetradecanoyl-acyl-carrier-protein',
        #     compartment='c'))
        # self.assertEqual(metabolite_1_response.status_code, 302)
        # metabolite_2_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='co2_c',
        #     formula='CO2',
        #     name='CO2',
        #     compartment='c'))
        # self.assertEqual(metabolite_2_response.status_code, 302)
        # metabolite_3_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='malACP_c',
        #     formula='C14H22N2O10PRS',
        #     name='Malonyl-acyl-carrier-protein',
        #     compartment='c'))
        # self.assertEqual(metabolite_3_response.status_code, 302)
        # metabolite_4_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='h_c',
        #     formula='H',
        #     name='H',
        #     compartment='c'))
        # self.assertEqual(metabolite_4_response.status_code, 302)
        # metabolite_5_response = self.client.post('/cobra/metabolites/', dict(
        #     cobra_id='ddcaACP_c',
        #     formula='C23H43N2O8PRS',
        #     name='Dodecanoyl-ACP-n-C120ACP',
        #     compartment='c'))
        # self.assertEqual(metabolite_5_response.status_code, 302)
        # metabolite_set_response = self.client.get('/cobra/metabolites/')
        # self.assertContains(metabolite_set_response, 'content')

        # reaction_response = self.client.post('/cobra/reactions/', dict(
        #     cobra_id='3OAS140',
        #     name='3 oxoacyl acyl carrier protein synthase n C140 ',
        #     subsystem='Cell Envelope Biosynthesis',
        #     lower_bound=0,
        #     upper_bound=1000,
        #     metabolites=[1, 2, 3, 4, 5, 6],
        #     coefficients=[-1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
        #     gene_reaction_rule='( STM2378 or STM1197 )'))
        # self.assertEqual(reaction_response.status_code, 302)
        # reaction_set_response = self.client.get('/cobra/reactions/')
        # self.assertContains(reaction_set_response, 'content')

        # model_response = self.client.post('/cobra/models/', dict(
        #     cobra_id='example_model',
        #     objective='3OAS140'))
        # self.assertEqual(model_response.status_code, 302)
        # model_set_response = self.client.get('/cobra/models/', content_type='application/json')
        # self.assertContains(model_set_response, 'content')
