from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Region, Center


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Ism", max_length=50)
    last_name = forms.CharField(label="Familiya", max_length=50)
    phone = forms.CharField(label="Telefon raqam", max_length=20)
    region = forms.ModelChoiceField(label="Hudud (viloyat/tuman)", queryset=Region.objects.all())

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "phone", "region", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.phone = self.cleaned_data["phone"]
        user.region = self.cleaned_data["region"]
        if commit:
            user.save()
        return user


class CenterSignUpForm(UserCreationForm):
    center_name = forms.CharField(label="Markaz nomi", max_length=150)
    phone = forms.CharField(label="Telefon raqam", max_length=20)
    region = forms.ModelChoiceField(label="Hudud (viloyat/tuman)", queryset=Region.objects.all())
    address = forms.CharField(label="Manzil", max_length=255, required=False)

    class Meta:
        model = User
        fields = ["username", "phone", "region", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CENTER
        user.phone = self.cleaned_data["phone"]
        user.region = self.cleaned_data["region"]
        if commit:
            user.save()
            Center.objects.create(
                owner=user,
                name=self.cleaned_data["center_name"],
                region=self.cleaned_data["region"],
                address=self.cleaned_data.get("address", ""),
            )
        return user
