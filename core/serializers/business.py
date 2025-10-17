from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from core.models import Business, BusinessType
from .address import AddressSerializer
from math import ceil

def _normalize_cnpj(value: str) -> str:
    v = (value or "").strip()
    digits = "".join(ch for ch in v if ch.isdigit())
    if len(digits) != 14:
        return v
    return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"


class BusinessTypeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ["id", "name", "is_active"]
        read_only_fields = fields


class BusinessTypeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BusinessType
        fields = [
            "id",
            "code",
            "name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "code", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            validated_data["Account"] = account
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for attr in ("name", "is_active"):
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()
        return instance


class BusinessMiniSerializer(serializers.ModelSerializer):
    business_type = BusinessTypeMiniSerializer(read_only=True)

    class Meta:
        model = Business
        fields = ["id", "code", "name", "business_type", "is_active"]
        read_only_fields = fields


class BusinessSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False, allow_null=True)
    parent = BusinessMiniSerializer(read_only=True)
    children = serializers.SerializerMethodField()
    business_type = BusinessTypeMiniSerializer(read_only=True)

    address_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    parent_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    business_type_id = serializers.UUIDField(
        write_only=True,
        required=True,
        allow_null=False,
        help_text=_("ID do tipo de negócio vinculado ao Account atual."),
    )

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "code",
            "name",
            "cnpj",
            "business_type",
            "business_type_id",
            "is_active",
            "address",
            "address_id",
            "parent",
            "parent_id",
            "children",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "parent",
            "children",
            "business_type",
            "created_at",
            "updated_at",
        ]
        
    def get_children(self, obj: Business):
        """
        Retorna os filhos paginados:
        {
          "items": [...],
          "total": 123,
          "page": 1,
          "page_size": 5,
          "total_pages": 25,
          "has_next": true,
          "has_prev": false
        }
        Parâmetros aceitos em query:
          - children_page (default 1)
          - children_page_size (default 5, máx 100)
          - OU (opcionais) children_limit / children_offset (prioridade menor)
        """
        request = self.context.get("request")
        qp = getattr(request, "query_params", {}) if request else {}

        try:
            page = int(qp.get("children_page", 1) or 1)
        except Exception:
            page = 1

        try:
            page_size = int(qp.get("children_page_size", 5) or 5)
        except Exception:
            page_size = 5

        page = max(1, page)
        page_size = max(1, min(100, page_size))

        total = obj.children.count()
        total_pages = max(1, ceil(total / page_size)) if total else 1
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * page_size
        limit = page_size

        if "children_limit" in qp or "children_offset" in qp:
            try:
                limit = int(qp.get("children_limit", limit))
                offset = int(qp.get("children_offset", offset))
                limit = max(1, min(100, limit))
                offset = max(0, offset)
                page = (offset // limit) + 1
                page_size = limit
                total_pages = max(1, ceil(total / page_size)) if total else 1
            except Exception:
                pass

        qs = obj.children.all().order_by("created_at")[offset : offset + limit]
        items = BusinessMiniSerializer(qs, many=True, context=self.context).data

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
        
    def validate_business_type_id(self, value):
        """Valida que o BusinessType pertence ao Account do request."""
        request = self.context.get("request")
        account = getattr(request, "account", None) if request else None
        if account:
            try:
                BusinessType.objects.get(id=value, Account=account)
            except BusinessType.DoesNotExist:
                raise serializers.ValidationError(
                    _("BusinessType must belong to the current Account.")
                )
        return value

    def validate_parent_id(self, value):
        """Valida que o parent pertence ao mesmo Account (opcional)."""
        if value:
            request = self.context.get("request")
            account = getattr(request, "account", None) if request else None
            if account:
                try:
                    Business.objects.get(id=value, Account=account)
                except Business.DoesNotExist:
                    raise serializers.ValidationError(
                        _("Parent Business must belong to the current Account.")
                    )
        return value

    def validate_cnpj(self, value: str) -> str:
        return _normalize_cnpj(value)

    def _set_foreign_keys(self, instance: Business, validated_data: dict) -> None:
        """
        Aplica IDs de FKs no instance, removendo-os do validated_data.
        Obs.: address_id será tratado antes (para suportar address aninhado).
        """
        for field_name, fk_field in [
            ("parent_id", "parent_id"),
            ("business_type_id", "business_type_id"),
        ]:
            value = validated_data.pop(field_name, serializers.empty)
            if value is not serializers.empty:
                setattr(instance, fk_field, value)

    def _extract_address_inputs(self, validated_data: dict):
        """
        Retira 'address' (dict) e 'address_id' do validated_data para evitar sobrescritas.
        Retorna (address_data, address_id).
        """
        address_data = validated_data.pop("address", None)
        address_id = validated_data.pop("address_id", serializers.empty)
        return address_data, address_id

    def _create_or_update_address(self, existing_address, address_data):
        """
        Cria/atualiza Address via AddressSerializer usando o mesmo context (request/account).
        - existing_address: instância Address ou None
        - address_data: dict
        Retorna a instância Address resultante.
        """
        if existing_address:
            ser = AddressSerializer(
                instance=existing_address,
                data=address_data,
                partial=True,
                context=self.context,
            )
        else:
            ser = AddressSerializer(
                data=address_data,
                context=self.context,
            )
        ser.is_valid(raise_exception=True)
        return ser.save()

    def create(self, validated_data):
        try:
            request = self.context.get("request")
            account = getattr(request, "account", None) if request else None
            if account:
                validated_data["Account"] = account

            address_data, address_id = self._extract_address_inputs(validated_data)

            if (
                address_data
                and address_id is not serializers.empty
                and address_id is not None
            ):
                raise serializers.ValidationError(
                    {"address": _("Use either 'address' or 'address_id', not both.")}
                )

            instance = Business(
                Account=validated_data.pop("Account"),
                name=validated_data.pop("name"),
                cnpj=validated_data.pop("cnpj"),
                is_active=validated_data.get("is_active", True),
            )

            self._set_foreign_keys(instance, validated_data)

            if address_data:
                addr = self._create_or_update_address(
                    existing_address=None, address_data=address_data
                )
                instance.address_id = addr.id
            elif address_id is not serializers.empty:
                instance.address_id = address_id  

            instance.save()
            return instance
        except Exception as e:
            print(">>> BusinessSerializer.create ERROR:", e)
            raise e

    def update(self, instance: Business, validated_data):
        address_data, address_id = self._extract_address_inputs(validated_data)

        for attr in ("name", "cnpj", "is_active"):
            if attr in validated_data:
                setattr(instance, attr, validated_data.pop(attr))

        self._set_foreign_keys(instance, validated_data)

        if address_data is not None:
            existing = getattr(instance, "address", None)
            addr = self._create_or_update_address(
                existing_address=existing, address_data=address_data
            )
            if not instance.address_id or instance.address_id != addr.id:
                instance.address_id = addr.id
        elif address_id is not serializers.empty:
            instance.address_id = address_id

        instance.save()
        return instance
