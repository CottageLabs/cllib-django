import importlib.resources
import re

from django.db import migrations
from django.db.migrations.operations.base import Operation


def create_operation_default_value(table_name, col_name, default_val) -> Operation:
    """

    Parameters
    ----------
    table_name
    col_name
    default_val
        remember to add '' for string value, e.g. "'default_value'"

    Returns
    -------

    """

    return migrations.RunSQL(
        (f"alter table {table_name} "
         f" alter column {col_name} "
         f" set default {default_val} "),

        (f'alter table {table_name} '
         f' alter column {col_name} '
         ' drop default '),
    )


def create_default_empty(table_name, col_names: list[str]) -> list[Operation]:
    return [
        create_operation_default_value(table_name, col_name, default_val="''")
        for col_name in col_names
    ]


def create_operation_seq(seq_name, init_val=1) -> Operation:
    return migrations.RunSQL(
        f"CREATE SEQUENCE {seq_name} start with {init_val} ",
        f"DROP SEQUENCE {seq_name}",
    )


def create_operation_add_index(index_name, table_name, fields: list) -> Operation:
    return migrations.RunSQL(
        f"create index {index_name} on {table_name} ({','.join(fields)})",
        f"DROP index {index_name}",
    )


def create_operation_zero_one_check(table_name, field_name, constraint_name):
    return migrations.RunSQL(
        f"""
alter table {table_name}
add constraint {constraint_name}
check (({field_name} = 0) OR ({field_name} = 1));
            """,
        f"""
alter table {table_name}
drop constraint {constraint_name};
        """
    )


def load_sql_by_path(module_name, path):
    return importlib.resources.files(module_name).joinpath(path).read_text()


def create_function_by_file(module_name, path) -> Operation:
    create_sql = load_sql_by_path(module_name, path)
    if fn_name := re.findall(r'create\s+(or replace)?\s*function (\w+)\(', create_sql):
        fn_name = fn_name[0]
    else:
        raise ValueError(f'function name not found [{module_name}][{path}]')

    return migrations.RunSQL(
        create_sql,
        f"DROP function {fn_name}",
    )


def update_function_by_file(module_name, new_path, old_path) -> Operation:
    return migrations.RunSQL(
        load_sql_by_path(module_name, new_path),
        load_sql_by_path(module_name, old_path),
    )
