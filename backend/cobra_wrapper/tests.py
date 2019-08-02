import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

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
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='3omrsACP_c',
                formula='C25H45N2O9PRS',
                name='3-Oxotetradecanoyl-acyl-carrier-protein',
                compartment='c',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='co2_c',
                formula='CO2',
                name='CO2',
                compartment='c',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='malACP_c',
                formula='C14H22N2O10PRS',
                name='Malonyl-acyl-carrier-protein',
                compartment='c',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='h_c',
                formula='H',
                name='H',
                compartment='c',
                owner=user
            ),
            CobraMetabolite.objects.create(
                cobra_id='ddcaACP_c',
                formula='C23H43N2O8PRS',
                name='Dodecanoyl-ACP-n-C120ACP',
                compartment='c',
                owner=user
            )
        ]

        reaction = CobraReaction.objects.create(
            cobra_id='3OAS140',
            name='3 oxoacyl acyl carrier protein synthase n C140 ',
            subsystem='Cell Envelope Biosynthesis',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='( STM2378 or STM1197 )',
            owner=user
        )
        reaction.metabolites.set(metabolites)

        model = CobraModel.objects.create(
            cobra_id='example_model',
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

    def test_list(self):
        self._create_models(self._create_user_and_login())

        # metabolite_0_response = self.client.post('/cobra/metabolites/', dict(  # FIXME:
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

    def test_detail(self):
        info = self._create_models(self._create_user_and_login())
        info

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

    def test_create_ok(self):
        self._create_user_and_login()

    def test_create_fail(self):
        self._create_user_and_login()

    def test_update_ok(self):
        info = self._create_models(self._create_user_and_login())
        info

    def test_update_fail(self):
        info = self._create_models(self._create_user_and_login())
        info

    def test_delete_ok(self):
        info = self._create_models(self._create_user_and_login())
        info

    def test_delete_fail(self):
        info = self._create_models(self._create_user_and_login())
        info

    def test_fba(self):
        info = self._create_models(self._create_user_and_login())
        info

    def test_fva(self):
        info = self._create_models(self._create_user_and_login())
        info
