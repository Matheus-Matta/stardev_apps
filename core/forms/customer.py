# account/forms_customer.py
from django import forms
from core.models import Customer, CustomerAddress, CustomerContact

class CustomerForm(forms.ModelForm):
    """
    Customer:
    - exclude Account (tenant)
    - M2M (addresses/contacts) gerenciados pelas through tables; não expor aqui
    """
    class Meta:
        model = Customer
        fields = [
            "customer_type", "full_name", "fantasy_name",
            "document", "state_registration", "municipal_registration",
            "primary_email", "primary_phone",
            "payment_term", "credit_limit", "is_blocked", "notes_erp",
            "loyalty_code", "preferred_store", "marketing_opt_in", "birth_date",
            "delivery_notes",
            "delivery_time_window_start", "delivery_time_window_end",
            "requires_scheduling", "unloading_requirements",
            "is_active",
        ]

    def clean_document(self):
        v = (self.cleaned_data.get("document") or "").strip()
        return "".join(ch for ch in v if ch.isalnum()) or None


class CustomerAddressForm(forms.ModelForm):
    """
    Vínculo Customer<->Address (through):
    - não expõe Account; já vem do Customer/Address
    """
    class Meta:
        model = CustomerAddress
        fields = [
            "customer", "address",
            "role", "is_primary",
            "valid_from", "valid_until",
            "label", "notes",
        ]


class CustomerContactForm(forms.ModelForm):
    """
    Vínculo Customer<->Contact (through)
    """
    class Meta:
        model = CustomerContact
        fields = [
            "customer", "contact",
            "is_primary", "notes",
        ]
