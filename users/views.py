from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import login
from django.views.generic import FormView
from .forms import SignUpForm, EmailLoginForm
from .services import UserService
from django.urls import reverse_lazy

# Create your views here.
class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        user = UserService.create_user(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"]
        )
        login(self.request, user)
        return super().form_valid(form)


class LoginView(DjangoLoginView):
    template_name = "users/login.html"
    form_class = EmailLoginForm
    redirect_authenticated_user = True
    