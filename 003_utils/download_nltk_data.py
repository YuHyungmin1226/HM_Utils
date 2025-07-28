import nltk
import ssl

# SSL 인증서 검증 비활성화
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 필요한 NLTK 데이터 다운로드
print("NLTK 데이터 다운로드 중...")
nltk.download('punkt')
nltk.download('stopwords')

print("다운로드 완료!") 