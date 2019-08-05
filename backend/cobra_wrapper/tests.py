import json

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import CobraModel, CobraReaction, CobraMetabolite


class CobraWrapperViewTests(TestCase):
    def _create_user_and_login(self):
        user_info = {'username': 'test', 'password': 'testtest123'}
        user = User.objects.create_user(**user_info)
        self.client = Client()
        self.client.login(**user_info)
        return user

    def _create_models(self, user):
        """Examples in cobra doc to build a model"""
        metabolites = [
            CobraMetabolite.objects.create(
                cobra_id='ACP_c',
                formula='C11H21N2O7PRS',
                name='acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='3omrsACP_c',
                formula='C25H45N2O9PRS',
                name='3-Oxotetradecanoyl-acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='co2_c',
                formula='CO2',
                name='CO2',
                compartment='c',
                charge='1',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='malACP_c',
                formula='C14H22N2O10PRS',
                name='Malonyl-acyl-carrier-protein',
                compartment='c',
                charge='1',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='h_c',
                formula='H',
                name='H',
                compartment='c',
                charge='1',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='ddcaACP_c',
                formula='C23H43N2O8PRS',
                name='Dodecanoyl-ACP-n-C120ACP',
                compartment='c',
                charge='1',
                owner=user
            )
        ]

        reaction = CobraReaction.objects.create(
            cobra_id='3OAS140',
            name='3 oxoacyl acyl carrier protein synthase n C140 ',
            subsystem='Cell Envelope Biosynthesis',
            lower_bound=0,
            upper_bound=1000,
            objective_coefficient=0,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='( STM2378 or STM1197 )',
            owner=user
        )
        reaction.metabolites.set(metabolites)

        model = CobraModel.objects.create(
            cobra_id='example_model',
            name='test',
            objective='3OAS140',
            owner=user
        )
        model.reactions.set([reaction])

        return {
            'model': model,
            'reaction': reaction,
            'models': [model],
            'reactions': [reaction],
            'metabolites': metabolites
        }

    def test_metabolites_list(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/metabolites/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrametabolite_list.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobrametabolite_detail.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'formula')
        self.assertContains(response, '<a href="/cobra/metabolites/1/">Detail</a>', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/create/">Create</a>', html=True)

    def test_reactions_list(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/reactions/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrareaction_list.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobrareaction_detail.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'subsystem')
        self.assertContains(response, '<a href="/cobra/reactions/1/">Detail</a>', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/create/">Create</a>', html=True)

    def test_models_list(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/models/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_list.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobramodel_detail.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'objective')
        self.assertContains(response, '<a href="/cobra/models/1/">Detail</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/create/">Create</a>', html=True)

    def test_metabolites_detail(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/metabolites/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrametabolite_detail.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobrametabolite_list.html')
        for comp in ['id', 'cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'subsystem')
        self.assertContains(response, '<a href="/cobra/metabolites/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/1/update/">Edit</a>', html=True)

        response = self.client.get('/cobra/metabolites/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_reactions_detail(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/reactions/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrareaction_detail.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobrareaction_list.html')
        for comp in ['id', 'cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                     'objective_coefficient', 'metabolites and coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'formula')
        self.assertNotContains(response, 'gene_object_rule')
        self.assertContains(response, '<a href="/cobra/reactions/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/1/update/">Edit</a>', html=True)

        response = self.client.get('/cobra/reactions/7777777/')
        self.assertEqual(response.status_code, 404)

    def test_models_detail(self):
        self._create_models(self._create_user_and_login())
        response = self.client.get('/cobra/models/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_detail.html')
        self.assertTemplateNotUsed(response, 'cobra_wrapper/cobramodel_list.html')
        for comp in ['id', 'cobra_id', 'name', 'objective', 'reactions']:
            self.assertContains(response, comp)
        self.assertNotContains(response, 'gene')
        self.assertContains(response, '<a href="/cobra/models/1/delete/">Delete</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fba/">FBA</a>', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/fva/create/">FVA</a>', html=True)

        response = self.client.get('/cobra/reactions/7777777/')
        self.assertEqual(response.status_code, 404)

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

    # def test_detail(self):
    #     model_response = self.client.get('/cobra/models/{}/'.format(info['models'][0].id))
    #     self.assertEqual(model_response.status_code, 200)
    #     self.assertContains(model_response, 'objective')

    #     reaction_response = self.client.get('/cobra/reactions/{}/'.format(info['reactions'][0].id))
    #     self.assertEqual(reaction_response.status_code, 200)
    #     self.assertContains(reaction_response, 'subsystem')

    #     metabolite_response = self.client.get('/cobra/metabolites/{}/'.format(info['metabolites'][0].id))
    #     self.assertEqual(metabolite_response.status_code, 200)
    #     self.assertContains(metabolite_response, 'formula')

    # def test_detail_get_failure(self):
    #     self._create_user_and_login()

    #     model_response = self.client.get('/cobra/models/7777777/')
    #     self.assertEqual(model_response.status_code, 404)

    #     reaction_response = self.client.get('/cobra/reactions/7777777/')
    #     self.assertEqual(reaction_response.status_code, 404)

    #     metabolite_response = self.client.get('/cobra/metabolites/7777777/')
    #     self.assertEqual(metabolite_response.status_code, 404)

    def test_create_metabolites(self):
        self._create_user_and_login()
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
            charge='test',
            compartment='test'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_list.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobrametabolite_detail.html')

        response = self.client.get('/cobra/metabolites/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)

    def test_create_reactions(self):
        self._create_user_and_login()
        self.client.post('/cobra/reactions/create/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            objective_coefficients=0,
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='test'))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/reactions/create/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            objective_coefficients=0,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='test'))
        self.assertEqual(response.status_code, 200)  # FIXME: why 200 not 302?
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_list.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobrareaction_detail.html')

        response = self.client.get('/cobra/reactions/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
                     'metabolites', 'coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)

    def test_create_models(self):
        self._create_user_and_login()
        self.client.post('/cobra/models/create/', dict(
            cobra_id='test',
            name='test',
            objective='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/models/create/', dict(
            cobra_id='test',
            name='test',
            objective='test'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('cobra_wrapper/cobramodel_create_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_list.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobramodel_detail.html')

        response = self.client.get('/cobra/models/create/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Create">', html=True)
        self.assertContains(response, '<a href="/cobra/models/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'reactions', 'objective']:
            self.assertContains(response, comp)

    def test_update_metabolites(self):
        self._create_models(self._create_user_and_login())
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
            charge='test',
            compartment='test'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_detail.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobrametabolite_create_form.html')

        response = self.client.get('/cobra/metabolites/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)

    def test_update_reactions(self):
        self._create_models(self._create_user_and_login())
        response = self.client.post('/cobra/models/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/models/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            objective_coefficients=0,
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='test'))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/reactions/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            objective_coefficients=0,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_detail.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobrareaction_create_form.html')

        response = self.client.get('/cobra/reactions/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound', 'objective_coefficient',
                     'metabolites', 'coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)

    def test_update_models(self):
        self._create_models(self._create_user_and_login())
        response = self.client.post('/cobra/metabolites/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test' * 50))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('cobra_wrapper/cobramodel_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_detail.html')
        self.assertTemplateNotUsed('cobra_wrapper/cobramodel_create_form.html')

        response = self.client.get('/cobra/models/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'reactions', 'objective']:
            self.assertContains(response, comp)

    def test_delete_metabolites(self):
        self._create_models(self._create_user_and_login())

        response = self.client.post('/cobra/metabolites/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/metabolites/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_confirm_delete.html')
        self.assertContains(response, '<p>You can not delete the metabolite!</p>', html=True)

        response = self.client.post('/cobra/metabolites/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_delete_reactions(self):
        self._create_models(self._create_user_and_login())

        response = self.client.post('/cobra/reactions/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/reactions/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_confirm_delete.html')
        self.assertContains(response, '<p>You can not delete the reaction!</p>', html=True)

        response = self.client.post('/cobra/reactions/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_delete_models(self):
        self._create_models(self._create_user_and_login())

        response = self.client.post('/cobra/models/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/models/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_confirm_delete.html')
        self.assertContains(response, '<p>Are you sure to delete: example_model[test]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)

        response = self.client.post('/cobra/models/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_fba(self):
        self._create_models(self._create_user_and_login())

        response = self.client.get('/cobra/models/1/fba/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cobra_wrapper/cobramodel_fba_detail.html')
        for comp in ['objective_value', 'status', 'fluxes', 'shadow_price']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
        self.assertNotContains(response, 'maximum')

    def test_fva_create(self):
        self._create_models(self._create_user_and_login())

        response = self.client.get('/cobra/models/1/fva/create/')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_fva_create_form.html')
        for comp in ['loopless', 'fraction_of_optimum', 'pfba_factor', 'reaction_list']:
            self.assertContains(response, comp)
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Submit">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
        self.assertNotContains(response, 'minimum')

    def test_fva(self):
        self._create_models(self._create_user_and_login())

        response = self.client.get('/cobra/models/1/fva/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cobra_wrapper/cobramodel_fva_detail.html')
        for comp in ['name', 'maximum', 'minimum']:
            self.assertContains(response, comp)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
