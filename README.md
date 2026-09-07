# Shoe Data Pipeline

신발 편집샵의 상품 데이터를 동적으로 수집하고, 전처리와 품질검증을 거쳐 MySQL에 적재하는 데이터 파이프라인 프로젝트입니다.

단순히 웹 데이터를 크롤링하는 것에서 끝내지 않고,

**데이터 수집 → Raw 저장 → 전처리 → 품질검증 → MySQL 적재**

과정을 하나의 파이프라인으로 구성하는 것을 목표로 구현했습니다.

---

## 1. 프로젝트 개요

신발 편집샵에서 브랜드별 상품 정보를 Selenium을 이용해 동적으로 수집합니다.

수집한 원본 데이터는 CSV 형태로 저장하고, Pandas를 이용해 가격 등의 데이터를 전처리합니다.

전처리가 완료된 데이터는 별도의 Staging 데이터로 관리하며, 데이터 품질검사를 통과한 데이터는 최종적으로 MySQL 데이터베이스에 적재합니다.

전체 과정은 `main.py`를 통해 순차적으로 실행할 수 있도록 구성했습니다.

---

## 2. 주요 기능

현재 구현된 주요 기능은 다음과 같습니다.

* Selenium 기반 동적 웹 크롤링
* 브랜드별 상품 데이터 수집
* 상품 상세페이지 데이터 수집
* 상품명 추출
* 즉시구매가 추출
* 최근거래가 추출
* Raw 데이터 CSV 저장
* Pandas 기반 데이터 전처리
* Staging 데이터 생성
* 데이터 품질검증
* MySQL 데이터 적재
* 동일 상품 재수집 시 최신 데이터 업데이트
* 전체 데이터 파이프라인 자동 실행

---

## 3. 수집 대상

현재 다음 브랜드의 신발 상품을 대상으로 데이터를 수집합니다.

* 뉴발란스
* 아식스
* 나이키
* 살로몬

수집할 상품 개수는 크롤러 설정값을 통해 조절할 수 있도록 구성했습니다.

```python
MAX_PRODUCTS_PER_BRAND = 1
```

예를 들어 브랜드별 최대 100개 상품을 수집하려면 다음과 같이 변경할 수 있습니다.

```python
MAX_PRODUCTS_PER_BRAND = 100
```

스크롤 횟수 역시 별도의 설정값으로 관리합니다.

```python
SCROLL_COUNT = 1
```

이를 통해 테스트 단계에서는 소량의 데이터를 빠르게 확인하고, 이후 수집량을 단계적으로 증가시킬 수 있습니다.

---

## 4. 수집 데이터

상품별로 다음 데이터를 수집합니다.

| 컬럼    | 설명              |
| ----- | --------------- |
| 브랜드명  | 상품 브랜드          |
| 상품명   | 상품의 한글 상품명      |
| 즉시구매가 | 현재 즉시 구매 가능한 가격 |
| 최근거래가 | 가장 최근에 거래된 가격   |
| URL   | 상품 상세페이지 주소     |

수집 예시:

```text
브랜드명: 살로몬
상품명: 살로몬 XA 프로 3D V9 GTX 블랙 팬텀 퓨터 (와이드)
즉시구매가: 249000
최근거래가: 249000
```

---

## 5. 데이터 파이프라인

전체 데이터 처리 과정은 다음과 같습니다.

```text
Shoe E-commerce Platform
        ↓
Selenium Crawling
        ↓
Raw Data
        ↓
Data Transform
        ↓
Staging Data
        ↓
Data Quality Check
        ↓
MySQL
```

실제 파일 기준으로 보면 다음과 같습니다.

```text
crawler.py
    ↓
data/raw/soldout_raw.csv
    ↓
transform.py
    ↓
data/staging/soldout_staging.csv
    ↓
quality.py
    ↓
database.py
    ↓
MySQL
```

이 과정은 `main.py`에서 순서대로 실행됩니다.

---

## 6. 프로젝트 구조

```text
soldout_pipeline/
│
├── main.py
├── README.md
├── .env
├── .gitignore
│
├── src/
│   ├── crawler.py
│   ├── transform.py
│   ├── quality.py
│   └── database.py
│
└── data/
    ├── raw/
    │   └── soldout_raw.csv
    │
    └── staging/
        └── soldout_staging.csv
```

> 기존 `pipeline.py`는 프로젝트의 메인 실행 파일임을 명확하게 하기 위해 `main.py`로 변경했습니다.

---

## 7. 주요 파일 설명

### `main.py`

전체 데이터 파이프라인을 실행하는 메인 파일입니다.

각 모듈의 기능을 순서대로 호출합니다.

```text
1. Crawling
2. Transform
3. Quality Check
4. Database Load
```

따라서 각 Python 파일을 개별적으로 실행하지 않고 `main.py` 하나를 실행하여 전체 과정을 처리할 수 있습니다.

