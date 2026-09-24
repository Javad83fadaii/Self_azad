from django.db import migrations, models


LEGACY_CONSTRAINT_NAME = "unique_active_student_reservation_per_day"


def remove_legacy_partial_constraint(apps, schema_editor):
    Reservation = apps.get_model("reservations", "Reservation")
    table_name = Reservation._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        constraints = schema_editor.connection.introspection.get_constraints(cursor, table_name)

    if LEGACY_CONSTRAINT_NAME not in constraints:
        return

    legacy_constraint = models.UniqueConstraint(
        fields=["student", "reservation_date"],
        condition=models.Q(status="RESERVED"),
        name=LEGACY_CONSTRAINT_NAME,
    )
    schema_editor.remove_constraint(Reservation, legacy_constraint)


def populate_active_reservation_date(apps, schema_editor):
    Reservation = apps.get_model("reservations", "Reservation")
    Reservation.objects.filter(status="RESERVED").update(
        active_reservation_date=models.F("reservation_date")
    )
    Reservation.objects.exclude(status="RESERVED").update(active_reservation_date=None)


class Migration(migrations.Migration):
    dependencies = [
        ("reservations", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    remove_legacy_partial_constraint,
                    reverse_code=migrations.RunPython.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name="reservation",
                    name=LEGACY_CONSTRAINT_NAME,
                ),
            ],
        ),
        migrations.AddField(
            model_name="reservation",
            name="active_reservation_date",
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.RunPython(
            populate_active_reservation_date,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="reservation",
            constraint=models.UniqueConstraint(
                fields=("student", "active_reservation_date"),
                name="unique_active_student_reservation_date",
            ),
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(
                fields=["meal_schedule", "status"],
                name="rsv_sched_status_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="reservation",
            index=models.Index(
                fields=["student", "reservation_date"],
                name="reservation_student_date_idx",
            ),
        ),
    ]
