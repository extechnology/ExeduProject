from datetime import timedelta
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Application', '0022_certificate_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batches',
            name='time_end',
        ),
        migrations.AddField(
            model_name='batches',
            name='batch_start_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='batches',
            name='duration',
            field=models.DurationField(blank=True, default=timedelta, null=True),  # ✅ fixed
        ),
        migrations.AddField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='start_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Application.tutorname'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bach_number',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Application.batches'),
        ),
    ]
