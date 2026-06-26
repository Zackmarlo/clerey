from django.db import migrations, models


def move_old_asd_risk_data(apps, schema_editor):
    ASDReport = apps.get_model('reports', 'ASDReport')

    for report in ASDReport.objects.all():
        if not report.videos_risk_level:
            report.videos_risk_level = report.risk_level

        if not report.videos_recommendation:
            report.videos_recommendation = report.recommendation

        physiology_response = report.physiology_ai_response or {}

        if not report.physiology_risk_level:
            report.physiology_risk_level = physiology_response.get('risk_level')

        if not report.physiology_recommendation:
            report.physiology_recommendation = physiology_response.get('risk_message')

        report.save(update_fields=[
            'videos_risk_level',
            'videos_recommendation',
            'physiology_risk_level',
            'physiology_recommendation',
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_asdreport_eeg_data_asdreport_eeg_vhdr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='asdreport',
            name='videos_risk_level',
            field=models.CharField(
                blank=True,
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='videos_recommendation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='physiology_risk_level',
            field=models.CharField(
                blank=True,
                choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='physiology_recommendation',
            field=models.TextField(blank=True, null=True),
        ),

        migrations.RunPython(move_old_asd_risk_data, migrations.RunPython.noop),

        migrations.RemoveField(
            model_name='asdreport',
            name='physiology_file',
        ),
        migrations.RemoveField(
            model_name='asdreport',
            name='risk_level',
        ),
        migrations.RemoveField(
            model_name='asdreport',
            name='recommendation',
        ),
    ]
