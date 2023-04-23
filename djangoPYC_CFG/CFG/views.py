import sys
from pathlib import Path
sys.path.append(fr"{Path(__file__).resolve().parent.parent}/CFG");
print("views path:", sys.path);
from django.shortcuts import render
import json
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from disposeCFG.main import getCFG



def receive_codeData(request):
    # return HttpResponse("无效的 JSON 数据。");
    if request.method == 'GET':
        json_data = request.body.decode('utf-8');
        try:
            data = json.loads(json_data);
        except ValueError:
            return HttpResponseBadRequest("无效的 JSON 数据。");

        data = json.loads(json_data);
        code = data.get('code', None);
        if code:
            # 如果获取到了code属性
            ans = getCFG(code);
            print("完成");
            return JsonResponse(ans);


