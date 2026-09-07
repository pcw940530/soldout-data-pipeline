import pandas as pd


def load_staging_data():
    df = pd.read_csv(
        "data/staging/soldout_staging.csv"
    )

    print(
        f"[INFO] Staging 데이터 불러오기 완료: "
        f"{len(df):,}건"
    )

    return df


if __name__ == "__main__":
    df = load_staging_data()

    print(df)

def validate_row_count(df):
    if len(df) == 0:
        raise ValueError(
            "[ERROR] 데이터가 0건입니다."
        )

    print(
        f"[PASS] 데이터 건수 검사 통과: "
        f"{len(df):,}건"
    )

def validate_required_columns(df):
    required_columns = [
        "브랜드명",
        "상품명",
        "즉시구매가",
        "URL"
    ]

    missing_counts = (
        df[required_columns]
        .isnull()
        .sum()
    )

    if missing_counts.sum() > 0:
        raise ValueError(
            f"[ERROR] 필수 컬럼 결측치 발견\n"
            f"{missing_counts}"
        )

    print(
        "[PASS] 필수 컬럼 결측치 검사 통과"
    )

def validate_price(df):
    invalid_price = (
        df["즉시구매가"].isnull()
        | (df["즉시구매가"] <= 0)
    )

    if invalid_price.any():
        raise ValueError(
            "[ERROR] 비정상적인 즉시구매가가 존재합니다."
        )

    print(
        "[PASS] 즉시구매가 유효성 검사 통과"
    )

def validate_duplicate_url(df):
    duplicate_count = df["URL"].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"[ERROR] 중복 URL이 "
            f"{duplicate_count}건 존재합니다."
        )

    print(
        "[PASS] URL 중복 검사 통과"
    )
    
if __name__ == "__main__":
    df = load_staging_data()

    validate_row_count(df)

    validate_required_columns(df)

    validate_price(df)

    validate_duplicate_url(df)