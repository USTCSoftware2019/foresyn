import os
import glob
import shutil

from django.core.management.base import BaseCommand, CommandError


def main():
    venv_dir = os.environ.get('VIRTUAL_ENV', None)
    if not venv_dir:
        raise CommandError('Can not determine venv dir')
    available_mysql_dir = os.path.join(
        venv_dir, 'lib', 'python3.*', 'site-packages', 'django', 'db', 'backends', 'mysql')
    found_mysql_dir = glob.glob(available_mysql_dir)
    if not found_mysql_dir:
        raise CommandError('Can not find the django mysql dir: {}'.format(available_mysql_dir))
    mysql_dir = found_mysql_dir[0]
    base_path = os.path.join(mysql_dir, 'base.py')
    operation_path = os.path.join(mysql_dir, 'operations.py')

    if not os.path.isfile(base_path + '.bak'):
        shutil.copyfile(base_path, base_path + '.bak')

    if not os.path.isfile(operation_path + '.bak'):
        shutil.copyfile(operation_path, operation_path + '.bak')

    content = []
    with open(base_path, 'r') as file:
        for line in file:
            if line.strip() != (
                    r"raise ImproperlyConfigured("
                    r"'mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)"):
                content.append(line)
            else:
                content.append('# ' + line)
                content.append('    pass\n')
    with open(base_path, 'w') as file:
        file.writelines(content)

    content = []
    with open(operation_path, 'r') as file:
        for line in file:
            if line.strip() != r"query = query.decode(errors='replace')":
                content.append(line)
            else:
                content.append("            query = query.encode(errors='replace')\n")
    with open(operation_path, 'w') as file:
        file.writelines(content)


class Command(BaseCommand):
    """
    Django requires newer mysqlclient but pymysql requires lower one.
    The command fixes the problem according to
    https://stackoverflow.com/questions/55657752/django-installing-mysqlclient-error-mysqlclient-1-3-13-or-newer-is-required
    by editing django library.
    If better solution is found, remove the command.
    """
    help = 'Fix dependency problem between django and pymysql towards mysqlclient'

    def handle(self, **kwargs):
        main()
