from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View, CreateView
from .forms import UserSignUpForm
from .tokens import account_activation_token
from django.core.mail import EmailMessage


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
            return render(request, "accounts/signup_done.html")


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
            login(request, user)
            success = True
        else:
            success = False

        return render(request, "accounts/activate_done.html", {
            "success": success
        })