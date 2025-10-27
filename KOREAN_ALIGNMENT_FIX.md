# 한글 문자 너비를 고려한 테이블 정렬 수정

## 📅 업데이트 날짜
2025-10-27

## 🎯 문제점

터미널에서 한글과 영문 문자의 표시 너비가 다른데, Python의 기본 문자열 포맷팅(`:<20`)은 이를 고려하지 않아 테이블 정렬이 틀어지는 문제가 발생했습니다.

### 문자 너비 차이
- **한글 (전각 문자)**: 2칸 차지
- **영문/숫자 (반각 문자)**: 1칸 차지

### 예시
```python
# Python의 기본 포맷팅
print(f"{'카메라':<10} {'IP':<10}")
print(f"{'카메라 1':<10} {'192.168.1.101':<10}")

# 출력 (정렬 안 맞음)
카메라     IP        
카메라 1   192.168.1.101
```

**문제**: `'카메라'`는 실제로 6칸을 차지하지만, Python은 3글자로 인식하여 7칸의 공백을 추가 → 총 10칸이 아닌 더 많은 공간 차지

## 🔧 해결 방법

### 1. 문자 너비 계산 함수 추가

```python
import unicodedata

def get_display_width(text):
    """
    문자열의 실제 터미널 표시 너비를 계산
    한글/중국어/일본어 등 전각 문자는 2칸, 영문/숫자 등은 1칸
    ANSI 색상 코드는 너비에서 제외
    """
    import re
    # ANSI 색상 코드 제거
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    text_without_ansi = ansi_escape.sub('', text)
    
    width = 0
    for char in text_without_ansi:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2  # 전각 문자 (한글, 중국어, 일본어 등)
        else:
            width += 1  # 반각 문자 (영문, 숫자, 기호 등)
    return width
```

### 2. 패딩 함수 추가

```python
def pad_string(text, target_width):
    """
    문자열을 목표 너비에 맞춰 오른쪽에 공백 추가
    한글 문자 너비를 고려하여 정확한 정렬
    """
    current_width = get_display_width(text)
    padding = target_width - current_width
    if padding > 0:
        return text + ' ' * padding
    return text
```

## 📊 문자 너비 계산 예시

```
문자열        | 글자 수 | 실제 너비 | 설명
-------------|---------|-----------|------------------
'카메라'     | 3       | 6         | 한글 3자 × 2칸
'IP'         | 2       | 2         | 영문 2자 × 1칸
'원본'       | 2       | 4         | 한글 2자 × 2칸
'PASS'       | 4       | 4         | 영문 4자 × 1칸
'카메라 1'   | 4       | 8         | 한글 3자(6칸) + 공백(1칸) + 숫자(1칸)
```

## 🔧 수정된 코드

### 전체 요약 테이블

**변경 전:**
```python
print(f"  {item:<20} : {status_str}")
```

**변경 후:**
```python
padded_item = pad_string(item, 20)
print(f"  {padded_item} : {status_str}")
```

### 카메라 상세 결과 테이블

**변경 전:**
```python
print(f"  {'카메라':<12} {'IP':<17} {'원본':<10} {'블러':<10} {'로그':<10}")
print(f"  {name:<12} {ip:<17} {source_str}     {mediamtx_str}     {log_str}")
```

**변경 후:**
```python
# 헤더
header_camera = pad_string("카메라", 12)
header_ip = pad_string("IP", 17)
header_source = pad_string("원본", 10)
header_blur = pad_string("블러", 10)
header_log = pad_string("로그", 10)
print(f"  {header_camera} {header_ip} {header_source} {header_blur} {header_log}")

# 데이터
padded_name = pad_string(name, 12)
padded_ip = pad_string(ip, 17)
padded_source = pad_string(source_str, 10)
padded_blur = pad_string(mediamtx_str, 10)
padded_log = pad_string(log_str, 10)
print(f"  {padded_name} {padded_ip} {padded_source} {padded_blur} {padded_log}")
```

### 시스템 점검 상세 결과 테이블

**변경 전:**
```python
print(f"  {'서비스 상태':<20} {'상태':<15} {'판정':<10}")
print(f"  {service_name:<20} {state:<15} {status_str:<10}")
```

