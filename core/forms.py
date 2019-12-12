from django import forms 
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENTS = (
    ('P', 'PayPal'),
    ('S', 'Stripe')

)
class checkoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Avenue sainte eugenie'
    }))
    appartement_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Appartment or suite'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
           'class': 'custom-select d-block w-100'
        }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control '
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENTS)
