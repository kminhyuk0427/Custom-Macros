#  keyM v2.1.5

##  특징

-  **빠름**: 최소 0.01s 딜레이
-  **가벼움**: 메모리 22mb, CPU 3% (동작 시)
-  **쉬움**: 가이드 따라만 하면 됨

##  주요 기능(세부 설명은 config.py)

-  **mode**: 0=비활성 1=연속동작 2=단일동작
-  **holds**: 특정 키를 몇 초 동안 누르고 있도록 설정 가능
-  **delay**: 몇초 후 다음 키를 누를지 지정
-  **토글 키**: 기본은 백틱키"`"로 되어있음
-  **강제 종료 키**: ALT + SHIFT + DEL

##  주의사항

-  **중복 X**: 매크로 진행중에는 다른 매크로가 눌리지 않음
-  **반복 중단**: 매크로 반복동작 중에 키를 때면 그 즉시 동작중이던 매크로가 중지됨
-  **반복 동작 오류1**: mode1(반복동작)에서 키를 매우 빠르게 눌렀다 때면 keyUP이 인식되지 않아 계속해서 입력될 수 있음
-  **반복 동작 오류2**: 반복동작모드를 빠르게 하면 os키입력이 섞이는 문제 있음

##  실행법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 실행 파일 생성

-  다운로드 받은 폴더에서 build.bat를 실행하여 빌드

### 3. 매크로 실행

-  바탕화면에 아이콘 클릭 후 실행(관리자 권한 자동으로 들어감)
-  바탕화면에 없으면 ..\Custom-Macros-master\dist폴더에 실행 파일이 존재함
-  게임 키고 나서 매크로 실행을 권장

##  매크로 설정

### 기본 예시
```python
MACROS = {
    '2': {
        'keys': ['3', '6'],
        'delays': [0.01, 0.01],
        'mode': 2
    },
}
```

### 홀드키 예
```python
't': {
    'keys': ['s', 'd'],
    'holds': [2.0, 0.01],  # s를 2초 동안 누름
    'delays': [0.1, 0.01],
    'mode': 2
}
```

### 반복 동작 예
```python
'3': {
    'keys': ['q', 'w', 'e'],
    'mode': 1 
}
```

##  종료하는 법

-  **방법 1**: ALT + SHIFT + DEL 키를 동시에 눌러서 강제 종료
-  **방법 2**: 작업 표시줄 숨김 아이콘에서 매크로 우클릭 → 종료

##  참고:

https://github.com/JU5TDIE/Lester-Ver2.0

https://learn.microsoft.com/en-us/previous-versions/windows/desktop/bb321074(v=vs.85)

https://gist.github.com/tracend/912308

https://github.com/LOUDO56/PyMacroRecord

https://stackoverflow.com/questions/43988871/convert-directinput-codes-into-keycodes-net

https://github.com/lihaoyi/macropy
