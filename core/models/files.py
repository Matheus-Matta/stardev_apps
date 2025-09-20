# account/models_files.py
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from .account import Account
from auditlog.registry import auditlog


def files_upload_path(instance, filename):
    """
    Caminho final do upload.
    Usa o label (ou gera um) e o ID da Account para manter a organização.
    Ex.: accounts/<account_id>/files/<label>/<arquivo.ext>
    """
    name = f'{instance.Account_id}_{filename}'
    return f"{name}"


class Files(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    Account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="files"
    )

    label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Gerado automaticamente se não informado."
    )

    file = models.FileField(
        upload_to=files_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            "jpg", "jpeg", "png", "webp", "gif", "svg",
            "pdf", "txt", "csv", "json", "xml", "md",
            "doc", "docx", "odt",
            "xls", "xlsx", "ods",
            "ppt", "pptx", "odp",
            "mp3", "wav", "ogg", "aac",
            "mp4", "mov", "mkv", "webm",
            "zip", "rar", "7z",
        ])],
    )

    original_name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        unique_together = ("Account", "label")

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()

        if not self.label:
            self.label = f"file-{uuid.uuid4().hex[:12]}"

        if self.file and not self.original_name:
            self.original_name = getattr(self.file, "name", None)

        super().save(*args, **kwargs)

    def __str__(self):
        who = getattr(self.Account, "slug", self.Account_id)
        return f"{self.label or self.original_name or self.id} @ {who}"

    @property
    def url(self):
        return self.file.url if self.file else None

auditlog.register(Files)