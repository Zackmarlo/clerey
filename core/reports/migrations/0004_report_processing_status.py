from django.db import migrations, models


STATUS_CHOICES = [
    ('idle', 'Idle'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_split_asd_risk_recommendation'),
    ]

    operations = [
        migrations.AddField(
            model_name='asdreport',
            name='report_vid_status',
            field=models.CharField(choices=STATUS_CHOICES, default='idle', max_length=20),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='report_vid_error',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='report_phy_status',
            field=models.CharField(choices=STATUS_CHOICES, default='idle', max_length=20),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='report_phy_error',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='adhdreport',
            name='report_status',
            field=models.CharField(choices=STATUS_CHOICES, default='idle', max_length=20),
        ),
        migrations.AddField(
            model_name='adhdreport',
            name='report_error',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