---

### `crawler.py`

Selenium을 이용해 신발 편집샵의 상품 데이터를 동적으로 수집합니다.

주요 역할:

* 브랜드별 상품 검색
* 페이지 스크롤
* 상품 목록 탐색
* 상품명 수집
* 상품 상세페이지 접근
* 즉시구매가 수집
* 최근거래가 수집
* 상품 URL 수집

초기에는 상품 목록에 표시되는 가격을 즉시구매가로 사용했지만, 목록에서 표시되는 가격만으로는 실제 가격의 의미를 정확하게 구분하기 어려운 경우가 있었습니다.

이를 개선하기 위해 상품 상세페이지에 직접 접근한 뒤,

```text
즉시 구매가
최근 거래가
```

항목을 기준으로 가격을 구분하여 수집하도록 수정했습니다.

---

### `transform.py`

크롤링을 통해 저장된 Raw 데이터를 분석 및 DB 적재가 가능한 형태로 변환합니다.

대표적으로 가격 문자열을 숫자 데이터로 변환합니다.

```text
249,000원
↓
249000
```

숫자로 변환할 수 없는 데이터는 결측값으로 처리할 수 있도록 구성했습니다.

변환이 완료된 데이터는 다음 경로에 저장됩니다.

```text
data/staging/soldout_staging.csv
```

---

### `quality.py`

전처리가 완료된 데이터를 MySQL에 적재하기 전에 데이터 품질을 검사합니다.

현재 적용된 품질검사 항목은 다음과 같습니다.

* 데이터 건수 검사
* 필수 컬럼 결측치 검사
* 즉시구매가 유효성 검사
* URL 중복 검사

정상 데이터인지 확인한 후 DB 적재 단계로 넘어가도록 구성했습니다.

---

### `database.py`

Staging 데이터를 MySQL 데이터베이스에 적재합니다.

사용 테이블:

```sql
soldout_products
```

테이블 구조:

```sql
CREATE TABLE IF NOT EXISTS soldout_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    브랜드명 VARCHAR(50) NOT NULL,
    상품명 VARCHAR(255) NOT NULL,
    즉시구매가 INT NOT NULL,
    최근거래가 INT NULL,
    URL VARCHAR(500) NOT NULL UNIQUE
);
```

상품 URL에는 `UNIQUE` 제약조건을 적용하여 동일한 상품이 중복으로 생성되는 것을 방지했습니다.

---

## 8. 동일 상품 데이터 업데이트

상품 가격과 최근거래가는 시간이 지나면서 변경될 수 있습니다.

초기에는 동일한 URL이 이미 데이터베이스에 존재하면 데이터를 무시하는 방식으로 처리했지만, 이 경우 새롭게 수집한 가격이 기존 데이터에 반영되지 않는 문제가 있었습니다.

이를 개선하기 위해 다음 방식을 적용했습니다.

```sql
ON DUPLICATE KEY UPDATE
```

현재는 동일한 상품 URL이 다시 수집되면 새로운 행을 중복 생성하는 대신 기존 상품의 데이터를 최신 수집 값으로 갱신합니다.

```text
새로운 URL
→ INSERT

이미 존재하는 URL
→ UPDATE
```

이를 통해 상품을 반복해서 수집하더라도 URL을 기준으로 동일 상품을 관리하면서 최신 정보를 반영할 수 있도록 구성했습니다.

---

## 9. Raw / Staging 데이터 분리

데이터 처리 과정을 명확하게 구분하기 위해 Raw 데이터와 Staging 데이터를 별도로 관리합니다.

### Raw Data

경로:

```text
data/raw/soldout_raw.csv
```

크롤링 직후의 원본 형태에 가까운 데이터를 저장합니다.

예:

```text
249,000원
```

### Staging Data

경로:

```text
data/staging/soldout_staging.csv
```

Raw 데이터를 전처리한 후 품질검사와 DB 적재에 사용할 데이터를 저장합니다.

예:

```text
249000
```

따라서 데이터 흐름은 다음과 같습니다.

```text
웹 데이터
↓
Raw
↓
Transform
↓
Staging
↓
Quality Check
↓
MySQL
```

---

## 10. 환경변수 관리

데이터베이스 접속 정보는 코드에 직접 작성하지 않고 `.env` 파일을 이용하여 관리합니다.

프로젝트 루트에 다음과 같은 `.env` 파일을 생성합니다.

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=본인의_DB_비밀번호
DB_NAME=soldout_db
```

Python에서는 `python-dotenv`를 이용해 환경변수를 불러옵니다.

보안을 위해 `.env` 파일은 Git에 포함하지 않습니다.

`.gitignore` 예시:

```text
.env
__pycache__/
*.pyc
.vscode/
.ipynb_checkpoints/
```

---

## 11. MySQL 설정

파이프라인 실행 전 MySQL에 데이터베이스를 생성합니다.

```sql
CREATE DATABASE soldout_db;
```

데이터 적재 테이블은 Python 코드에서 존재 여부를 확인하고 필요한 경우 생성합니다.

적재 결과는 다음 SQL을 이용해 확인할 수 있습니다.

```sql
USE soldout_db;

