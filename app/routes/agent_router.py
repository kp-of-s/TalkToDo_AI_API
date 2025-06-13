from flask import Blueprint, request, jsonify
import boto3, os, json
from dotenv import load_dotenv

load_dotenv()

agent_bp = Blueprint("agent_bp", __name__)

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

bedrock = boto3.client(
    "bedrock-agent-runtime",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

@agent_bp.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    user_id = request.json.get("user_id", "")
    bucket = os.getenv("S3_BUCKET")  # 예: ai-s3-j2pk
    prefix = f"meetings/{user_id}/"

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # 사용자 txt 파일 읽기
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        meeting_txts = []

        for obj in response.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".txt"):
                txt_obj = s3.get_object(Bucket=bucket, Key=key)
                content = txt_obj["Body"].read().decode("utf-8")
                meeting_txts.append(content)

        if not meeting_txts:
            return jsonify({"response": "회의 텍스트를 찾을 수 없습니다."})

        # 전체 회의 텍스트 합치기
        context = "\n\n".join(meeting_txts)
        prompt = f"""다음은 과거 회의록입니다:\n\n{context}\n\n사용자 질문: {user_input}\n\n답변:"""

        session_id = f"session-{user_id}"
        response = bedrock.invoke_agent(
            agentId=os.getenv("BEDROCK_AGENT_ID"),
            agentAliasId=os.getenv("BEDROCK_AGENT_ALIAS_ID"),
            sessionId=session_id,
            inputText=prompt,
            enableTrace=False
        )

        output_text = ""
        for event in response.get("completion", []):
            if "chunk" in event:
                try:
                    output_text += event["chunk"]["bytes"].decode("utf-8")
                except Exception as e:
                    print("❌ Decode error:", e)

        return jsonify({"response": output_text})

    except Exception as e:
        print("❌ 에러:", str(e))
        return jsonify({"error": str(e)}), 500
