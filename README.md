# Soldout Data Pipeline

무신사 솔드아웃의 신발 상품 데이터를 동적으로 수집하고, 전처리와 품질검증을 거쳐 MySQL에 적재하는 데이터 파이프라인 프로젝트입니다.

## 프로젝트 개요

무신사 솔드아웃에서 브랜드별 신발 상품 정보를 Selenium으로 수집한 뒤, Pandas를 이용해 데이터를 정제하고 품질을 검사한 후 MySQL 데이터베이스에 저장합니다.

단순 크롤링에 그치지 않고,

**수집 → 전처리 → 품질검증 → DB 적재**

과정을 하나의 파이프라인으로 구성하는 것을 목표로 진행했습니다.

## 수집 대상

현재 다음 브랜드의 신발 상품 데이터를 수집합니다.

* 뉴발란스
* 아식스
* 나이키
* 살로몬

수집 상품 개수는 코드에서 설정할 수 있습니다.

```python
MAX_PRODUCTS_PER_BRAND = 1
```

예를 들어 브랜드별 100개를 수집하려면 다음과 같이 변경할 수 있습니다.

```python
MAX_PRODUCTS_PER_BRAND = 100
```

## 수집 데이터

상품별로 다음 정보를 수집합니다.

| 컬럼    | 설명              |
| ----- | --------------- |
| 브랜드명  | 상품 브랜드          |
| 상품명   | 상품의 한글 상품명      |
| 즉시구매가 | 현재 즉시 구매 가능한 가격 |
| 최근거래가 | 가장 최근 거래된 가격    |
| URL   | 상품 상세페이지 주소     |

예시:

```text
브랜드명: 살로몬
상품명: 살로몬 XA 프로 3D V9 GTX 블랙 팬텀 퓨터 (와이드)
즉시구매가: 249000
최근거래가: 249000
```

## 데이터 파이프라인

전체 데이터 처리 흐름은 다음과 같습니다.

```text
Musinsa Soldout
        ↓
Selenium Crawling
        ↓
data/raw/soldout_raw.csv
        ↓
Data Transform
        ↓
data/staging/soldout_staging.csv
        ↓
Data Quality Check
        ↓
MySQL
```

각 단계는 독립적인 Python 파일로 분리하고, `pipeline.py`에서 순서대로 실행하도록 구성했습니다.

## 프로젝트 구조

```text
soldout_pipeline/
│
├── pipeline.py
│
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

## 주요 파일 설명

### `crawler.py`

Selenium을 이용하여 무신사 솔드아웃의 데이터를 동적으로 수집합니다.

주요 역할:

* 브랜드 검색
* 상품 목록 탐색
* 상품명 수집
* 상품 상세페이지 접근
* 즉시구매가 수집
* 최근거래가 수집
* 상품 URL 수집

상품 상세페이지의 텍스트를 분석하여 실제 즉시구매가와 최근거래가를 구분하여 수집합니다.

### `transform.py`

Raw 데이터를 분석 및 적재가 가능한 형태로 변환합니다.

예를 들어 가격 데이터는 다음과 같이 변환됩니다.

```text
249,000원
↓
249000
```

`N/A`와 같이 숫자로 변환할 수 없는 값은 결측값으로 처리합니다.

변환된 데이터는 다음 파일에 저장됩니다.

```text
data/staging/soldout_staging.csv
```

### `quality.py`

MySQL에 데이터를 적재하기 전 데이터 품질을 확인합니다.

현재 적용된 품질검사 항목:

* 데이터 건수 확인
* 필수 컬럼 결측치 확인
* 즉시구매가 유효성 확인
* URL 중복 확인

품질검사를 통과한 데이터만 다음 DB 적재 단계로 넘어갑니다.

### `database.py`

전처리와 품질검증을 완료한 데이터를 MySQL에 저장합니다.

사용 테이블:

```sql
soldout_products
```

테이블 구조:

```sql
CREATE TABLE soldout_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    브랜드명 VARCHAR(50) NOT NULL,
    상품명 VARCHAR(255) NOT NULL,
    즉시구매가 INT NOT NULL,
    최근거래가 INT NULL,
    URL VARCHAR(500) NOT NULL UNIQUE
);
```

같은 상품 URL이 이미 존재하는 경우 새 데이터를 무시하지 않고 최신 데이터로 갱신하도록 구성했습니다.

```sql
ON DUPLICATE KEY UPDATE
```

따라서 상품의 가격이 변경된 경우 다시 수집하면 기존 데이터의 가격도 최신 값으로 업데이트됩니다.

### `pipeline.py`

전체 데이터 파이프라인을 실행하는 파일입니다.

실행 순서:

```text
1. Crawling
2. Transform
3. Quality Check
4. Database Load
```

각 파일을 따로 실행하지 않고 `pipeline.py` 하나로 전체 과정을 실행할 수 있습니다.

## Raw / Staging 데이터 분리

본 프로젝트에서는 수집 데이터와 전처리 데이터를 분리하여 관리합니다.

### Raw

```text
data/raw/soldout_raw.csv
```

크롤링 직후의 원본 형태에 가까운 데이터를 저장합니다.

예:

```text
249,000원
```

### Staging

```text
data/staging/soldout_staging.csv
```

전처리가 완료되어 품질검증과 DB 적재가 가능한 데이터를 저장합니다.

예:

```text
249000
```

이를 통해 원본 데이터와 처리된 데이터를 분리하여 확인할 수 있도록 구성했습니다.

## 실행 방법

### 1. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```text
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=본인의_DB_비밀번호
DB_NAME=soldout_db
```

보안을 위해 `.env` 파일은 GitHub에 업로드하지 않습니다.

`.gitignore`

```text
.env
__pycache__/
*.pyc
.vscode/
.ipynb_checkpoints/
```

### 2. MySQL 데이터베이스 생성

```sql
CREATE DATABASE soldout_db;
```

### 3. 파이프라인 실행

현재 프로젝트에서 사용하는 Python 환경 기준 실행 명령어:

```bash
"/c/ProgramData/miniconda3/envs/crawling/python.exe" pipeline.py
```

정상 실행 시 다음과 같은 흐름으로 진행됩니다.

```text
[PIPELINE] 크롤링 단계 완료

