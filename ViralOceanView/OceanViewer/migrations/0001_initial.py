# Generated by Django 4.1.1 on 2022-09-28 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('OceanFinder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accNbr_gb', models.CharField(blank=True, max_length=12, null=True, verbose_name='genbank accession number')),
                ('used_name', models.CharField(default='example_1', max_length=45)),
                ('isRefSeq', models.BooleanField(default=False)),
                ('prot_seq', models.TextField(default='MGG-G', verbose_name='Aligned protein sequence')),
                ('cds_seq', models.TextField(blank=True, verbose_name='CDS')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='OceanFinder.job')),
            ],
            options={
                'ordering': ['used_name'],
            },
        ),
    ]
