"""Records that the wallet foreign key now points at the public id.

State only: the column was already rewritten by games.0015, which had to do it
in the same statement batch as the primary key swap.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("games", "0015_wallet_credentials"),
        ("r_place", "0009_alter_canvas_options_cell_wallet"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name="cell",
                    name="wallet",
                    field=models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cells",
                        to="games.wallet",
                    ),
                ),
            ],
        ),
    ]
