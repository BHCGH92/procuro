from django.db import migrations

def create_default_location(apps, schema_editor):
    Location = apps.get_model('storage', 'Location')
    SubLocation = apps.get_model('storage', 'SubLocation')
    Area = apps.get_model('storage', 'Area')
    SubArea = apps.get_model('storage', 'SubArea')

    loc, _ = Location.objects.get_or_create(name="Unassigned Location")
    
    # 2. Create sub level
    sub_loc, _ = SubLocation.objects.get_or_create(
        name="Unassigned Sub Location", 
        location=loc
    )
    
    # 3. Create area level
    area, _ = Area.objects.get_or_create(
        name="Unassigned Area", 
        sub_location=sub_loc
    )
    
    # 4. Create the final "Unassigned" spot
    SubArea.objects.get_or_create(
        name="Unassigned Sub Area", 
        area=area
    )

class Migration(migrations.Migration):
    dependencies = [
        ('storage', '0002_alter_storage_id'), #
    ]

    operations = [
        migrations.RunPython(create_default_location),
    ]