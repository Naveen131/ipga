from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from accounts.models import User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'mobile_number',
                  'password','title', 'first_name', 'gender','user_type',
                  'last_name', 'designation', 'reg_id', 'organization_name',)

    def save(self, commit=True):
        user = super(UserCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Raw passwords are not stored, so there is no way to see "
                                                    "this user's password, but you can change the password "
                                                    "using <a href=\"../password/\">this form</a>."))

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Exclude 'username', 'first_name', and 'last_name' from the form
    #     excluded_fields = ['username', 'first_name', 'last_name']
    #     for field_name in excluded_fields:
    #         if field_name in self.fields:
    #             del self.fields[field_name]

    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.fields["password"]