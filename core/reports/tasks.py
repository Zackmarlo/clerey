import json
import requests as http_requests
from requests.exceptions import ConnectionError, Timeout
from celery import shared_task
from django.conf import settings
from errors.models import SystemErrorLog
from .models import ASDReport, ADHDReport


AI_SERVER_UNAVAILABLE = "AI_SERVER_UNAVAILABLE"
AI_SERVER_REQUEST_ERROR = "AI_SERVER_REQUEST_ERROR"
AI_SERVER_ERROR = "AI_SERVER_ERROR"


def _file_tuple(field_file):
    return (field_file.name.rsplit("/", 1)[-1], field_file)


def _set_report_status(report, status_field, error_field, status, error_code=None):
    setattr(report, status_field, status)
    setattr(report, error_field, error_code)
    report.save(update_fields=[status_field, error_field, "updated_at"])


def _retry_or_mark_unavailable(task, report, status_field, error_field, exc, report_type):
    if task.request.retries >= task.max_retries:
        _set_report_status(
            report,
            status_field,
            error_field,
            "failed",
            AI_SERVER_UNAVAILABLE,
        )
        return {
            "report_id": str(report.id),
            "type": report_type,
            "status": "failed",
            "error": AI_SERVER_UNAVAILABLE,
        }

    raise task.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_asd_videos_task(self, report_id):
    report = ASDReport.objects.get(id=report_id)

    try:
        with report.motion_video.open("rb") as motion_file, report.emotion_video.open("rb") as emotion_file:
            ai_response = http_requests.post(
                f"{settings.AI_SERVER_URL}/predict/observational",
                files={
                    "behavioral_video": _file_tuple(motion_file),
                    "emotion_video": _file_tuple(emotion_file),
                },
                data={"questionnaire_data": json.dumps(report.questionnaire_answers)},
                timeout=(60, 1000),
            )

        ai_response.raise_for_status()
        ai_data = ai_response.json()

        report.videos_ai_response = ai_data
        report.videos_risk_level = ai_data.get("risk_level", "low")
        report.videos_recommendation = ai_data.get("risk_message", "")
        report.report_vid_status = "completed"
        report.report_vid_error = None
        report.save(update_fields=[
            "videos_ai_response",
            "videos_risk_level",
            "videos_recommendation",
            "report_vid_status",
            "report_vid_error",
            "updated_at",
        ])

        return {
            "report_id": str(report.id),
            "type": "asd_videos",
            "status": "completed",
        }

    except (ConnectionError, Timeout) as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_CONNECTION_ERROR",
            message=str(e),
        )
        return _retry_or_mark_unavailable(
            self,
            report,
            "report_vid_status",
            "report_vid_error",
            e,
            "asd_videos",
        )

    except http_requests.RequestException as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_REQUEST_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_vid_status",
            "report_vid_error",
            "failed",
            AI_SERVER_REQUEST_ERROR,
        )
        raise

    except Exception as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_vid_status",
            "report_vid_error",
            "failed",
            AI_SERVER_ERROR,
        )
        raise


@shared_task(bind=True, max_retries=3)
def process_asd_physiology_task(self, report_id):
    report = ASDReport.objects.get(id=report_id)

    try:
        videos_ai_response = report.videos_ai_response or {}
        if videos_ai_response == {}:
            raise ValueError("videos_ai_response is empty. ASD videos must be processed before physiology files.")
        observational_probability = videos_ai_response.get('fused_probability')
        if observational_probability is None:
            raise ValueError("fused_probability is missing from videos_ai_response.")

        with report.eeg_vhdr.open("rb") as eeg_vhdr, report.eeg_vmrk.open("rb") as eeg_vmrk, report.eeg_data.open("rb") as eeg_data:
            ai_response = http_requests.post(
                f"{settings.AI_SERVER_URL}/predict/physiology",
                files={
                    "eeg_vhdr": _file_tuple(eeg_vhdr),
                    "eeg_vmrk": _file_tuple(eeg_vmrk),
                    "eeg_data": _file_tuple(eeg_data),
                },
                data={
                    "observational_probability": str(observational_probability),
                },
                timeout=(60, 1000),
            )

        ai_response.raise_for_status()
        ai_data = ai_response.json()

        report.physiology_ai_response = ai_data
        report.physiology_risk_level = ai_data.get("risk_level", "low")
        report.physiology_recommendation = ai_data.get("risk_message", "")
        report.report_phy_status = "completed"
        report.report_phy_error = None
        report.save(update_fields=[
            "physiology_ai_response",
            "physiology_risk_level",
            "physiology_recommendation",
            "report_phy_status",
            "report_phy_error",
            "updated_at",
        ])

        return {
            "report_id": str(report.id),
            "type": "asd_physiology",
            "status": "completed",
        }

    except (ConnectionError, Timeout) as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_CONNECTION_ERROR",
            message=str(e),
        )

        return _retry_or_mark_unavailable(
            self,
            report,
            "report_phy_status",
            "report_phy_error",
            e,
            "asd_physiology",
        )

    except http_requests.RequestException as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_REQUEST_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_phy_status",
            "report_phy_error",
            "failed",
            AI_SERVER_REQUEST_ERROR,
        )
        raise

    except Exception as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_phy_status",
            "report_phy_error",
            "failed",
            AI_SERVER_ERROR,
        )
        raise


@shared_task(bind=True, max_retries=3)
def process_adhd_task(self, report_id):
    report = ADHDReport.objects.get(id=report_id)

    try:
        with report.eeg_file.open("rb") as eeg_file:
            ai_response = http_requests.post(
                f"{settings.AI_SERVER_URL}/predict/adhd",
                files={"eeg_csv": _file_tuple(eeg_file)},
                timeout=(60, 1000),
            )

        ai_response.raise_for_status()
        ai_data = ai_response.json()

        report.ai_full_response = ai_data
        report.risk_level = ai_data.get("risk_level", "low")
        report.recommendation = ai_data.get("risk_message", "")
        report.report_status = "completed"
        report.report_error = None
        report.save(update_fields=[
            "ai_full_response",
            "risk_level",
            "recommendation",
            "report_status",
            "report_error",
            "updated_at",
        ])

        return {
            "report_id": str(report.id),
            "type": "adhd",
            "status": "completed",
        }

    except (ConnectionError, Timeout) as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_CONNECTION_ERROR",
            message=str(e),
        )

        return _retry_or_mark_unavailable(
            self,
            report,
            "report_status",
            "report_error",
            e,
            "adhd",
        )

    except http_requests.RequestException as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_REQUEST_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_status",
            "report_error",
            "failed",
            AI_SERVER_REQUEST_ERROR,
        )
        raise

    except Exception as e:
        SystemErrorLog.objects.create(
            error_type="AI_SERVER_ERROR",
            message=str(e),
        )
        _set_report_status(
            report,
            "report_status",
            "report_error",
            "failed",
            AI_SERVER_ERROR,
        )
        raise
