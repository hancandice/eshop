from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ("Stripe", "Stripe"),
    ("PayPal", "PayPal"),
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(label="Address")
    apartment_address = forms.CharField(required=False)
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': "custom-select d-block w-100"
    }))
    zip = forms.CharField()
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': "Promo code",
        'aria-label': "Recipient's username",
        'aria-describedby': "basic-addon2",
    }))