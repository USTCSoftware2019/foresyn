from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
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
from .models import PackModel, PackReaction, PackGene, PackMetabolite, PackComputationalModel


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
    def get_obj(self, user, obj_type, pk):
        if obj_type == "model":
            return PackModel.objects.filter(user=user, model=pk)
        elif obj_type == "usermodel":
            return PackComputationalModel.objects.filter(user=user, model=pk)  # FIXME
        elif obj_type == "reaction":
            return PackReaction.objects.filter(user=user, reaction=pk)
        elif obj_type == "gene":
            return PackGene.objects.filter(user=user, gene=pk)
        elif obj_type == "metabolite":
            return PackMetabolite.objects.filter(user=user, metabolite=pk)
        elif obj_type == "biobrick":
            raise NotImplemented

    def get(self, request):
        obj_type = request.POST.get("type")

        counts = {
            "model": PackModel.objects.filter(user=request.user).count(),
            "usermodel": PackComputationalModel.objects.filter(user=request.user).count(),
            "reaction": PackReaction.objects.filter(user=request.user).count(),
            "gene": PackGene.objects.filter(user=request.user).count(),
            "metabolite": PackMetabolite.objects.filter(user=request.user).count()
        }

        if not obj_type:
            obj_type = "model"

        queryset = None
        if obj_type == "model":
            queryset = PackModel.objects.filter(user=request.user)
        elif obj_type == "usermodel":
            queryset = PackComputationalModel.objects.filter(user=request.user)
        elif obj_type == "reaction":
            queryset = PackReaction.objects.filter(user=request.user)
        elif obj_type == "gene":
            queryset = PackGene.objects.filter(user=request.user)
        elif obj_type == "metabolite":
            queryset = PackMetabolite.objects.filter(user=request.user)
        elif obj_type == "biobrick":
            raise NotImplemented

        return render(request, "accounts/pack.html", {
            "type": obj_type,
            "counts": counts,
            "this_cnt": queryset.count(),
            "queryset": queryset
        })

    def post(self, request):
        obj_type = request.POST.get("type")
        action = request.POST.get("action")
        pk = request.POST.get("pk")
        obj = self.get_obj(request.user, obj_type, pk)
        if action == "query":
            if not obj:
                return JsonResponse({"result": 0})
            else:
                return JsonResponse({"result": 1})
            pass
        elif action == "add":
            if not obj:
                if obj_type == "model":
                    return PackModel.objects.create(user=request.user, model=pk)
                elif obj_type == "usermodel":
                    return PackComputationalModel.objects.create(user=request.user, model=pk)  # FIXME
                elif obj_type == "reaction":
                    return PackReaction.objects.filter(user=request.user, reaction=pk)
                elif obj_type == "gene":
                    return PackGene.objects.filter(user=request.user, gene=pk)
                elif obj_type == "metabolite":
                    return PackMetabolite.objects.filter(user=request.user, metabolite=pk)
                elif obj_type == "biobrick":
                    raise NotImplemented
        elif action == "delete":
            if obj:
                obj.delete()
        else:
            return HttpResponse("error")

        return HttpResponse("ok")
