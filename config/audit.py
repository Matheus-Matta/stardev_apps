# core/audit.py (por ex.)
from django.dispatch import receiver
from auditlog.signals import post_log
from auditlog.models import LogEntry

@receiver(post_log)
def attach_account_to_log(sender, instance, action, log_entry: LogEntry|None, **kwargs):
    if not log_entry:
        return
    account_id = getattr(instance, "Account_id", None)
    account = getattr(instance, "Account", None)
    if account_id or account:
        ad = (log_entry.additional_data or {}) | {
            "account_id": str(account_id) if account_id else None,
            "account_name": getattr(account, "name", None),
        }
        log_entry.additional_data = {k: v for k, v in ad.items() if v is not None}
        log_entry.save(update_fields=["additional_data"])