[PIPELINE] Transform 단계 완료

[PASS] 데이터 건수 검사 통과
[PASS] 필수 컬럼 결측치 검사 통과
[PASS] 즉시구매가 유효성 검사 통과
[PASS] URL 중복 검사 통과

[PIPELINE] Quality 단계 완료

[INFO] MySQL 연결 성공
[INFO] MySQL 데이터 적재 완료

[PIPELINE] Database 단계 완료
```

## 사용 기술

| 구분                   | 기술                     |
| -------------------- | ---------------------- |
| Language             | Python                 |
| Crawling             | Selenium               |
| Data Processing      | Pandas                 |
| Database             | MySQL                  |
| DB Connector         | mysql-connector-python |
| Environment Variable | python-dotenv          |
| Version Control      | Git / GitHub           |

## 구현 과정에서 개선한 부분

초기에는 상품 목록에서 가격 데이터를 바로 수집했지만, 목록에서 표시되는 가격이 실제 `즉시구매가`가 아닌 경우가 있었습니다.

예를 들어 특정 상품에서는 목록에서 확인한 `190,000원`이 실제로는 즉시판매가였고, 상세페이지에서 확인한 즉시구매가는 `249,000원`이었습니다.

이를 개선하기 위해 상품 상세페이지로 이동한 후 직접 다음 정보를 찾아 수집하도록 변경했습니다.

```text
즉시 구매가
최근 거래가
```

또한 기존에는 동일한 URL이 존재할 경우 `INSERT IGNORE` 방식으로 데이터를 무시했지만, 가격처럼 변경될 수 있는 데이터를 최신 상태로 유지하기 위해 `ON DUPLICATE KEY UPDATE` 방식으로 수정했습니다.

## 현재 상태

현재 구현된 기능:

* Selenium 기반 동적 크롤링
* 브랜드별 상품 수집
* 상품명 추출
* 즉시구매가 추출
* 최근거래가 추출
* Raw 데이터 저장
* 데이터 전처리
* Staging 데이터 저장
* 데이터 품질검증
* MySQL 데이터 적재
* 동일 상품 최신 데이터 업데이트
* 전체 파이프라인 자동 실행

현재는 소량의 데이터를 기준으로 파이프라인 정상 동작을 확인했으며, 이후 수집 상품 수를 단계적으로 늘려 안정성을 테스트할 예정입니다.

## 향후 개선 계획

* 브랜드별 다중 상품 수집 안정성 개선
* 대량 데이터 수집 테스트
* Selenium 예외처리 강화
* WebDriverWait 기반 동적 로딩 처리
* 로그 관리 개선
* 품질검사 항목 추가
* 수집 시간 기록
* 데이터 분석 및 시각화 연계

## 프로젝트 목적

이 프로젝트를 통해 웹에서 데이터를 가져오는 크롤링뿐만 아니라,

```text
데이터 수집
→ 원본 저장
→ 전처리
→ 데이터 품질검증
→ 데이터베이스 적재
```

로 이어지는 데이터 엔지니어링의 기본적인 파이프라인 구조를 직접 구현하고 이해하는 것을 목표로 했습니다.
