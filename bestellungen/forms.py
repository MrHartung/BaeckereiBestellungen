"""
Forms for the bestellungen app.
"""

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail

from .models import CustomUser


class RegistrationForm(UserCreationForm):
    """Form for user registration."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "E-Mail-Adresse"}
        ),
    )

    first_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Vorname"}
        ),
    )

    last_name = forms.CharField(
        required=True,
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nachname"}
        ),
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Benutzername"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Passwort (min. 10 Zeichen)"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Passwort bestätigen"}
        )

    def save(self, commit=True):
        """Save user and send verification email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            self.send_verification_email(user)

        return user

    def send_verification_email(self, user):
        """Send verification email to user."""
        token = user.generate_verification_token()

        # In development, use localhost; in production use actual domain
        base_url = (
            settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "localhost:8000"
        )
        if not base_url.startswith("http"):
            base_url = f"http://{base_url}"

        verification_url = f"{base_url}/verify-email/{token}/"

        message = f"""
Hallo {user.first_name},

vielen Dank für Ihre Registrierung!

Bitte verifizieren Sie Ihre E-Mail-Adresse, indem Sie auf folgenden Link klicken:
{verification_url}

Falls Sie sich nicht registriert haben, ignorieren Sie diese E-Mail.

Mit freundlichen Grüßen
Ihr Bäckerei-Team
        """

        send_mail(
            "E-Mail-Adresse bestätigen",
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class LoginForm(forms.Form):
    """Form for user login."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "E-Mail-Adresse"}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Passwort"}
        )
    )
