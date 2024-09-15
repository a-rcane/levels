from flask import Flask, request, jsonify
import pandas as pd
from sqlalchemy import create_engine, QueuePool
from database import get_db_connection, create_table
import numpy as np
import json
from flask_caching import Cache

app = Flask(__name__)


cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)


with app.app_context():
    create_table()


DATABASE_URL = 'sqlite:///data/sensor_data.db'
engine = create_engine(DATABASE_URL, poolclass=QueuePool, pool_size=10, max_overflow=20)


@app.route('/ingest', methods=['POST'])
def ingest():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    try:
        # Fetch and load CSV
        df = pd.read_csv(url)
        with engine.connect() as conn:
            df.to_sql('sensor_data', conn, if_exists='append', index=False, chunksize=10000)

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

    # Apply filters to query
    for key in ['id', 'type', 'subtype', 'location']:
        if key in filters:
            append_filter(key, filters[key])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return query, params


@app.route('/median', methods=['GET'])
@cache.cached(timeout=60, key_prefix='median_data')
def get_median():
    filter_param = request.args.get('filter')
    filters = json.loads(filter_param) if filter_param else {}

    query = "SELECT reading FROM sensor_data"
    query, params = apply_filters(query, filters)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            readings = [row['reading'] for row in result.fetchall()]

        if not readings:
            return jsonify({"message": "No sensor data found matching the filter."}), 200

        median_value = np.median(readings)

        response = {
            "count": len(readings),
            "median": median_value
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, threaded=True)