**변경 후:**
```python
# 헤더
header_service = pad_string("서비스 상태", 20)
header_state = pad_string("상태", 15)
header_result = pad_string("판정", 10)
print(f"  {header_service} {header_state} {header_result}")

# 데이터
padded_service = pad_string(service_name, 20)
padded_state = pad_string(state, 15)
padded_status = pad_string(status_str, 10)
print(f"  {padded_service} {padded_state} {padded_status}")
```

## 📊 수정 전/후 비교

### 수정 전 (정렬 틀어짐)
```
  카메라          IP                원본         블러         로그
  카메라 1        192.168.1.101    PASS PASS PASS
```

### 수정 후 (정렬 맞음)
```
  카메라       IP                원본       블러       로그      
  카메라 1     192.168.1.101     PASS       PASS       PASS      
```

## 🎯 작동 원리

### 1. 너비 계산
```python
text = "카메라"
width = get_display_width(text)  # 6 (한글 3자 × 2칸)
```

### 2. 패딩 추가
```python
padded = pad_string("카메라", 12)
# "카메라      " (6칸 + 6칸 공백 = 총 12칸)
```

### 3. 출력
```python
print(f"  {padded}")  # 정확히 12칸 차지
```

## 🔍 Unicode East Asian Width

Python의 `unicodedata.east_asian_width()`는 문자의 동아시아 문자 너비를 반환합니다:

| 값  | 의미                | 너비 | 예시                    |
|-----|---------------------|------|-------------------------|
| F   | Fullwidth (전각)    | 2    | 한글, 중국어, 일본어    |
| W   | Wide (넓음)         | 2    | 특수 문자, 이모지       |
| H   | Halfwidth (반각)    | 1    | 반각 가타카나           |
| Na  | Narrow (좁음)       | 1    | 영문, 숫자              |
| A   | Ambiguous (애매)    | 1*   | 그리스 문자, 특수 기호  |
| N   | Neutral (중립)      | 1    | 일반 ASCII              |

*우리 코드에서는 'F'와 'W'만 2칸으로 처리

## ✅ 테스트 결과

```bash
$ python test_korean_width.py

=== 문자 너비 테스트 ===
'카메라' 너비: 6
'IP' 너비: 2
'원본' 너비: 4
'PASS' 너비: 4

=== 패딩 테스트 ===
[카메라      ] <- 12칸
[IP          ] <- 12칸
[원본      ] <- 10칸
[PASS      ] <- 10칸

=== 정렬 테스트 ===
  카메라       IP                원본       블러       로그      
  카메라 1     192.168.1.101     PASS       PASS       PASS      
```

## 🎨 ANSI 색상 코드 처리

색상 코드가 포함된 문자열도 정확히 처리됩니다:

```python
text = "\033[32mPASS\033[0m"  # 녹색 PASS
width = get_display_width(text)  # 4 (색상 코드 제외)

padded = pad_string(text, 10)
# "\033[32mPASS\033[0m      " (4칸 + 6칸 공백 = 총 10칸)
```

## 💡 추가 정보

### 왜 문제가 발생했나?

Python의 `len()` 함수와 문자열 포맷팅(`:<20`)은 **문자의 개수**만 세고, **터미널 표시 너비**는 고려하지 않습니다.

```python
len("카메라")  # 3 (문자 개수)
get_display_width("카메라")  # 6 (실제 터미널 너비)
```

### 다른 언어에서는?

대부분의 동아시아 언어(한글, 중국어, 일본어 등)는 2칸을 차지합니다:
- 한글: "안녕하세요" → 10칸
- 중국어: "你好" → 4칸
- 일본어: "こんにちは" → 10칸

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

**터미널에서 한글 테이블이 완벽하게 정렬됩니다!**

- ✅ 한글 문자 너비(2칸) 정확히 계산
- ✅ 영문 문자 너비(1칸) 정확히 계산
- ✅ ANSI 색상 코드 처리
- ✅ 모든 테이블에서 정확한 정렬
- ✅ 터미널에서 깔끔한 출력

이제 **터미널에서도 테이블 정렬이 완벽하게** 표시됩니다! 🎊

