from django.db import models
import uuid

class SystemErrorLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    error_type = models.CharField(max_length=100)
    message = models.TextField()
    traceback = models.TextField(blank=True)
    resolved_by = models.CharField(max_length=200, blank=True)
    is_resolved = models.BooleanField(default=False)
    occurred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "✓" if self.is_resolved else "✗"
        return f"[{status}] {self.error_type} — {self.occurred_at}"