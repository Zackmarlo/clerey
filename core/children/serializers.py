from rest_framework import serializers
from .models import ChildProfile, DoctorChildAccess
from users.models import User
from datetime import date
from users.validators import validate_meaningful_text, validate_person_name


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def calculate_age_months(dob):
    today = date.today()
    months = (today.year - dob.year) * 12 + today.month - dob.month
    if today.day < dob.day:
        months -= 1
    return max(months, 0)


class BasicInfoSerializer(serializers.Serializer):
    """Validates basic_info JSONB field structure"""
    full_name = serializers.CharField(max_length=200, required=True)
    date_of_birth = serializers.DateField(required=True)
    age = serializers.IntegerField(min_value=0, required=True)
    gender = serializers.ChoiceField(choices=['male', 'female'], required=True)
    birth_order = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_full_name(self, value):
        return validate_person_name(value)

    def validate_birth_order(self, value):
        return validate_meaningful_text(value, "Birth order", allow_blank=True)


class DevMilestonesSerializer(serializers.Serializer):
    """Validates dev_milestones JSONB field structure"""
    age_of_fw = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    age_of_sw = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    lost_skills = serializers.BooleanField(required=False, allow_null=True)
    speech_level = serializers.ChoiceField(
        choices=['non-verbal', 'single words', 'short sentences', 'full sentences'],
        required=False,
        allow_null=True
    )
    gestures_use = serializers.IntegerField(min_value=0, required=False, allow_null=True)


class MedHistorySerializer(serializers.Serializer):
    """Validates med_history JSONB field structure"""
    diagnosed = serializers.ChoiceField(
        choices=['none', 'ASD', 'speech_delay', 'other'],
        required=False,
        allow_null=True
    )
    hear_problem = serializers.BooleanField(required=False, allow_null=True)
    vision_problem = serializers.BooleanField(required=False, allow_null=True)
    fam_history = serializers.ChoiceField(
        choices=['yes', 'no', 'not sure'],
        required=False,
        allow_null=True
    )


class BehaviorSerializer(serializers.Serializer):
    """Validates behavior JSONB field structure"""
    energy_level = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    sensitive_level = serializers.IntegerField(min_value=0, required=False, allow_null=True)


class ChildProfileSerializer(serializers.ModelSerializer):
    """Main serializer for ChildProfile with nested validation"""
    basic_info = BasicInfoSerializer(required=False, allow_null=True)
    dev_milestones = DevMilestonesSerializer(required=False, allow_null=True)
    med_history = MedHistorySerializer(required=False, allow_null=True)
    behavior = BehaviorSerializer(required=False, allow_null=True)

    class Meta:
        model = ChildProfile
        fields = [
            'id', 'child_id', 'basic_info', 'dev_milestones', 'med_history', 'behavior',
            'clinic_note', 'eeg_history', 'created_by', 'created_at',
        ]
        read_only_fields = ['child_id', 'created_by', 'created_at']

    def validate_basic_info(self, value):
        """Validate basic_info structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("basic_info must be a dictionary")
        
        # Ensure date_of_birth is always stored as a plain string inside JSONB
        if value and 'date_of_birth' in value:
            if isinstance(value['date_of_birth'], date):
                value['date_of_birth'] = value['date_of_birth'].isoformat()

        # Validate that age matches date_of_birth if both are provided
        if value and 'age' in value:
            dob = value.get("date_of_birth")
            age = value.get("age")

            if isinstance(dob, str):
                dob = date.fromisoformat(dob)

            expected_age = calculate_age(dob)

            if age != expected_age:
                raise serializers.ValidationError({
                    "basic_info": {
                        "age": f"Age must match date_of_birth. Expected age is {expected_age}."
                    }
                })

        return value

    def validate_dev_milestones(self, value):
        """Validate dev_milestones structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("dev_milestones must be a dictionary")
        
        # Validate that developmental milestones ages are not greater than child age
        if value and 'age_of_fw' in value and 'age_of_sw' in value:
            age_of_fw = value.get('age_of_fw')
            age_of_sw = value.get('age_of_sw')
            dob = self.initial_data.get('basic_info', {}).get('date_of_birth')
            if isinstance(dob, str):
                dob = date.fromisoformat(dob)
            
            child_age_months = calculate_age_months(dob)
            if age_of_fw is not None and age_of_fw > child_age_months:
                raise serializers.ValidationError({
                    "dev_milestones": {
                        "age_of_fw": "Age of first word cannot be greater than child age."
                    }
                })

            if age_of_sw is not None and age_of_sw > child_age_months:
                raise serializers.ValidationError({
                    "dev_milestones": {
                        "age_of_sw": "Age of start walking cannot be greater than child age."
                    }
                })

        return value

    def validate_med_history(self, value):
        """Validate med_history structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("med_history must be a dictionary")
        return value

    def validate_behavior(self, value):
        """Validate behavior structure"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("behavior must be a dictionary")
        return value

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        json_fields = ['basic_info', 'dev_milestones', 'med_history', 'behavior']

        for field in json_fields:
            if field in validated_data and validated_data[field] is not None:
                current_value = getattr(instance, field) or {}
                new_value = validated_data[field] or {}
                validated_data[field] = {**current_value, **new_value}

        return super().update(instance, validated_data)


class DoctorEmailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'last_login']

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class SendChildAccessSerializer(serializers.Serializer):
    doctor_email = serializers.EmailField()

    def validate_doctor_email(self, value):
        try:
            doctor = User.objects.get(email=value, role='doctor', is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active doctor found with this email.")

        self.context['doctor'] = doctor
        return value


class ChildAccessSerializer(serializers.Serializer):
    """Serializer for doctor access credentials"""
    child_id = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=255)


class ClinicNoteSerializer(serializers.ModelSerializer):
    """Serializer for updating clinic notes only"""
    class Meta:
        model = ChildProfile
        fields = ['clinic_note']
