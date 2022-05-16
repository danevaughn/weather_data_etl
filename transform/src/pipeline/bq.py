from google.cloud import bigquery
from typing import List


schema = [
    bigquery.SchemaField('coord_lon', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('coord_lat', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('weather_main', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('weather_description', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('base', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('main_temp', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('main_feels_like', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('main_temp_min', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('main_temp_max', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('temp_unit', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('main_pressure', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('main_humidity', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('visibility', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('wind_speed', bigquery.enums.SqlTypeNames.FLOAT64),
    bigquery.SchemaField('wind_deg', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('clouds_all', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('dt', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('sys_sunrise', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('sys_sunset', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('timezone', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('id', bigquery.enums.SqlTypeNames.INT64),
    bigquery.SchemaField('name', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('bucket_name', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('blob_name', bigquery.enums.SqlTypeNames.STRING),
    bigquery.SchemaField('timestamp', bigquery.enums.SqlTypeNames.TIMESTAMP),
    bigquery.SchemaField('real_insert_timestamp', bigquery.enums.SqlTypeNames.TIMESTAMP)
]


load_job_config = bigquery.LoadJobConfig(
    schema=schema, write_disposition='WRITE_APPEND', ignore_unknown_values=False
)

def get_columns(schema: List[bigquery.SchemaField] = schema) -> List[str]:
    columns = []
    for column in schema:
        columns.append(column.name)
    return columns