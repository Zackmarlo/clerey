from django.db import models
import uuid
import random
import string
from django.contrib.auth.hashers import make_password
from users.models import User

def generate_child_id():
    """Generates a unique readable ID like CHLD-A3F9X2"""
    while True:
        candidate = f"CHLD-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        if not ChildProfile.objects.filter(child_id=candidate).exists():
            return candidate

def generate_child_password():
    """Generates a random 8-character password for the child profile"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class ChildProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child_id = models.CharField(max_length=20, unique=True, default=generate_child_id)
    hashed_password = models.CharField(max_length=255)  # never store plain passwords
    clinic_note = models.TextField(blank=True, null=True)
    eeg_history = models.BooleanField(null=True, blank=True)
    
    # Basic Information Contains: full_name(str), date_of_birth(date), age(int), gender(male/female), birth_order(str)
    basic_info = models.JSONField(null=True, blank=True, default=dict)
    
    # Developmental Milestones Contains: age_of_fw(int), age_of_sw(int), lost_skills(bool), speech_level(non-verbal/single words/short sentences/full sentences), gestures_use(int)
    dev_milestones = models.JSONField(null=True, blank=True, default=dict)
    
    # Medical History Contains: diagnosed(none/ASD/speech delay/other), hear_problem(bool), vision_problem(bool), fam_history(yes/no/not sure)
    med_history = models.JSONField(null=True, blank=True, default=dict)
    
    # Behavior Contains: energy_level(int), sensitive_level(int)
    behavior = models.JSONField(null=True, blank=True, default=dict)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate and hash the password only on first creation
        if self._state.adding: # only generate on first save
            raw_password = generate_child_password()
            self.raw_password = raw_password  # temporarily hold it to show the user once
            self.hashed_password = make_password(raw_password)
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Extract full_name from basic_info JSONB field"""
        if self.basic_info and 'full_name' in self.basic_info:
            return self.basic_info['full_name']
        return f"Child {self.child_id}"

    def __str__(self):
        return f"{self.get_full_name()} ({self.child_id})"


class DoctorChildAccess(models.Model):
    """Tracks which doctors have been granted access to which child profiles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accessible_children_as_doctor')
    child = models.ForeignKey(ChildProfile, on_delete=models.CASCADE, related_name='authorized_doctors')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'child')  # prevent duplicate access rows

    def __str__(self):
        return f"Dr. {self.doctor.email} → {self.child.child_id}"