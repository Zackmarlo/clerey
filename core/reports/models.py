import uuid
from django.db import models
from children.models import ChildProfile


REPORT_STATUS_CHOICES = [
    ('idle', 'Idle'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]


class ASDReport(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, related_name='asd_report')

    # ── Videos + questionnaire (Page 1) ───────────────────────
    # FileField saves the actual file to disk under media/asd_videos/
    motion_video = models.FileField(upload_to='asd_videos/motion/', null=True, blank=True)
    emotion_video = models.FileField(upload_to='asd_videos/emotion/', null=True, blank=True)
    questionnaire_answers = models.JSONField(null=True, blank=True)
    videos_ai_response = models.JSONField(null=True, blank=True)   # AI result from videos+questionnaire
    report_vid_status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='idle')
    report_vid_error = models.CharField(max_length=100, null=True, blank=True)

    # ── Physiology files (Page 2 — depends on observational probability) ──
    eeg_vhdr = models.FileField(upload_to='asd_physiology/vhdr/', null=True, blank=True)
    eeg_vmrk = models.FileField(upload_to='asd_physiology/vmrk/', null=True, blank=True)
    eeg_data = models.FileField(upload_to='asd_physiology/data/', null=True, blank=True)
    physiology_ai_response = models.JSONField(null=True, blank=True)  # AI result from physiology only
    report_phy_status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='idle')
    report_phy_error = models.CharField(max_length=100, null=True, blank=True)

    videos_risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, null=True, blank=True)
    videos_recommendation = models.TextField(null=True, blank=True)

    physiology_risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, null=True, blank=True)
    physiology_recommendation = models.TextField(null=True, blank=True)

    # ── Final combined output (set when both are done, or individually) ──
    ai_full_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        child_name = self.child.get_full_name() if hasattr(self.child, 'get_full_name') else 'Unknown'
        risk_level = self.videos_risk_level or self.physiology_risk_level or 'pending'
        return f"ASD Report — {child_name} ({risk_level})"


class ADHDReport(models.Model):
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.OneToOneField(ChildProfile, on_delete=models.CASCADE, related_name='adhd_report')
    eeg_file = models.FileField(upload_to='adhd_eeg/', null=True, blank=True)  # ← FileField here too
    ai_full_response = models.JSONField(null=True, blank=True)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    report_status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='idle')
    report_error = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        child_name = self.child.get_full_name() if hasattr(self.child, 'get_full_name') else 'Unknown'
        return f"ADHD Report — {child_name} ({self.risk_level})"
