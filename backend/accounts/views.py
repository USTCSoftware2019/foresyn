from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, CreateView
from .forms import UserSignUpForm
from .tokens import account_activation_token
from django.core.mail import EmailMessage
# from .models import PackModel, PackReaction, PackGene, PackMetabolite, PackComputationalModel
from .models import Favorite
from django.apps import apps

class UserSignUp(CreateView):
    template_name = 'accounts/signup.html'
    form_class = UserSignUpForm
    # success_url = reverse_lazy('login')  # this router is loaded after accounts app, so use reverse_lazy

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            mail_subject = 'Activate your account'
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            to_email = form.cleaned_data.get('email')
            message = render_to_string('accounts/activate_email.html', {
                "protocol": "http",  # FIXME: protocol
                "domain": current_site,
                "uid": uid,
                "token": token,
                "email": to_email,
            })
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return redirect("accounts:signup_done")
        else:
            return render(request, "accounts/signup.html", {
                "form": form,
            })


class UserActivation(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            # login(request, user)
            success = True
        else:
            success = False

        return render(request, "accounts/activate_done.html", {
            "success": success
        })


class UserProfile(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, "accounts/profile.html", {
            "first": user.first_name,
            "last": user.last_name,
            "username": user.username,
        })

    def post(self, request):
        first = request.POST.get("first")
        last = request.POST.get("last")
        user = request.user

        if first and last:
            user.first_name = first
            user.last_name = last
            user.save()

        return redirect("accounts:profile")


@method_decorator(csrf_exempt, name='dispatch')  # temporary workaround
class UserPack(LoginRequiredMixin, View):
    pass
    # def get_obj(self, user, obj_type, pk):
    #     if obj_type == "model":
    #         return PackModel.objects.filter(user=user, model=pk)
    #     elif obj_type == "usermodel":
    #         return PackComputationalModel.objects.filter(user=user, model=pk)  # FIXME
    #     elif obj_type == "reaction":
    #         return PackReaction.objects.filter(user=user, reaction=pk)
    #     elif obj_type == "gene":
    #         return PackGene.objects.filter(user=user, gene=pk)
    #     elif obj_type == "metabolite":
    #         return PackMetabolite.objects.filter(user=user, metabolite=pk)
    #     elif obj_type == "biobrick":
    #         raise NotImplementedError()
    #
    def get(self, request):
        obj_type = request.POST.get("type")

        counts = {
            "model": Favorite.objects.filter(user=request.user, target_content_type=ContentType.objects.get(
                app_label='bigg_database', model='model')).count(),
            "usermodel": 1,
            "reaction": 1,
            "gene": 1,
            "metabolite": 1
        }

        if not obj_type:
            obj_type = "model"

        queryset = None
        if obj_type == "model":
            queryset = Favorite.objects.filter(user=request.user, target_content_type=ContentType.objects.get(
                app_label='bigg_database', model='model'))
        # elif obj_type == "usermodel":
        #     queryset = PackComputationalModel.objects.filter(user=request.user)
        # elif obj_type == "reaction":
        #     queryset = PackReaction.objects.filter(user=request.user)
        # elif obj_type == "gene":
        #     queryset = PackGene.objects.filter(user=request.user)
        # elif obj_type == "metabolite":
        #     queryset = PackMetabolite.objects.filter(user=request.user)

        return render(request, "accounts/pack.html", {
            "type": obj_type,
            "counts": counts,
            "this_cnt": queryset.count(),
            "queryset": queryset
        })
    # this favorite implementation uses django-favorite
    def post(self, request):
        user = request.user
        target_model = apps.get_model(app_label=request.POST['target_app'],
                                      model_name=request.POST['target_name'])
        target_content_type = ContentType.objects.get_for_model(target_model)
        target_object_id = request.POST['target_object_id']

        # delete it if it's already a favorite
        if user.favorite_set.filter(target_content_type=target_content_type,
                                    target_object_id=target_object_id):
            user.favorite_set.get(target_content_type=target_content_type,
                                  target_object_id=target_object_id).delete()
            status = 'deleted'

        # otherwise, create it
        else:
            user.favorite_set.create(target_content_type=target_content_type,
                                     target_object_id=target_object_id)
            status = 'added'

        response = {'status': status,
                    'fav_count': Favorite.objects.filter(target_content_type=target_content_type,
                                                         target_object_id=target_object_id).count()}

        return JsonResponse(response)