SELECT *
FROM soldout_products;
```

---

## 12. 실행 방법

프로젝트 루트에서 `main.py`를 실행합니다.

현재 개발 환경 기준 실행 명령어:

```bash
"/c/ProgramData/miniconda3/envs/crawling/python.exe" main.py
```

정상 실행되면 다음과 같은 순서로 처리됩니다.

```text
[PIPELINE] 크롤링 단계 완료

[PIPELINE] Transform 단계 완료

[PASS] 데이터 건수 검사 통과
[PASS] 필수 컬럼 결측치 검사 통과
[PASS] 즉시구매가 유효성 검사 통과
[PASS] URL 중복 검사 통과

[PIPELINE] Quality 단계 완료

[INFO] MySQL 연결 성공
[INFO] 테이블 생성 완료
[INFO] MySQL 데이터 적재 완료

[PIPELINE] Database 단계 완료
```

---

## 13. 사용 기술

| 구분                   | 기술                     |
| -------------------- | ---------------------- |
| Language             | Python                 |
| Crawling             | Selenium               |
| Data Processing      | Pandas                 |
| Database             | MySQL                  |
| DB Connector         | mysql-connector-python |
| Environment Variable | python-dotenv          |
| Version Control      | Git / GitHub           |

---

## 14. 구현 과정에서 개선한 부분

### 상품명 추출 개선

초기 상품 목록에서는 브랜드명과 상품명이 함께 표시되어 상품명 대신 브랜드명이 저장되는 문제가 있었습니다.

상품 카드의 텍스트 구조를 확인하고 실제 상품명이 위치한 데이터를 기준으로 추출하도록 로직을 수정했습니다.

### 가격 데이터 정확도 개선

상품 목록에서 표시되는 가격만으로는 즉시구매가와 다른 가격 정보를 정확하게 구분하기 어려운 경우가 있었습니다.

상품 상세페이지까지 접근하여 `즉시 구매가`와 `최근 거래가`를 각각 확인하고 수집하도록 개선했습니다.

### 가격 데이터 전처리

크롤링 결과의 가격은 다음과 같은 문자열 형태로 수집됩니다.

```text
122,000원
```

이를 MySQL의 숫자 컬럼에 저장할 수 있도록 Pandas 전처리를 통해 다음과 같이 변환합니다.

```text
122000
```

### 중복 상품 처리 개선

초기에는 동일 URL이 존재할 경우 데이터를 무시했지만, 이 방식에서는 변경된 상품 가격을 반영할 수 없었습니다.

현재는 URL을 고유값으로 사용하면서 동일 상품이 다시 수집될 경우 최신 데이터로 갱신하도록 개선했습니다.

---

## 15. 현재 구현 상태

현재 소량의 상품 데이터를 기준으로 다음 전체 과정이 정상적으로 동작하는 것을 확인했습니다.

```text
상품 검색
↓
상품 정보 수집
↓
상세페이지 접근
↓
즉시구매가 / 최근거래가 수집
↓
Raw CSV 저장
↓
데이터 전처리
↓
Staging CSV 저장
↓
데이터 품질검사
↓
MySQL 적재
```

현재는 브랜드별 소량 수집을 통해 전체 파이프라인의 동작을 검증한 상태입니다.

---

## 16. 향후 개선 계획

다음 단계에서는 수집량을 단계적으로 증가시키면서 파이프라인의 안정성을 개선할 예정입니다.

* 브랜드별 다중 상품 수집 테스트
* 대량 데이터 수집 안정성 확인
* Selenium Stale Element 예외 대응
* `WebDriverWait` 기반 동적 로딩 처리
* 크롤링 예외처리 강화
* 데이터 품질검사 항목 추가
* 수집 시간 기록
* 로그 관리 개선
* 데이터 분석 및 시각화 연계

---

## 17. 프로젝트 목적

이 프로젝트의 목적은 단순히 웹페이지의 데이터를 가져오는 크롤러를 만드는 것이 아니라, 수집된 데이터가 실제 데이터베이스에 저장되기까지의 전체 흐름을 직접 구현하는 것입니다.

```text
Data Collection
      ↓
Raw Data
      ↓
Data Transform
      ↓
Staging Data
      ↓
Quality Check
      ↓
Database
```

이를 통해 데이터 수집, 전처리, 품질관리, 데이터베이스 적재로 이어지는 기본적인 데이터 파이프라인 구조를 직접 구현하고 이해하는 것을 목표로 합니다.
