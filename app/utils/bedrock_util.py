# bedrock_util.py

import os
import json
from typing import List, Dict
import boto3
from dotenv import load_dotenv

load_dotenv()


class BedrockUtil:
    def __init__(self):
        self.runtime = boto3.client(
            "bedrock-runtime",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.model_id = os.getenv("BEDROCK_MODEL_ID")
        self.bucket = os.getenv("S3_BUCKET")
        self.prefix = os.getenv("S3_PREFIX", "")

    def _call_claude(self, prompt: str) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = self.runtime.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    # ✅ 단일 텍스트 처리
    def summarize_meeting(self, text: str) -> Dict:
        prompt = f"""<system>
너는 회의 요약 전문가야. 다음 회의 내용을 요약해서 JSON 형식으로 정리해줘.
</system>
<user>
{text}

요약 형식:
{{
  "subject": "회의 주제",
  "summary": "회의 내용 요약"
}}
</user>"""
        try:
            result = self._call_claude(prompt)
            return json.loads(result)
        except Exception as e:
            print("요약 실패:", e)
            return {"subject": "", "summary": "요약 실패"}

    def extract_todos(self, text: str) -> List[Dict]:
        prompt = f"""<system>
너는 회의 분석 전문가야. 아래 회의에서 할 일을 JSON 배열로 추출해줘.
</system>
<user>
{text}

[
  {{
    "text": "할 일 내용",
    "start": "시작 날짜 또는 없음",
    "end": "종료 날짜 또는 없음"
  }},
  ...
]
</user>"""
        try:
            result = self._call_claude(prompt)
            return json.loads(result)
        except Exception as e:
            print("할 일 추출 실패:", e)
            return []

    def extract_schedule(self, text: str) -> List[Dict]:
        prompt = f"""<system>
너는 일정 추출 전문가야. 회의에서 날짜나 일정을 JSON으로 정리해줘.
</system>
<user>
{text}

[
  {{
    "text": "일정 내용",
    "start": "시작 날짜 또는 없음",
    "end": "종료 날짜 또는 없음"
  }},
  ...
]
</user>"""
        try:
            result = self._call_claude(prompt)
            return json.loads(result)
        except Exception as e:
            print("일정 추출 실패:", e)
            return []

    # ✅ S3 전체 처리
    def _load_text_files_from_s3(self) -> List[Dict]:
        response = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix)
        results = []
        for obj in response.get("Contents", []):
            key = obj["Key"]
            if not key.endswith(".txt"):
                continue
            s3_obj = self.s3.get_object(Bucket=self.bucket, Key=key)
            text = s3_obj["Body"].read().decode("utf-8")
            results.append({"key": key, "text": text})
        return results

    def summarize_all_files(self) -> List[Dict]:
        files = self._load_text_files_from_s3()
        results = []

        for f in files:
            summary = self.summarize_meeting(f["text"])

            # 📌 등록일 가져오기
            head = self.s3.head_object(Bucket=self.bucket, Key=f["key"])
            uploaded_at = head["LastModified"].strftime("%Y-%m-%d")

            # 📌 요약 안에도 넣고 싶다면 여기에 추가 가능
            summary["start"] = uploaded_at  # Optional

            results.append({
                "file": f["key"],
                "summary": summary
            })

        return results


    def generate_all_todos(self) -> List[Dict]:
     files = self._load_text_files_from_s3()
     results = []

     for f in files:
         todos = self.extract_todos(f["text"])


         head = self.s3.head_object(Bucket=self.bucket, Key=f["key"])
         uploaded_at = head["LastModified"].strftime("%Y-%m-%d")


         for todo in todos:
             if not todo.get("start"):
                 todo["start"] = uploaded_at

         results.append({
             "file": f["key"],
             "todos": todos
         })

     return results



    def generate_all_schedules(self) -> List[Dict]:
      files = self._load_text_files_from_s3()
      results = []

      for f in files:
          schedules = self.extract_schedule(f["text"])

          head = self.s3.head_object(Bucket=self.bucket, Key=f["key"])
          uploaded_at = head["LastModified"].strftime("%Y-%m-%d")

          for sch in schedules:
              if not sch.get("start"):
                  sch["start"] = uploaded_at

          results.append({
              "file": f["key"],
              "schedules": schedules
          })

      return results
