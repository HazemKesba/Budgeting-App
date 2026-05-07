from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import login
from django.views.generic import FormView
from .forms import SignUpForm, EmailLoginForm
from .services import UserService
from django.urls import reverse_lazy

class SignupView(FormView):
    """Handles user registration via a plain form and delegates creation to UserService."""
    
    template_name = "users/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        """Process valid form data, create user via service layer, and log them in."""
        user = UserService.create_user(
            full_name=form.cleaned_data["full_name"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"]
        )
        login(self.request, user)
        return super().form_valid(form)

class LoginView(DjangoLoginView):
    """Handles user authentication using email-based credentials."""
    
    template_name = "users/login.html"
    form_class = EmailLoginForm
    redirect_authenticated_user = True