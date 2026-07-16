from flask import jsonify, request
from datetime import datetime

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import sqlite3
import random
import os

class LogServer:

    def __init__(self):
        self.db_path = "data/logs.db"
        self.parquet_path = "data/logs.parquet"
        os.makedirs("data", exist_ok=True)
        self._create_table()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level VARCHAR(10),
                service VARCHAR(100),
                date DATE,
                message TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _sync_parquet(self):
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, level, service, date, message FROM logs"
        ).fetchall()
        conn.close()

        table = pa.table({
            "id": pa.array([r[0] for r in rows], type=pa.int64()),
            "level": pa.array([r[1] or "INFO" for r in rows], type=pa.string()),
            "service": pa.array([r[2] or "unknown" for r in rows], type=pa.string()),
            "date": pa.array([r[3] or "" for r in rows], type=pa.string()),
            "message": pa.array([r[4] or "" for r in rows], type=pa.string()),
        })
        pq.write_table(table, self.parquet_path)

    def health_check(self):
        return jsonify({"status": "healthy"}), 200

    def get_logs(self):
        if not os.path.exists(self.parquet_path):
            self._sync_parquet()

        level_filter = request.args.get("level")
        service_filter = request.args.get("service")
        message_filter = request.args.get("message")
        limit = request.args.get("limit", type=int)
        offset = request.args.get("offset", default=0, type=int)

        # Build predicate pushdown filters for Parquet row group skipping
        filters = []
        if level_filter and level_filter != "ALL":
            filters.append(("level", "==", level_filter))
        if service_filter and service_filter != "ALL":
            filters.append(("service", "==", service_filter))

        table = pq.read_table(self.parquet_path, filters=filters if filters else None)

        # Substring match can't be pushed down to Parquet, apply post-read
        if message_filter:
            mask = pc.match_substring(table.column("message"), message_filter, ignore_case=True)
            table = table.filter(mask)

        total = table.num_rows

        if offset > 0:
            table = table.slice(offset)
        if limit:
            table = table.slice(0, limit)

        result = table.to_pydict()
        logs = []
        for i in range(table.num_rows):
            logs.append({
                "id": result["id"][i],
                "level": result["level"][i],
                "service": result["service"][i],
                "date": result["date"][i],
                "message": result["message"][i],
            })

        return jsonify({"logs": logs, "total": total}), 200

    def random_log(self):
        levels = ["INFO", "WARN", "ERROR"]
        services = ["auth-service", "api-gateway", "payment-service", "user-service"]
        messages = ["Request processed", "Connection timeout", "Auth failed", "Service started", "Rate limit exceeded"]

        conn = self._get_conn()
        for i in range(10):
            conn.execute(
                "INSERT INTO logs (level, service, date, message) VALUES (?, ?, ?, ?)",
                (random.choice(levels), random.choice(services), datetime.now().isoformat(), random.choice(messages))
            )
        conn.commit()
        conn.close()
        self._sync_parquet()
        return jsonify({"status": "generated logs"}), 201

    def create_log(self, payload):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO logs (level, service, date, message) VALUES (?, ?, ?, ?)",
            (payload.get("level"), payload.get("service"), payload.get("date"), payload.get("message"))
        )
        conn.commit()
        conn.close()
        self._sync_parquet()
        return jsonify({"status": "log created"}), 201

    def delete_log(self, log_id):
        conn = self._get_conn()
        conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))
        conn.commit()
        conn.close()
        self._sync_parquet()
        return jsonify({"status": "log deleted"}), 200

    def clear_logs(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM logs")
        conn.commit()
        conn.close()
        if os.path.exists(self.parquet_path):
            os.remove(self.parquet_path)
        return jsonify({"status": "logs cleared"}), 200

    def get_services(self):
        conn = self._get_conn()
        rows = conn.execute("SELECT DISTINCT service FROM logs WHERE service IS NOT NULL").fetchall()
        conn.close()
        return jsonify([r[0] for r in rows]), 200
