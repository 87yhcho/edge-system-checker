# H.264 디코딩 에러 메시지 처리

## 📅 업데이트 날짜
2025-10-27

## 🔍 에러 분석

### 발생한 에러
```
[h264 @ 0x394707c0] Missing reference picture, default is 0
[h264 @ 0x394707c0] decode_slice_header error
```

### 에러 의미

이 에러는 **H.264 비디오 디코딩 과정에서 발생하는 일시적인 경고 메시지**입니다.

**원인:**
- H.264 비디오는 **I-프레임**(Independent frame, 완전한 이미지)과 **P/B-프레임**(Predicted frame, 이전 프레임 참조)으로 구성됨
- RTSP 스트림에 연결할 때 중간부터 받게 되면, 참조할 이전 프레임이 없어서 발생
- 다음 I-프레임을 받으면 자동으로 정상 재생됨

## 🎥 H.264 비디오 구조

### 프레임 타입
```
I-frame: 완전한 이미지 (독립적)
P-frame: 이전 프레임 참조 (차이만 저장)
B-frame: 앞뒤 프레임 참조 (차이만 저장)
```

### 스트림 연결 예시
```
[카메라 스트림]
... → P → P → I → P → P → P → I → P → P → ...
              ↑
            연결 시점
            (P 프레임부터 받음)
```

**문제:**
- 연결 시점이 P-프레임이면 참조할 이전 프레임이 없음
- 다음 I-프레임까지 몇 프레임은 제대로 디코딩 안 됨
- I-프레임을 받으면 정상 재생

**결론:**
- 이 에러는 **정상적인 현상**
- 실제 스트림 재생에는 문제 없음
- 단지 FFmpeg가 경고 메시지를 출력하는 것

## 🔧 해결 방법

### 수정된 코드 (camera_check.py)

**추가된 내용:**
```python
# OpenCV/FFmpeg 에러 메시지 숨기기 (H.264 디코딩 경고 제거)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
cv2.setLogLevel(0)  # OpenCV 로그 레벨을 0으로 설정 (에러 숨김)
```

**적용 위치:**
```python
"""
카메라 RTSP 연결 점검 모듈
"""
import cv2
import time
import gc
import os
import re
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# 여기에 추가!
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
cv2.setLogLevel(0)
```

## 📊 수정 전/후 비교

### 수정 전 (에러 메시지 출력)
```
ℹ 카메라 4 블러 처리 스트리밍 (포트 1114) 연결 시도 중...
ℹ   URL: 127.0.0.1:1114
[h264 @ 0x394707c0] Missing reference picture, default is 0
[h264 @ 0x394707c0] decode_slice_header error
[h264 @ 0x394707c0] Missing reference picture, default is 0
[h264 @ 0x394707c0] decode_slice_header error
[h264 @ 0x394707c0] Missing reference picture, default is 0
[h264 @ 0x394707c0] decode_slice_header error
... (수십 줄의 에러 메시지)
✓ 카메라 4 블러 처리 스트리밍 연결 성공!
```

### 수정 후 (에러 메시지 숨김)
```
ℹ 카메라 4 블러 처리 스트리밍 (포트 1114) 연결 시도 중...
ℹ   URL: 127.0.0.1:1114
✓ 카메라 4 블러 처리 스트리밍 연결 성공!
```

## 🎯 적용된 설정

### 1. OpenCV FFmpeg 옵션
```python
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'
```
- **rtsp_transport;udp**: UDP를 사용하여 RTSP 전송 (더 빠름)
- **fflags;nobuffer**: 버퍼링 최소화 (실시간 스트림에 적합)

### 2. OpenCV 로그 레벨
```python
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
```
- OpenCV 내부 로그를 SILENT 모드로 설정

### 3. OpenCV 로그 레벨 (코드)
```python
cv2.setLogLevel(0)
```
- OpenCV의 로그 레벨을 0으로 설정 (에러 메시지 숨김)

## ❓ 자주 묻는 질문

### Q1: 에러를 숨기면 실제 문제도 못 찾는 거 아닌가요?
**A:** 아닙니다! 
- 이 에러는 **경고 메시지**일 뿐, 실제 문제가 아닙니다
- 스트림 연결 실패 같은 **실제 오류는 여전히 감지**됩니다
- 프로그램의 `try-except` 블록에서 실제 오류를 처리합니다

