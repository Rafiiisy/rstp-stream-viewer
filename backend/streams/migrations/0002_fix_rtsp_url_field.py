# Generated manually to fix RTSP URL validation

from django.db import migrations, models
import streams.models

class Migration(migrations.Migration):

    dependencies = [
        ('streams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stream',
            name='url',
            field=models.CharField(max_length=500, validators=[streams.models.validate_rtsp_url]),
        ),
    ]
