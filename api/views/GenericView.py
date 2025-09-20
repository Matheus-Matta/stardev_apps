# api/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from api.helpers import ModelHelper
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from core.throttling import AccountScopedRateThrottle
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError

class GetView(APIView):
    """
    GET /api/<model_name>/<pk>/
    Protegido por JWT e por tenant: só retorna se o objeto pertencer ao Account do usuário.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountScopedRateThrottle]
    throttle_scope = "account:1hour"
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def get(self, request, model_name: str, pk: str):
        h = ModelHelper(request)
        data = h.get_one_serialized(model_name, pk)
        if data is None:
            return Response({"ok": False, "detail": f"{model_name} não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        fields = data.get('fields')
        fields['id'] = data.get('id') or pk
        print('[GetView] fields', request.user, model_name, fields)
        return Response({"ok": True, model_name: fields}, status=status.HTTP_200_OK)
    

class PostView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountScopedRateThrottle]
    throttle_scope = "account:1hour"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request, model_name: str):
        try:
            data = request.data or request.FILES
            print('[PostView] post', request.data)
            h = ModelHelper(request)
            payload = request.data if isinstance(request.data, dict) else {}
            data = h.create_one(model_name, payload)
            if data is None:
                return Response({"ok": False, "detail": "Não foi possível criar."},
                                status=status.HTTP_400_BAD_REQUEST)
            fields = data.get('fields')
            fields['id'] = data.get('id') or ''
            print('[PostView] fields', request.user, model_name, fields)
            return Response({"ok": True, "detail": f"{model_name} criado com sucesso!", model_name: fields}, status=status.HTTP_201_CREATED)
        
        except PermissionDenied as e:
            return Response({"ok": False, "detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"ok": False, "detail": str(e.detail if hasattr(e, 'detail') else e)},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"ModelHelper.create_one: Exception creating one for model {model_name}: {str(e)}")
            return Response({"ok": False, "detail": f"Erro ao criar. {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)


class PutView(APIView):
    """
    PUT /api/<model_name>/<pk>/
    Corpo: { ...campos_do_form... }  (parcial ou completo, a depender do seu form)
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountScopedRateThrottle]
    throttle_scope = "account:1hour"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def put(self, request, model_name: str, pk: str):
        try:
            print('[PutView] post', request.data)
            h = ModelHelper(request)
            payload = request.data if isinstance(request.data, dict) else {}
            data = h.update_one(model_name, pk, payload)
            if data is None:
                return Response({"ok": False, "detail": "Não encontrado"},
                                status=status.HTTP_404_NOT_FOUND)
            if "errors" in data:
                return Response({"ok": False, "errors": data["errors"]},
                                status=status.HTTP_400_BAD_REQUEST)
            fields = data.get('fields')
            fields['id'] = data.get('id') or pk
            print('[PutView] fields', request.user, model_name, pk, fields)
            return Response({"ok": True, "detail": f"{model_name} atualizado com sucesso!", model_name: fields}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"ok": False, "detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"ok": False, "detail": f"Erro ao atualizar. {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)


class DeleteView(APIView):
    """
    DELETE /api/<model_name>/<pk>/
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AccountScopedRateThrottle]
    throttle_scope = "account:1hour"
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def delete(self, request, model_name: str, pk: str):
        try:
            h = ModelHelper(request)
            ok = h.delete_one(model_name, pk)
            if not ok:
                return Response({"ok": False, "detail": "Não encontrado"},
                                status=status.HTTP_404_NOT_FOUND)
            return Response({"ok": True, "detail": f"{model_name} deletado com sucesso!", "deleted": True}, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"ok": False, "detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"ok": False, "detail": f"Erro ao deletar. {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
