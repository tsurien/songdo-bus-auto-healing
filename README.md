# 송도 버스 도착 안내 및 자동 복구 서비스

송도센트럴파크역 38563번 정류소의 도착정보를 안내하고, 수집·안내·저장 장애를 제한적으로 복구하는 팀 프로젝트입니다. 요구사항은 `docs/prd-auto-healing.md`, 작업 상태는 `tasks/tasks-auto-healing.md`를 확인하세요.

## 개발 환경 준비

Python 3.12와 Docker Desktop이 필요합니다. 프로젝트 폴더에서 아래 명령을 실행합니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`py` 명령이 없다면 설치된 Python 3.12 실행 파일의 전체 경로로 첫 명령을 실행하세요. Docker Desktop을 켜고 `docker version`으로 연결을 확인합니다. 현재 프로젝트에는 애플리케이션 실행 명령이 아직 없습니다.

## 설정과 비밀값

공공 API, Gemini, Supabase 키 등은 코드나 저장소에 입력하지 않습니다. 로컬 `.env` 또는 운영환경 변수로 관리하며 `.env`와 Streamlit 비밀 설정 파일은 Git 추적에서 제외합니다. 실제 키는 팀이 각자 안전하게 준비합니다. API와 데이터베이스 연동은 아직 확인하지 않았습니다.
