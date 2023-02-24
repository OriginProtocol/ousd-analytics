from django import forms

class SubscriberForm(forms.Form):
    email = forms.EmailField(
      label='',
      max_length=100,
      widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email', 'style': 'height:48px'}),
    )