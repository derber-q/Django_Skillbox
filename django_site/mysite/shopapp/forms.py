from django import forms
from django.core import validators
from django.contrib.auth.models import (Group)

from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "prise", "description", "discount", "preview"
    images = forms.ImageField(
        widget=forms.ClearableFileInput #(attrs={"multiple": True})
    )

    # class ProductForm(forms.Form):
        # name = forms.CharField(max_length=100)
        # prise = forms.DecimalField(min_value=1, max_value=1000000, decimal_places=2)
        # description = forms.CharField(
        #     label='Product',
        #     widget=forms.Textarea(attrs={'rows': 5, "cols": 30}),
        # validators=[validators.RegexValidator(
        #     regex=r'great',
        #     message='Field must contain word "great"'
        #     )],
        # )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "delivery_adress", "products", "promocode", "user",

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "name",

class CSVImportForm(forms.Form):
    csv_file = forms.FileField()