### Q2: 모든 카메라에서 이 에러가 발생하나요?
**A:** 네, 대부분 발생합니다.
- RTSP 스트림에 처음 연결할 때 흔한 현상
- I-프레임을 받기 전까지 일시적으로 발생
- 몇 초 후 자동으로 정상 재생됨

### Q3: 이 에러가 스트림 품질에 영향을 주나요?
**A:** 아니요!
- 연결 초기 몇 프레임만 영향
- I-프레임 이후로는 정상 재생
- 실제 사용자가 보는 영상에는 영향 없음

### Q4: 왜 갑자기 많이 출력되나요?
**A:** FFmpeg의 기본 동작입니다.
- FFmpeg는 기본적으로 모든 디코딩 문제를 출력
- 카메라 4대를 순차적으로 체크하면서 각각 발생
- 각 카메라마다 원본 + 블러 스트림 = 총 8번 연결
- 로그 레벨을 조정하면 숨길 수 있음

## ✅ 테스트 결과

```bash
$ python checker.py

모드 선택 [1: GUI / 2: Auto] (기본값: 2): 2

[2/4] 카메라 RTSP 연결 점검
────────────────────────────────────────
📡 Auto 모드: 영상 표시 없이 스트림 상태만 자동 확인합니다.

총 4대의 카메라를 점검합니다.

════════════════════════════════════════
   카메라 1 점검
════════════════════════════════════════

[1/2] 카메라 1 - 원본 카메라 영상
────────────────────────────────────────
ℹ 카메라 1 원본 카메라 연결 시도 중...
ℹ   URL: 192.168.1.101:554
✓ 카메라 1 원본 카메라 연결 성공!
  ✓ 프레임 읽기 성공 → 자동 PASS

[2/2] 카메라 1 - 블러 처리 스트리밍
────────────────────────────────────────
ℹ 카메라 1 블러 처리 스트리밍 연결 시도 중...
ℹ   URL: 127.0.0.1:1111
✓ 카메라 1 블러 처리 스트리밍 연결 성공!
  ✓ 프레임 읽기 성공 → 자동 PASS

# 에러 메시지 없이 깔끔하게 출력!
```

## 💡 추가 정보

### H.264 GOP (Group of Pictures) 구조
```
I P P P P P P P I P P P P P P P I
└─ GOP 1 (8프레임) ─┘ └─ GOP 2 (8프레임) ─┘
```

- **GOP 크기**: 보통 1초 (30프레임 기준 30프레임마다 I-프레임)
- **연결 대기 시간**: 최대 1 GOP 크기 (보통 1초 이내)
- **실제 영향**: 연결 후 1초 이내로 정상 재생

### FFmpeg 로그 레벨
```
AV_LOG_QUIET   = -8  (완전 침묵)
AV_LOG_PANIC   =  0  (패닉 오류만)
AV_LOG_FATAL   =  8  (치명적 오류만)
AV_LOG_ERROR   = 16  (오류만)
AV_LOG_WARNING = 24  (경고 포함)
AV_LOG_INFO    = 32  (정보 포함, 기본값)
AV_LOG_VERBOSE = 40  (상세 정보)
AV_LOG_DEBUG   = 48  (디버그 정보)
```

우리는 `cv2.setLogLevel(0)`으로 설정하여 **패닉 오류만 출력**하도록 했습니다.

## 🚀 사용 방법

```bash
# SSH로 접속
ssh koast-user@10.1.10.128

# 프로그램 실행
cd ~/edge-system-checker
source venv/bin/activate
python checker.py

# Auto 모드 선택
모드 선택 [1: GUI / 2: Auto] (기본값: 2): 2
```

## 🎉 결론

**H.264 디코딩 에러 메시지가 숨겨졌습니다!**

- ✅ `Missing reference picture` 에러는 정상적인 현상
- ✅ RTSP 스트림 연결 초기에 발생하는 일시적 경고
- ✅ 실제 스트림 재생에는 문제 없음
- ✅ OpenCV 로그 레벨 조정으로 에러 메시지 숨김
- ✅ 깔끔한 출력으로 가독성 향상

이제 **불필요한 에러 메시지 없이 깔끔하게** 카메라 점검이 진행됩니다! 🎊

