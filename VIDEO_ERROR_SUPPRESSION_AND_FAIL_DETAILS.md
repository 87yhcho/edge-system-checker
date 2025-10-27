# 비디오 에러 메시지 완전 숨기기 & FAIL 항목 상세 표시

## 📅 업데이트 날짜
2025-10-27

## 🎯 수정사항

### 1. 비디오 에러 메시지 완전 숨기기

**문제:**
- H.264, HEVC 등 다양한 코덱의 디코딩 경고 메시지가 여전히 출력됨
- 기존 설정으로는 일부 에러만 숨겨짐

**해결:**
- FFmpeg 로그 레벨을 완전 침묵(`-8`)으로 설정
- 모든 비디오 코덱 에러 메시지 완전 차단

### 2. 시스템 점검 FAIL 항목 상세 표시

**문제:**
- FAIL 결과만 표시되고 어떤 항목이 실패했는지 알기 어려움
- 특히 IP 주소 필수 체크에서 어떤 IP가 누락됐는지 모름

**해결:**
- FAIL 발생 시 상세 정보 즉시 표시
- IP 주소 체크에서 필수 IP별 상태 표시

## 🔧 수정된 코드

### 1. 비디오 에러 메시지 완전 숨기기 (camera_check.py)

**변경 전:**
```python
# OpenCV/FFmpeg 에러 메시지 숨기기 (H.264 디코딩 경고 제거)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
cv2.setLogLevel(0)
```

**변경 후:**
```python
# OpenCV/FFmpeg 에러 메시지 완전히 숨기기 (H.264, HEVC 등 모든 디코딩 경고 제거)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
os.environ['OPENCV_FFMPEG_LOGLEVEL'] = '-8'  # AV_LOG_QUIET (-8) = 완전 침묵
cv2.setLogLevel(0)
```

**추가된 환경 변수:**
- `OPENCV_VIDEOIO_DEBUG='0'`: VideoIO 디버그 메시지 비활성화
- `OPENCV_FFMPEG_LOGLEVEL='-8'`: FFmpeg 로그 레벨을 AV_LOG_QUIET로 설정

### 2. FAIL 항목 상세 표시 (system_check.py)

**변경 전:**
```python
if 'ip_addresses' in network:
    ip_info = network['ip_addresses']
    if ip_info.get('status') == 'PASS':
        print_pass(f"IP 주소: {ip_info.get('count')}개")
        for addr in ip_info.get('addresses', []):
            print(f"    {addr}")
```

**변경 후:**
```python
if 'ip_addresses' in network:
    ip_info = network['ip_addresses']
    if ip_info.get('status') == 'PASS':
        print_pass(f"IP 주소: {ip_info.get('count')}개")
        for addr in ip_info.get('addresses', []):
            print(f"    {addr}")
    else:
        print_fail(f"IP 주소: {ip_info.get('count')}개 (필수 IP 누락)")
        # 필수 IP 상태 표시
        if 'required' in ip_info:
            for req_ip in ip_info.get('required', []):
                if req_ip in ip_info.get('found', []):
                    print_pass(f"  ✓ {req_ip}")
                else:
                    print_fail(f"  ✗ {req_ip} (없음)")
```

## 📊 수정 전/후 비교

### 1. 비디오 에러 메시지

**수정 전:**
```
ℹ 카메라 4 원본 카메라 연결 시도 중...
ℹ   URL: 192.168.1.104:554
[hevc @ 0x52d1640] Could not find ref with POC 1
✓ 카메라 4 원본 카메라 연결 성공!

ℹ 카메라 1 블러 처리 스트리밍 (포트 1111) 연결 시도 중...
ℹ   URL: 127.0.0.1:1111
[h264 @ 0x531f2c0] Missing reference picture, default is 0
[h264 @ 0x531f2c0] decode_slice_header error
... (수십 줄)
✓ 카메라 1 블러 처리 스트리밍 연결 성공!
```

**수정 후:**
```
ℹ 카메라 4 원본 카메라 연결 시도 중...
ℹ   URL: 192.168.1.104:554
✓ 카메라 4 원본 카메라 연결 성공!

ℹ 카메라 1 블러 처리 스트리밍 (포트 1111) 연결 시도 중...
ℹ   URL: 127.0.0.1:1111
✓ 카메라 1 블러 처리 스트리밍 연결 성공!
```

