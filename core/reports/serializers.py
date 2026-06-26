from rest_framework import serializers
from .models import ASDReport, ADHDReport

# ASD: Videos + Questionnaire
class ASDVideosParentSerializer(serializers.ModelSerializer):
    risk_level = serializers.CharField(source='videos_risk_level', read_only=True)
    recommendation = serializers.CharField(source='videos_recommendation', read_only=True)

    class Meta:
        model = ASDReport
        fields = ['risk_level', 'recommendation', 'report_vid_status', 'report_vid_error', 'updated_at']

class ASDVideosDoctorSerializer(serializers.ModelSerializer):
    risk_level = serializers.CharField(source='videos_risk_level', read_only=True)
    recommendation = serializers.CharField(source='videos_recommendation', read_only=True)

    class Meta:
        model = ASDReport
        # Doctor can see the video files and the AI response from the videos
        fields = ['motion_video', 'emotion_video', 'questionnaire_answers',
                  'videos_ai_response', 'risk_level', 'recommendation',
                  'report_vid_status', 'report_vid_error', 'updated_at']

# ASD: Physiology page
class ASDPhysiologyParentSerializer(serializers.ModelSerializer):
    risk_level = serializers.CharField(source='physiology_risk_level', read_only=True)
    recommendation = serializers.CharField(source='physiology_recommendation', read_only=True)

    class Meta:
        model = ASDReport
        fields = ['risk_level', 'recommendation', 'report_phy_status', 'report_phy_error', 'updated_at']

class ASDPhysiologyDoctorSerializer(serializers.ModelSerializer):
    risk_level = serializers.CharField(source='physiology_risk_level', read_only=True)
    recommendation = serializers.CharField(source='physiology_recommendation', read_only=True)
    
    class Meta:
        model = ASDReport
        fields = ['eeg_vhdr', 'eeg_vmrk', 'eeg_data', 'physiology_ai_response',
                  'risk_level', 'recommendation',
                  'report_phy_status', 'report_phy_error', 'updated_at']

# ADHD
class ADHDReportParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADHDReport
        fields = ['risk_level', 'recommendation', 'report_status', 'report_error', 'updated_at']

class ADHDReportDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADHDReport
        fields = ['eeg_file', 'ai_full_response', 'risk_level', 'recommendation',
                  'report_status', 'report_error', 'updated_at']