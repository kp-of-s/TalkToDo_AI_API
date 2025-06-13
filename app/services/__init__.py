# services 패키지 초기화 
from app.services.api_service import APIService
from app.utils.whisper_util import WhisperUtil
from app.utils.langchain_util import LangChainUtil
from app.utils.s3_util import S3Util

def create_api_service():
    whisper_util = WhisperUtil()
    langchain_util = LangChainUtil()
    s3_util = S3Util()
    
    return APIService(
        whisper_util=whisper_util,
        langchain_util=langchain_util,
        s3_util=s3_util
    ) 