from django import forms
from .models import Order
from accounts.models import Address


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('COD', 'Cash on Delivery (Pay when product arrives)'),
        ('ONLINE', 'Online Payment / Debit Card / UPI (Simulation)'),
    )

    selected_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        widget=forms.RadioSelect
    )

    # New Address fields if user chooses to enter a new one
    use_new_address = forms.BooleanField(required=False, initial=False)
    full_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}))
    address_line_1 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Flat, House No., Building'}))
    address_line_2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, Area, Landmark (Optional)'}))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}))
    postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit PIN code'}))
    country = forms.CharField(max_length=100, initial='India', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    save_address = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Payment
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        initial='COD',
        widget=forms.RadioSelect
    )

    # Online Card simulation inputs (optional)
    card_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name on Card'}))
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXX XXXX XXXX XXXX'}))
    card_expiry = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}))

    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional delivery instructions, notes...'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['selected_address'].queryset = Address.objects.filter(user=user)
            default_addr = Address.objects.filter(user=user, is_default=True).first()
            if default_addr:
                self.fields['selected_address'].initial = default_addr.id

    def clean(self):
        cleaned_data = super().clean()
        selected_address = cleaned_data.get('selected_address')
        use_new_address = cleaned_data.get('use_new_address')

        if not selected_address or use_new_address:
            # Must have new address fields
            required_fields = ['full_name', 'phone', 'address_line_1', 'city', 'state', 'postal_code']
            for f in required_fields:
                if not cleaned_data.get(f):
                    self.add_error(f, "This field is required for the delivery address.")

        payment_method = cleaned_data.get('payment_method')
        if payment_method == 'ONLINE':
            card_number = cleaned_data.get('card_number')
            if not card_number:
                self.add_error('card_number', "Please enter card number for online payment simulation.")

        return cleaned_data


class OrderCancelForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please describe reason for cancellation...'}),
        required=True
    )
