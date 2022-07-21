from django import forms
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

User = get_user_model()

SELLER_CHOICES = (
    ('B', 'Bijas',),
    ('A', 'Ahammedunny')

)


class Login(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    email = forms.EmailField(widget=forms.TextInput())
    password_one = forms.CharField(widget=forms.PasswordInput())
    password_two = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = self.cleaned_data
        password_one = self.cleaned_data_data.get['password_first']
        password_two = self.cleaned_data_data.get['password_again']
        if password_one != password_two:
            raise forms.ValidationError("password doesnt match")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get['username']
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("username exists")
        return username

    def clean_email(self):
        email_address = self.cleaned_data['email']
        qs = User.objects.filter(email=email_address)
        if qs.exists():
            raise forms.ValidationError("Email is already registered")
        return email_address


PAYMENT_CHOICES = (
    ('S', 'stripe'),
    ('P', 'pay_pal'),
)


class CheckOut(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(required=False,
                                                                              widget=CountrySelectWidget(attrs={
                                                                                  'class': 'custom-select d-block w-100'
                                                                              })
                                                                              )
    shipping_pin_code = forms.CharField(required=False
                                        )

    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(required=False,
                                                                             widget=CountrySelectWidget(attrs={
                                                                                 'class': 'custom-select d-block w-100'
                                                                             })
                                                                             )
    billing_pin_code = forms.CharField(required=False
                                       )
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)
    payment_method = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class Contact(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input2', 'type': 'text', 'name': 'name'}))
    number = forms.CharField(widget=forms.TextInput(attrs={'class': 'input2', 'type': 'text', 'name': "number"}))
    message = forms.CharField(widget=forms.Textarea(attrs={

        'class': 'input2', 'type': 'text', 'name': 'email'}))


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Promo code', 'aria-label': 'Recipients username',
               'aria-describedby': 'basic-addon2'}))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField()
    email = forms.EmailField()


class Googlephishing(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'id': 'user_name', 'type': 'text', 'class': 'validate'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'pass_word', 'type': 'password', 'class': 'validate'}))


class PocketSale(forms.Form):
    name = forms.CharField()
    name_of_seller = forms.CharField()
    price = forms.IntegerField()
    quantity = forms.IntegerField()
    discount = forms.IntegerField()
    discount_description = forms.CharField()
    amount = forms.BooleanField()
