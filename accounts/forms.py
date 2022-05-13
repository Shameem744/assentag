from django import forms
from .models import UserAccounts
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class UserForm(UserCreationForm):
    class Meta:
        model=UserAccounts
        fields=["email","first_name","last_name","dob","gender","phone"]
        widgets = {"dob":forms.DateTimeInput(attrs={'type':'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('dob', css_class='form-group col-md-3 mb-0'),
                Column('gender', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-0'),
                Column('password2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Sign Up')
        )

class UpdateForm(UserChangeForm):
    class Meta:
        model=UserAccounts
        fields=["first_name","last_name","phone"]