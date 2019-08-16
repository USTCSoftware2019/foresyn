from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import CobraModel, CobraReaction, CobraMetabolite


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
        self.assertContains(response, 'href="/cobra/metabolites/1/"')
        self.assertContains(response, 'href="/cobra/metabolites/2/"')

    def test_reactions_list(self):
        response = self.client.get('/cobra/reactions/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobrareaction_list.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        for comp in ['1', '3OAS140', '3 oxoacyl acyl carrier protein synthase n C140']:
            self.assertContains(response, comp)
        self.assertContains(response, 'href="/cobra/reactions/1/"')

    def test_models_list(self):
        response = self.client.get('/cobra/models/')
        self.assertTemplateUsed(response, 'cobra_wrapper/cobramodel_list.html')
        for comp in ['id', 'cobra_id', 'name']:
            self.assertContains(response, comp)
        for comp in ['1', 'example_model', 'test']:
            self.assertContains(response, comp)
        self.assertContains(response, 'href="/cobra/models/1/"')

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

    def test_create_metabolites(self):
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

    def test_create_reactions(self):
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

    def test_create_models(self):
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

    def test_update_metabolites(self):
        # TODO(myl7): Get a form, input it, post the form and be redirected to detail. Need an example.
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

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            formula='test',
            charge='test',
            compartment='test'))
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrametabolite_detail.html')

        response = self.client.get('/cobra/metabolites/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/metabolites/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'formula', 'charge', 'compartment']:
            self.assertContains(response, comp)

    def test_update_reactions(self):
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
            coefficients='-1.0, -1.0, -1.0, 1.0, 1.0, 1.0',
            gene_reaction_rule='test'))
        self.assertRaises(ValidationError)

        response = self.client.post('/cobra/reactions/1/update/', dict(
            cobra_id='test',
            name='test',
            subsystem='test',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='test'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_detail.html')

        response = self.client.get('/cobra/reactions/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/reactions/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'subsystem', 'lower_bound', 'upper_bound',
                     'metabolites', 'coefficients', 'gene_reaction_rule']:
            self.assertContains(response, comp)

    def test_update_models(self):
        response = self.client.post('/cobra/metabolites/7777777/update/', dict(
            cobra_id='test'
        ))
        self.assertEqual(response.status_code, 404)

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test' * 50))
        self.assertRaises(ValidationError)

        self.client.post('/cobra/metabolites/1/update/', dict(
            cobra_id='test',
            name='test',
            objective='test'))
        self.assertTemplateUsed('cobra_wrapper/cobramodel_update_form.html')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_detail.html')

        response = self.client.get('/cobra/models/1/update/')
        self.assertContains(response, '<input type="reset" value="Reset">', html=True)
        self.assertContains(response, '<input type="submit" value="Update">', html=True)
        self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
        for comp in ['cobra_id', 'name', 'reactions', 'objective']:
            self.assertContains(response, comp)

    def test_delete_metabolites(self):
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
        self.assertEqual(response.status_code, 302)

    def test_delete_reactions(self):
        # TODO(lbc12345): I don't think the successful deletion way can be tested. Like Are you sure to delete blabla...
        response = self.client.post('/cobra/reactions/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/reactions/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobrareaction_confirm_delete.html')
        self.assertContains(response, '<p>You can not delete the reaction!</p>', html=True)

        response = self.client.post('/cobra/reactions/1/delete/')
        self.assertEqual(response.status_code, 302)

    def test_delete_models(self):
        response = self.client.post('/cobra/models/7777777/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/cobra/models/1/delete/')
        self.assertTemplateUsed('cobra_wrapper/cobramodel_confirm_delete.html')
        self.assertContains(response, '<p>Are you sure to delete: example_model[test]?</p>', html=True)
        self.assertContains(response, '<input type="submit" value="Confirm">', html=True)

        response = self.client.post('/cobra/models/1/delete/')
        self.assertEqual(response.status_code, 302)

    # def test_fba(self):
    #     response = self.client.get('/cobra/models/1/fba/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed('cobra_wrapper/cobrafba_detail.html')
    #     for comp in ['objective_value', 'status', 'fluxes', 'shadow_price']:
    #         self.assertContains(response, comp)
    #     self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
    #     self.assertNotContains(response, 'maximum')
    #
    # def test_fva_create(self):
    #     response = self.client.get('/cobra/models/1/fva/create/')
    #     self.assertTemplateUsed('cobra_wrapper/cobrafva_create_form.html')
    #     for comp in ['loopless', 'fraction_of_optimum', 'pfba_factor', 'reaction_list']:
    #         self.assertContains(response, comp)
    #     self.assertContains(response, '<input type="reset" value="Reset">', html=True)
    #     self.assertContains(response, '<input type="submit" value="Submit">', html=True)
    #     self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)
    #     self.assertNotContains(response, 'minimum')
    #
    # def test_fva(self):
    #     response = self.client.get('/cobra/models/1/fva/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed('cobra_wrapper/cobrafva_detail.html')
    #     for comp in ['name', 'maximum', 'minimum']:
    #         self.assertContains(response, comp)
    #     self.assertContains(response, '<a href="/cobra/models/1/">Return</a>', html=True)

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
