from locust import HttpUser, task, between
import random
import json
import uuid


class SensorDataTestUser(HttpUser):

    @task(1)
    def test_ingest(self):
        """Task for testing the ingestion of sensor data."""
        csv_url = "https://hack.levels.fyi/data.csv"  # Replace with an actual URL for testing
        self.client.post(f"/ingest?url={csv_url}")

    @task(3)
    def test_retrieval(self):
        """Task for testing the retrieval of sensor data with filters."""
        filters = {
            "id": str('fea1b70d-56c5-5271-6a1f-3ecc431d5aa4'),    # Randomly generated UUIDs for testing
            "type": str('8f764c71-277f-5f26-bed1-46a864e4a083'),
            "location": str('4228288a-04f7-f69d-78cf-273d08c772c1')
        }
        filter_json = json.dumps(filters)

        self.client.get(f"/median?filter={filter_json}")
