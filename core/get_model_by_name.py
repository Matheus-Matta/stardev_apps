# views.py
from django.http import Http404
from django.apps import apps

def get_model_by_name(model_name: str):
    if "." in model_name:
        try:
            return apps.get_model(model_name)
        except LookupError:
            raise Http404("Modelo não encontrado.")
    candidates = [m for m in apps.get_models() if m.__name__.lower() == model_name.lower()]
    if not candidates:
        raise Http404("Modelo não encontrado.")
    if len(candidates) > 1:
        raise Http404("Modelo ambíguo. Use app_label.ModelName.")
    return candidates[0]