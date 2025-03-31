from django import forms
from .models import StorefrontConfiguration, DeliveryPartner, Store


class StorefrontConfigurationForm(forms.ModelForm):
    class Meta:
        model = StorefrontConfiguration
        fields = [
            'basket_charge_type',
            'basket_charge',
            'delivery_charge_per_km',
            'threshold_distance_km',
            'additional_charge_per_km',
            'maximum_distance_km',
        ]
        # add tailwind styling to the fields
        widgets = {
            'basket_charge_type': forms.Select(attrs={'class': 'form-control border p-2 rounded'}),
            'basket_charge': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
            'delivery_charge_per_km': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
            'threshold_distance_km': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
            'additional_charge_per_km': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
            'maximum_distance_km': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
        }


# class DeliveryPartnerForm(forms.ModelForm):
#     class Meta:
#         model = DeliveryPartner
#         fields = ['name', 'is_active']
#         # add tailwind styling to the widgets
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control border p-2 rounded'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-control border p-2 rounded'}),
#         }
from django import forms
from .models import DeliveryPartner


class DeliveryPartnerForm(forms.ModelForm):
    class Meta:
        model = DeliveryPartner
        fields = ['name', 'settlement_bank', 'account_number', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control border p-2 rounded'}),
            'settlement_bank': forms.Select(attrs={
                'class': 'form-control border p-2 rounded'}),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control border p-2 rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control border p-2 rounded'}),
        }
        labels = {
            'name': 'Partner Name',
            'settlement_bank': 'Bank Code',
            'account_number': 'Account Number',
            'is_active': 'Active',
        }

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['business_name', 'settlement_bank', 'account_number', 'percentage_charge', 'description']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control border p-2 rounded'}),
            'settlement_bank': forms.Select(attrs={'class': 'form-control border p-2 rounded'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control border p-2 rounded'}),
            'percentage_charge': forms.NumberInput(attrs={'class': 'form-control border p-2 rounded'}),
            'description': forms.Textarea(attrs={'class': 'form-control border p-2 rounded'}),
        }
        labels = {
            'business_name': 'Business Name',
            'settlement_bank': 'Settlement Bank Code',
            'account_number': 'Account Number',
            'percentage_charge': 'Percentage Charge',
            'description': 'Description',
        }
