from datetime import datetime
from hashlib import sha256

from django.core.exceptions import ObjectDoesNotExist

# FIXME(myl7): Remove metabolites and reactions
# from .models import (MetaboliteShare, ModelShare, OneTimeShareLink,
#                      ReactionShare)
from .models import ModelShare, OneTimeShareLink

share_type_map = {
    'model': ModelShare,
    # 'reaction': ReactionShare,
    # 'metabolite': MetaboliteShare
}


class OneTimeShareLinkManager:
    @staticmethod
    def acquire_key(shared_type, shared_id):
        '''
        Never expose this api to user without asking password
        '''
        obj = share_type_map[shared_type]
        password = obj.objects.get(id=shared_id)
        key = sha256(('{shared_type}_{shared_id}_{current_time}_{password}_{salt}'.format(
            shared_type=shared_type,
            shared_id=shared_id,
            current_time=datetime.timestamp(datetime.now()),
            password=password,
            salt='USTC-Software')).encode()).hexdigest()[:15]
        OneTimeShareLink.objects.create(key=key, shared_id=shared_id, shared_type=shared_type)
        return key

    @staticmethod
    def check_key(key, shared_type, shared_id):
        if not key:
            return False
        try:
            query_result = OneTimeShareLink.objects.get(key=key)
        except ObjectDoesNotExist:
            return False

        if query_result.shared_type == shared_type and query_result.shared_id == str(shared_id):
            query_result.delete()
            return True
        else:
            return False