### 2. FAIL 항목 상세 표시

**수정 전:**
```
ℹ 네트워크 설정 확인 중...
✓ 활성 연결: 5개

✗ 시스템 종합 점검 결과: FAIL (✓16 ✗1 ⚠0 ◌1)
```

**수정 후:**
```
ℹ 네트워크 설정 확인 중...
✗ IP 주소: 2개 (필수 IP 누락)
  ✓ 192.168.1.10/24
  ✗ 192.168.10.20/24 (없음)
✓ 활성 연결: 5개

✗ 시스템 종합 점검 결과: FAIL (✓16 ✗1 ⚠0 ◌1)
```

## 🎯 FFmpeg 로그 레벨

### FFmpeg 로그 레벨 종류
```
-8  AV_LOG_QUIET     완전 침묵 (에러도 출력 안 함)
 0  AV_LOG_PANIC     패닉 상황만
 8  AV_LOG_FATAL     치명적 오류만
16  AV_LOG_ERROR     오류만
24  AV_LOG_WARNING   경고 포함
32  AV_LOG_INFO      정보 포함 (기본값)
40  AV_LOG_VERBOSE   상세 정보
48  AV_LOG_DEBUG     디버그 정보
```

**우리가 설정한 값:**
- `-8` (AV_LOG_QUIET): 완전 침묵
- 모든 비디오 코덱 에러 메시지 차단

## 🔍 에러 메시지 종류

### 차단되는 에러 메시지들

**H.264 (AVC) 에러:**
```
[h264 @ 0x531f2c0] Missing reference picture, default is 0
[h264 @ 0x531f2c0] decode_slice_header error
```

**HEVC (H.265) 에러:**
```
[hevc @ 0x52d1640] Could not find ref with POC 1
[hevc @ 0x52d1640] Error splitting the input into NAL units
```

**기타 코덱 에러:**
- MJPEG, VP8, VP9 등 모든 코덱의 디코딩 경고
- 네트워크 타임아웃 경고
- 버퍼링 관련 경고

**모두 차단됨!**

## 💡 IP 주소 체크 상세 표시

### PASS 케이스
```
ℹ 네트워크 설정 확인 중...
✓ IP 주소: 3개
    enp1s0 192.168.1.10/24
    enp2s0 192.168.10.20/24
    enp3s0 10.0.0.100/24
```

### FAIL 케이스 (상세 표시)
```
ℹ 네트워크 설정 확인 중...
✗ IP 주소: 2개 (필수 IP 누락)
  ✓ 192.168.1.10/24
  ✗ 192.168.10.20/24 (없음)
```

**장점:**
- 어떤 IP가 있고 없는지 즉시 확인
- 문제 해결이 빠름
- 디버깅이 쉬움

## ✅ 환경 변수 전체 목록

### camera_check.py에 설정된 환경 변수

```python
# RTSP 전송 설정
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp|fflags;nobuffer'

# OpenCV 로그 레벨
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'

# VideoIO 디버그
os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'

# FFmpeg 로그 레벨 (완전 침묵)
os.environ['OPENCV_FFMPEG_LOGLEVEL'] = '-8'

# OpenCV 코드 로그 레벨
cv2.setLogLevel(0)
```

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

**비디오 에러 메시지가 완전히 사라지고, FAIL 항목이 상세하게 표시됩니다!**

### 1. 비디오 에러 메시지
- ✅ H.264, HEVC 등 모든 코덱 에러 완전 차단
- ✅ FFmpeg 로그 레벨을 -8 (완전 침묵)로 설정
- ✅ 깔끔한 출력으로 가독성 극대화

### 2. FAIL 항목 상세 표시
- ✅ IP 주소 체크 실패 시 어떤 IP가 누락됐는지 표시
- ✅ 필수 IP별 ✓/✗ 상태 표시
- ✅ 즉시 문제 파악 가능

이제 **불필요한 에러 메시지 없이 깔끔하고**, **FAIL 항목은 상세하게** 표시됩니다! 🎊

