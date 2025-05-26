import os
import json
from flask import Blueprint, jsonify, request
from settings import BENCHMARKS_PATH


benchmarks_bp = Blueprint('benchmarks', __name__)

@benchmarks_bp.route('/api/benchmarks', methods=['GET', 'DELETE'])
def benchmarks():
    if request.method == 'GET':
        if os.path.exists(BENCHMARKS_PATH):
            benchmark_files = [f for f in os.listdir(BENCHMARKS_PATH) if f.endswith(".json")]

            if benchmark_files:
                benchmarks_data = []
                for benchmark_file in benchmark_files:
                    with open(os.path.join(BENCHMARKS_PATH, benchmark_file), 'r') as f:
                        data = json.load(f)
                    benchmarks_data.append(data)
                return jsonify(benchmarks_data)
            else:
                return jsonify({"message": "No benchmark files found."}), 200
        else:
            return jsonify({"message": "No benchmark files found."}), 200
    
    if request.method == 'DELETE':
        if os.path.exists(BENCHMARKS_PATH):
            for filename in os.listdir(BENCHMARKS_PATH):
                if filename.endswith('.json'):
                    file_path = os.path.join(BENCHMARKS_PATH, filename)
                    os.remove(file_path)
            return jsonify({'message': 'Deleted all benchmark files.'}), 200
        else:
            return jsonify({'message': 'No benchmark files found.'}), 200