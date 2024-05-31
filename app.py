from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 모든 도메인에서의 요청을 허용하기 위해 CORS 설정
CORS(app)

@app.route('/process', methods=['POST'])
def process_text():
    # 요청으로부터 JSON 데이터를 받아옵니다.
    data = request.get_json()
    
    # 입력된 텍스트를 확인합니다.
    input_text = data.get('text')
    
    # 입력 텍스트를 처리합니다.
    if input_text == 'hello':
        result_text = 'hello는 안녕이야'
    else:
        result_text = '알 수 없는 입력입니다.'
    
    # 결과를 JSON 응답으로 반환합니다.
    response = {
        'result': result_text
    }
    return jsonify(response)

if __name__ == '__main__':
    # 서버를 실행합니다. localhost:5000에서 대기합니다.
    app.run(host='localhost', port=5000)
