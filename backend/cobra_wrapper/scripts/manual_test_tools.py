import os

import fabric
import invoke

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@fabric.task
def init_db_for_cobra(connection):
    with connection.cd(BASE_DIR):
        with connection.prefix('source ../venv/bin/activate'):
            connection.run('rm -f db.sqlite3')
            connection.run('find cobra_wrapper/migrations -name \'000*.py\' -delete')
            connection.run('./manage.py makemigrations')
            connection.run('./manage.py migrate')
            super_user_watchers = [
                invoke.Responder(pattern=r'Username.*:', response='test\n'),
                invoke.Responder(pattern=r'Email address:', response='\n'),
                invoke.Responder(pattern=r'Password:', response='test123456\n'),
                invoke.Responder(pattern=r'Password \(again\):', response='test123456\n')
            ]
            connection.run('./manage.py createsuperuser', pty=True, watchers=super_user_watchers)
            create_cobra_example_model_responder = invoke.Responder(
                pattern=r'Python.*\(InteractiveConsole\)',
                response='''
from django.contrib.auth.models import User
user = User.objects.get(username='test')
from cobra_wrapper.models import CobraModel, CobraReaction, CobraMetabolite
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
exit()
'''
            )
            connection.run('./manage.py shell', pty=True, watchers=[create_cobra_example_model_responder])
