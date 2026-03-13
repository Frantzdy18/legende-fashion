from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

# ---------- SIGNUP FORM SIMPLE ----------
class SimpleSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

# ---------- SIGNUP AVEC EMAIL (EMAIL PA OBLIGATWA) ----------
class SignupWithEmailForm(UserCreationForm):
    email = forms.EmailField(required=False)  # Email pa obligatwa

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# ---------- PRODUCT FORM ----------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nom', 'description', 'prix', 'quantite', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }






class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic']  # ajoute lòt chan si bezwen
        widgets = {
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }