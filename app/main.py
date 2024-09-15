from flask import Flask, request, jsonify
import pandas as pd
from database import get_db_connection, create_table
import numpy as np
import json

app = Flask(__name__)

with app.app_context():
    create_table()


@app.route('/ingest', methods=['POST'])
def ingest():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        df = pd.read_csv(url)
        conn = get_db_connection()
        df.to_sql('sensors', conn, if_exists='append', index=False, chunksize=10000)
        conn.commit()
        conn.close()
        return jsonify({"message": "Data ingested successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def apply_filters(query, filters):
    conditions = []
    params = []

    def append_filter(column_name, filter_values):
        if isinstance(filter_values, list):
            if len(filter_values) > 1:
                conditions.append(f'{column_name} IN ({", ".join("?" for _ in filter_values)})')
                params.extend(filter_values)
            elif len(filter_values) == 1:
                conditions.append(f'{column_name} = ?')
                params.append(filter_values[0])
        elif isinstance(filter_values, str):
            conditions.append(f'{column_name} = ?')
            params.append(filter_values)

    for key in ['id', 'type', 'subtype', 'location']:
        if key in filters:
            append_filter(key, filters[key])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query, params


@app.route('/median', methods=['GET'])
def get_median():
    filter_param = request.args.get('filter')
    filters = json.loads(filter_param) if filter_param else {}

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT reading FROM sensor_data"
    query, params = apply_filters(query, filters)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    readings = [row['reading'] for row in rows]

    if not readings:
        return jsonify({"message": "No sensor data found matching the filter."}), 200

    median_value = np.median(readings)

    response = {
        "count": len(readings),
        "median": median_value
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
