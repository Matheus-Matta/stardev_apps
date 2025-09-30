from rest_framework import serializers
from core.models import Customer, CustomerAddress, CustomerContact
from .address import AddressSerializer
from .contact import ContactSerializer
from .business import BusinessMiniSerializer

class CustomerAddressThroughSerializer(serializers.ModelSerializer):
    address    = AddressSerializer(read_only=True)
    address_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CustomerAddress
        fields = [
            "id",
            "address", "address_id",  
            "role", "is_primary",
            "valid_from", "valid_until",
            "label", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "address", "created_at", "updated_at"]

class CustomerContactThroughSerializer(serializers.ModelSerializer):
    contact    = ContactSerializer(read_only=True)
    contact_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CustomerContact
        fields = [
            "id",
            "contact", "contact_id",   
            "is_primary", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "contact", "created_at", "updated_at"]


class CustomerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "full_name", "document", "is_active"]
        read_only_fields = fields


class CustomerSerializer(serializers.ModelSerializer):
    preferred_store     = BusinessMiniSerializer(read_only=True)
    preferred_store_id  = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    addresses_links = CustomerAddressThroughSerializer(source="customer_addresses", many=True, read_only=True)
    contacts_links  = CustomerContactThroughSerializer(source="customer_contacts",  many=True, read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "customer_type", "full_name", "fantasy_name",
            "document", "state_registration", "municipal_registration",
            "primary_email", "primary_phone",
            "payment_term", "credit_limit", "is_blocked", "notes_erp",
            "loyalty_code", "preferred_store", "preferred_store_id",
            "marketing_opt_in", "birth_date",
            "delivery_notes",
            "delivery_time_window_start", "delivery_time_window_end",
            "requires_scheduling", "unloading_requirements",
            "addresses_links",
            "contacts_links",
            "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "preferred_store", "addresses_links", "contacts_links",
            "created_at", "updated_at",
        ]

    def _inject_tenant(self, validated: dict):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated["Account"] = account

    def _apply_store_fk(self, instance: Customer, validated: dict):
        store_id = validated.pop("preferred_store_id", serializers.empty)
        if store_id is not serializers.empty:
            instance.preferred_store_id = store_id

    def _sync_addresses(self, instance: Customer, items: list[dict]):
        """
        Espera uma lista de dicts com: address_id (obrigatório), role?, is_primary?, valid_from?, valid_until?, label?, notes?
        Estratégia simples: apaga e recria (idempotente via unique constraint).
        """
        CustomerAddress.objects.filter(customer=instance).delete()
        bulk = []
        for it in items or []:
            aid = it.get("address_id")
            if not aid:
                continue
            bulk.append(CustomerAddress(
                customer=instance,
                address_id=aid,
                role=it.get("role") or CustomerAddress._meta.get_field("role").default,
                is_primary=bool(it.get("is_primary", False)),
                valid_from=it.get("valid_from"),
                valid_until=it.get("valid_until"),
                label=it.get("label"),
                notes=it.get("notes"),
            ))
        if bulk:
            CustomerAddress.objects.bulk_create(bulk)

    def _sync_contacts(self, instance: Customer, items: list[dict]):
        """
        Espera lista de dicts com: contact_id (obrigatório), is_primary?, notes?
        """
        CustomerContact.objects.filter(customer=instance).delete()
        bulk = []
        for it in items or []:
            cid = it.get("contact_id")
            if not cid:
                continue
            bulk.append(CustomerContact(
                customer=instance,
                contact_id=cid,
                is_primary=bool(it.get("is_primary", False)),
                notes=it.get("notes"),
            ))
        if bulk:
            CustomerContact.objects.bulk_create(bulk)


    def create(self, validated):
        self._inject_tenant(validated)

        addresses_payload = self.initial_data.get("addresses_links") or self.initial_data.get("addresses") or []
        contacts_payload  = self.initial_data.get("contacts_links")  or self.initial_data.get("contacts")  or []

        obj = Customer(
            Account                   = validated.get("Account"),
            customer_type             = validated.get("customer_type"),
            full_name                 = validated.get("full_name"),
            fantasy_name              = validated.get("fantasy_name"),
            document                  = validated.get("document"),
            state_registration        = validated.get("state_registration"),
            municipal_registration    = validated.get("municipal_registration"),
            primary_email             = validated.get("primary_email"),
            primary_phone             = validated.get("primary_phone"),
            payment_term              = validated.get("payment_term"),
            credit_limit              = validated.get("credit_limit", 0),
            is_blocked                = validated.get("is_blocked", False),
            notes_erp                 = validated.get("notes_erp"),
            loyalty_code              = validated.get("loyalty_code"),
            marketing_opt_in          = validated.get("marketing_opt_in", False),
            birth_date                = validated.get("birth_date"),
            delivery_notes            = validated.get("delivery_notes"),
            delivery_time_window_start= validated.get("delivery_time_window_start"),
            delivery_time_window_end  = validated.get("delivery_time_window_end"),
            requires_scheduling       = validated.get("requires_scheduling", False),
            unloading_requirements    = validated.get("unloading_requirements"),
            is_active                 = validated.get("is_active", True),
        )
        self._apply_store_fk(obj, validated)
        obj.save()

        # sincroniza throughs (se vierem)
        if addresses_payload:
            self._sync_addresses(obj, addresses_payload)
        if contacts_payload:
            self._sync_contacts(obj, contacts_payload)

        return obj

    def update(self, instance: Customer, validated):
        for attr in [
            "customer_type", "full_name", "fantasy_name",
            "document", "state_registration", "municipal_registration",
            "primary_email", "primary_phone",
            "payment_term", "credit_limit", "is_blocked", "notes_erp",
            "loyalty_code", "marketing_opt_in", "birth_date",
            "delivery_notes",
            "delivery_time_window_start", "delivery_time_window_end",
            "requires_scheduling", "unloading_requirements",
            "is_active",
        ]:
            if attr in validated:
                setattr(instance, attr, validated[attr])

        self._apply_store_fk(instance, validated)
        instance.save()

        if "addresses_links" in self.initial_data or "addresses" in self.initial_data:
            payload = self.initial_data.get("addresses_links") or self.initial_data.get("addresses") or []
            self._sync_addresses(instance, payload)

        if "contacts_links" in self.initial_data or "contacts" in self.initial_data:
            payload = self.initial_data.get("contacts_links") or self.initial_data.get("contacts") or []
            self._sync_contacts(instance, payload)

        return instance
