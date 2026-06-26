from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asdreport',
            name='eeg_data',
            field=models.FileField(blank=True, null=True, upload_to='asd_physiology/data/'),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='eeg_vhdr',
            field=models.FileField(blank=True, null=True, upload_to='asd_physiology/vhdr/'),
        ),
        migrations.AddField(
            model_name='asdreport',
            name='eeg_vmrk',
            field=models.FileField(blank=True, null=True, upload_to='asd_physiology/vmrk/'),
        ),
    ]
