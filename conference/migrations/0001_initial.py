from django.db import migrations, models

def alter_scheduleitem_column(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # Drop constraints or indexes
        cursor.execute('ALTER TABLE conference_scheduleitem_speakers DROP CONSTRAINT FK_constraint_name;')
        cursor.execute('DROP INDEX index_name ON conference_scheduleitem_speakers;')
        # Alter the column
        cursor.execute('ALTER TABLE conference_scheduleitem_speakers ALTER COLUMN scheduleitem_id INT NOT NULL;')
        # Recreate constraints or indexes
        cursor.execute('CREATE UNIQUE INDEX index_name ON conference_scheduleitem_speakers(scheduleitem_id);')
        cursor.execute('ALTER TABLE conference_scheduleitem_speakers ADD CONSTRAINT FK_constraint_name FOREIGN KEY (scheduleitem_id) REFERENCES other_table(id);')

class Migration(migrations.Migration):

    dependencies = [
        # Add your migration dependencies here
    ]

    operations = [
        migrations.RunPython(alter_scheduleitem_column),
    ]
