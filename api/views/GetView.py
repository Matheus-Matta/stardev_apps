# api/views.py
from django.apps import apps as django_apps
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class GetView(APIView):
    """
    GET /api/<model_name>/<pk>/
    Protegido por JWT e por tenant: só retorna se o objeto pertencer ao Account do usuário.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, model_name: str, pk: str):
        try:
            model_cls = resolve_model(model_name)
        except Exception as e:
            print("[GET VIEW] Model não encontrado:", e)
            return Response(
                sign_payload({"data": {"ok": False, "detail": "Model não encontrado"}}),
                status=status.HTTP_404_NOT_FOUND,
            )

        qs = model_cls.objects.all()
        account_field = request.account or None
        if account_field:
            user_account_id = getattr(request.user, "Account_id", None)
            if user_account_id is None:
                return Response(
                    sign_payload({"data": {"ok": False, "detail": "Usuário sem conta vinculada."}}),
                    status=status.HTTP_403_FORBIDDEN,
                )
            qs = qs.filter(**{f"{account_field}_id": user_account_id})

        obj = get_object_or_404(qs, pk=pk)

        try:
            payload = serialize_with_policy(
                obj._meta.app_label,
                obj._meta.model_name,
                obj,
            )
            return Response(payload, status=status.HTTP_200_OK)
        except Exception as e:
            print("[GET VIEW] Erro ao serializar:", e)
            return Response(
                sign_payload({"data": {"ok": False, "detail": "Erro ao serializar dados."}}),
                status=status.HTTP_400_BAD_REQUEST,
            )
