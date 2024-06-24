import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/list')
def get_all_data():
    dataset_dir = 'dataset'
    filenames = [f for f in os.listdir(dataset_dir) if f.endswith('.json')]
    filenames.sort()
    return jsonify(filenames)


@app.route('/data/<filename>')
def get_data(filename):
    dataset_dir = 'dataset'
    file_path = os.path.join(dataset_dir, filename)

    # 检查文件是否存在
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # 读取并返回文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)