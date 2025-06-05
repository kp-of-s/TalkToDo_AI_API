from app.utils.bedrock_util import BedrockUtil

class RAGService:
    def __init__(self):
        self.util = BedrockUtil()

    # 단일 텍스트 처리용
    def summarize_text(self, text: str):
        return self.util.summarize_meeting(text)

    def extract_todos(self, text: str):
        return self.util.extract_todos(text)

    def extract_schedules(self, text: str):
        return self.util.extract_schedule(text)

    # S3 전체 처리용
    def summarize_all_files(self):
        return self.util.summarize_all_files()

    def generate_todos(self):
        return self.util.generate_all_todos()

    def generate_schedules(self):
        return self.util.generate_all_schedules()
