# 포트 Fallback 메커니즘 업데이트

## 📅 업데이트 날짜
2024-10-27 (v2.1)

## 🎯 변경 이유
사용자 환경에서 포트 2222를 기본값으로 사용하며, 실패 시 표준 포트 22로 자동 fallback 필요

---

## ✅ 변경 사항

### 1. 포트 기본값 변경
```python
# 이전 (v2)
def __init__(self, host: str, username: str, password: str, 
             port: int = 22, timeout: int = 30):

# 변경 후 (v2.1)
def __init__(self, host: str, username: str, password: str, 
             port: int = 2222, timeout: int = 30):
    self.fallback_port = 22  # fallback 포트 추가
```

### 2. 포트 Fallback 로직 구현
```python
def connect(self) -> bool:
    """SSH 연결 (포트 fallback 지원)"""
    # 1차 시도: 설정된 포트 (기본 2222)
    try:
        self.ssh.connect(self.host, port=self.port, ...)
        self.connected_port = self.port
        return True
    except Exception as e:
        first_error = str(e)
        
        # 2차 시도: fallback 포트 (22)
        if self.port != self.fallback_port:
            try:
                self.ssh.connect(self.host, port=self.fallback_port, ...)
                self.connected_port = self.fallback_port
                self.warnings.append(f"포트 {self.port} 실패, 포트 {self.fallback_port}로 연결 성공")
                return True
            except Exception as e2:
                self.errors.append(f"SSH 연결 실패 (포트 {self.port}: {first_error}, 포트 {self.fallback_port}: {str(e2)})")
                return False
```

### 3. 연결 포트 정보 표시
```python
# 연결 시도 시
print_info(f"연결 정보: {username}@{host}:{port} (실패 시 포트 22로 재시도)")

# 연결 성공 시
if checker.connected_port:
    print_pass(f"SSH 연결 성공 (포트 {checker.connected_port})")
```

---

## 📊 동작 시나리오

### 시나리오 1: 포트 2222로 성공
```
ℹ 연결 정보: admin@192.168.10.30:2222 (실패 시 포트 22로 재시도)
ℹ SSH 연결 테스트 중...
✓ SSH 연결 성공 (포트 2222)
```

### 시나리오 2: 포트 2222 실패 → 포트 22로 성공
```
ℹ 연결 정보: admin@192.168.10.30:2222 (실패 시 포트 22로 재시도)
ℹ SSH 연결 테스트 중...
⚠ 포트 2222 실패, 포트 22로 연결 성공
✓ SSH 연결 성공 (포트 22)
```

### 시나리오 3: 양쪽 모두 실패
```
ℹ 연결 정보: admin@192.168.10.30:2222 (실패 시 포트 22로 재시도)
ℹ SSH 연결 테스트 중...
✗ 연결 실패: SSH 연결 실패 (포트 2222: Connection refused, 포트 22: Connection refused)
```

---

## 🎯 장점

### 1. 유연성
- 사용자 환경에 맞는 포트(2222) 우선 사용
- 표준 포트(22)로 자동 fallback

### 2. 투명성
- 실제 연결된 포트 정보 표시
- 사용자가 어떤 포트로 연결되었는지 명확히 알 수 있음

### 3. 안정성
- 한 포트 실패해도 다른 포트로 연결 시도
- 다양한 Synology 설정 환경 대응

---

## 📝 설정 파일 업데이트

### env.example
```bash
# NAS 설정
NAS_IP=192.168.10.30
NAS_USER=admin2k
NAS_PASSWORD="Edge4IUU#Nas"
NAS_PORT=2222  # Synology 커스텀 SSH 포트 (실패 시 22로 재시도)
```

---

## 🔧 추가 개선 사항

### 연결 정보에 포트 추가
```python
result['connected_port'] = checker.connected_port
```
- 결과 딕셔너리에 실제 연결된 포트 저장
- 리포트에서 연결 포트 확인 가능

---

## ✅ 체크리스트

- [x] 포트 기본값 2222로 변경
- [x] Fallback 포트 22 추가
- [x] 포트 fallback 로직 구현
- [x] 연결된 포트 정보 표시
- [x] 경고 메시지 추가
- [x] 오류 메시지에 양쪽 포트 정보 포함
- [x] env.example 주석 업데이트
- [x] 린터 검사 통과

---

## 🎉 결과

**포트 2222를 기본값으로 사용하며, 실패 시 자동으로 포트 22로 재시도하는 견고한 연결 메커니즘 완성!**

사용자 환경의 특수성을 반영하면서도, 다양한 Synology 설정 환경에 대응할 수 있는 유연한 구조가 되었습니다.

---

*이 업데이트는 사용자 피드백을 반영하여 작성되었습니다.*

