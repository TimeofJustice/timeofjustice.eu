import configparser
import datetime
from pathlib import Path
import psycopg2

config = configparser.ConfigParser()
config.read(Path(__file__).resolve().parent.parent / 'config.ini')

production = psycopg2.connect(host="127.0.0.1",
                              database=config['DEFAULT']['PRODUCTION_DB'],
                              user=config['DEFAULT']['SQL_USER'],
                              password=config['DEFAULT']['SQL_PASS'],
                              port=config['DEFAULT']['SQL_PORT'])

staging = psycopg2.connect(host="127.0.0.1",
                           database=config['DEFAULT']['SQL_DB'],
                           user=config['DEFAULT']['SQL_USER'],
                           password=config['DEFAULT']['SQL_PASS'],
                           port=config['DEFAULT']['SQL_PORT'])

staging_cursor = staging.cursor()
production_cursor = production.cursor()

# get all tables from staging
staging_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
tables = staging_cursor.fetchall()

# drop all tables from staging
for table in tables:
    print(f"Dropping {table[0]}")
    staging_cursor.execute(f"DROP TABLE {table[0]} CASCADE;")

# save changes
staging.commit()

# Drop all relations from pg_class with kind 'S' (sequences)
staging_cursor.execute("SELECT relname FROM pg_class WHERE relkind = 'S';")
sequences = staging_cursor.fetchall()

for sequence in sequences:
    print(f"Dropping {sequence[0]}")
    staging_cursor.execute(f"DROP SEQUENCE {sequence[0]};")

# save changes
staging.commit()

# get all tables from production and create them in staging
production_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")

tables = production_cursor.fetchall()

for table in tables:
    print(f"Creating {table[0]}")

    # Fetch column details
    production_cursor.execute(f"SELECT column_name, data_type, character_maximum_length, is_nullable, is_identity FROM information_schema.columns WHERE table_name = '{table[0]}' ORDER BY ordinal_position;")
    columns = production_cursor.fetchall()

    # Start building the CREATE TABLE query
    query = f"CREATE TABLE {table[0]} ("
    for column in columns:
        column_name = column[0]
        data_type = column[1]
        char_max_length = column[2]
        is_nullable = column[3]
        is_identity = column[4]

        # Escape column name using double quotes
        query += f"\"{column_name}\" {data_type}"

        # Add length constraint if applicable
        if char_max_length is not None:
            query += f"({char_max_length})"

        # Add NOT NULL if applicable
        if is_nullable == 'NO':
            query += " NOT NULL"

        # Add IDENTITY if applicable
        if is_identity == 'YES':
            query += " GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY"

        query += ", "

    # Remove the trailing comma and space, then close the statement
    query = query[:-2] + ");"

    print(f"Executing query: {query}")

    # Execute the query on the staging database
    staging_cursor.execute(query)

# save changes
staging.commit()

for table in tables:
    table_name = table[0]
    print(f"Copying data from {table_name}")

    production_cursor.execute(f"SELECT * FROM {table_name};")
    rows = production_cursor.fetchall()

    # Fetch column details to handle data types correctly
    production_cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' ORDER BY ordinal_position;")
    columns = production_cursor.fetchall()

    for row in rows:
        query = f"INSERT INTO {table_name} VALUES ("
        for i, value in enumerate(row):
            # Determine the column type
            column_name = columns[i][0]
            column_type = columns[i][1]

            if value is None:
                query += "NULL, "
            elif isinstance(value, str):
                # Replace vue.timeofjustice.eu with staging.timeofjustice.eu in paths
                search_term = f"var/www/{config['DEFAULT']['PRODUCTION_DB']}/"
                replace_term = f"var/www/{config['DEFAULT']['SQL_DB']}/"

                if search_term in value:
                    value = value.replace(search_term, replace_term)
                query += f"'{value.replace("'", "''")}', "  # Escape single quotes in strings
            elif isinstance(value, (int, float)):
                query += f"{value}, "
            elif isinstance(value, datetime.date):
                query += f"'{value}', "  # Format date and datetime values
            elif isinstance(value, bool):
                query += f"{'TRUE' if value else 'FALSE'}, "  # Format boolean values
            else:
                query += f"'{value}', "  # Default case for other data types

        query = query[:-2] + ");"

        print(f"Executing query: {query}")

        try:
            staging_cursor.execute(query)
        except Exception as e:
            print(f"Failed to insert row into {table_name}: {e}")

    # save changes
    staging.commit()

# Get all sequences from production and set the last value in staging
production_cursor.execute("SELECT relname FROM pg_class WHERE relkind = 'S';")
sequences = production_cursor.fetchall()

for sequence in sequences:
    sequence_name = sequence[0]
    print(f"Setting last value for {sequence_name}")

    production_cursor.execute(f"SELECT last_value FROM {sequence_name};")
    last_value = production_cursor.fetchone()[0]

    staging_cursor.execute(f"SELECT setval('{sequence_name}', {last_value});")

    # save changes
    staging.commit()

# save changes
staging.commit()

# Close connections
staging_cursor.close()
staging.close()

production_cursor.close()
production.close()