---
name: project-health
description: "프로젝트 헬스체크 — 파일 무결성/폰트/중복/디스크 종합 점검 (헬스, 점검, 상태, health)"
---

# Project Health — 프로젝트 헬스체크

프로젝트 파일 무결성, PDF 폰트, 중복 파일, 디스크 사용량을 종합 점검.

## 점검 항목

### 1. PDF 폰트 무결성
Research/ 내 모든 생성 PDF에서 한글 폰트 임베딩 확인:
```python
import pypdf
# 'Unknown' 폰트만 있는 PDF = 깨진 파일
```
- NanumSquareOTF 또는 유효한 한글 폰트 존재 확인
- 깨진 파일 수와 목록 출력

### 2. 3종 세트 완성도
.md 파일마다 .pdf, .docx 대응 파일 존재 확인.

### 3. 중복 파일 검사
- Reference/ vs Research/papers/ 간 중복
- 루트 vs 하위 디렉토리 간 중복
- md5 해시로 정확한 중복 확인

### 4. orphan 파일
- .tmp, .bak, .swp 등 임시 파일
- test_*, *_test.* 등 테스트 잔여물

### 5. 디스크 사용량
```bash
du -sh Research/ Research/papers/ Pre/ Reference/ Templates/
```

### 6. Git 상태
- .gitignore 적용 확인
- 대용량 파일 추적 여부

## 출력 형식

```
| 항목            | 상태 | 상세                     |
|-----------------|------|--------------------------|
| PDF 폰트        | ✅   | 94/94 정상                |
| 3종 세트        | ⚠️   | 2개 .docx 누락            |
| 중복 파일        | ✅   | 0개                       |
| orphan 파일      | ✅   | 0개                       |
| 디스크 사용량    | ✅   | 총 450MB                  |
| Git 상태        | ✅   | .gitignore 적용 중        |
| 종합            | ⚠️   | 1건 주의                   |
```

## 자동 수정 (--fix)
- 깨진 PDF: md에서 재생성 (fpdf2 + NanumSquareOTF)
- orphan 파일: 삭제 확인 후 제거
- 중복 파일: 하나만 남기고 제거
