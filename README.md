# Function-Mapping-Visualizer

집합의 원소들 간의 관계를 시각화하는 인터랙티브 GUI 도구입니다. Matplotlib을 사용하여 렌더링하며, 원소를 클릭하여 화살표를 그릴 수 있습니다.

## 요구사항

`requirements.txt`에 나열된 종속성을 `pip install -r requirements.txt` 명령어로 설치하세요.

## 폰트 설정

한글과 같은 비ASCII 문자를 입력하면 누락된 글리프에 대한 경고가 표시될 수 있습니다. 코드는 이제 한글 문자를 표시할 수 있는 폰트를 자동으로 선택하려고 시도합니다. 시스템에 다음 폰트 중 하나 이상이 설치되어 있는지 확인하세요:

- AppleGothic
- Malgun Gothic
- NanumGothic
- DejaVu Sans

이러한 폰트가 모두 없으면 여전히 경고가 표시될 수 있습니다.
