from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# 백엔드의 UploadTestCase와 연결되는 뷰 함수
@csrf_exempt
def upload(request):
    if request.method == 'POST':
        # 클라이언트로부터 전송된 데이터를 파싱합니다.
        data = json.loads(request.body)

        # 여기서부터 클라이언트로부터 받은 데이터를 처리하고 응답을 생성하는 로직을 작성합니다.
        # 예를 들어:
        # original_text = data['corpus']['original_text']
        # ... 처리 로직 ...

        # 임시적으로 응답 데이터를 작성
        response_data = {"corpus_id": 123}  # 예시로 임의의 corpus_id를 반환합니다.

        return JsonResponse(response_data, status=201)  # JsonResponse로 응답을 보냅니다.
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)  # POST 이외의 메서드에 대한 에러 응답

# 백엔드의 DivideTestCase와 연결되는 뷰 함수
@csrf_exempt
def divide(request):
    if request.method == 'POST':
        # 클라이언트로부터 전송된 데이터를 파싱합니다.
        data = json.loads(request.body)

        # 여기서부터 클라이언트로부터 받은 데이터를 처리하고 응답을 생성하는 로직을 작성합니다.
        # 예를 들어:
        # corpus_id = data['corpus_id']
        # ... 처리 로직 ...

        # 임시적으로 응답 데이터를 작성
        response_data = {"task_id": 456}  # 예시로 임의의 task_id를 반환합니다.

        return JsonResponse(response_data, status=200)  # JsonResponse로 응답을 보냅니다.
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)  # POST 이외의 메서드에 대한 에러 응답

# 백엔드의 ParserTestCase와 연결되는 뷰 함수
@csrf_exempt
def parse(request):
    if request.method == 'POST':
        # 클라이언트로부터 전송된 데이터를 파싱합니다.
        data = json.loads(request.body)

        # 여기서부터 클라이언트로부터 받은 데이터를 처리하고 응답을 생성하는 로직을 작성합니다.
        # 예를 들어:
        # corpus_id = data['corpus_id']
        # ... 처리 로직 ...

        # 임시적으로 응답 데이터를 작성
        response_data = {"task_id": 789}  # 예시로 임의의 task_id를 반환합니다.

        return JsonResponse(response_data, status=200)  # JsonResponse로 응답을 보냅니다.
    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)  # POST 이외의 메서드에 대한 에러 응답
