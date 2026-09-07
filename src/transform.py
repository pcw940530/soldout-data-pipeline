import pandas as pd


def load_raw_data():
    df = pd.read_csv(
        "data/raw/soldout_raw.csv"
    )

    print(
        f"[INFO] Raw 데이터 불러오기 완료: "
        f"{len(df):,}건"
    )

    return df


def inspect_data(df):
    print("\n[INFO] 데이터 기본 정보")
    print(df.info())

    print("\n[INFO] 컬럼별 결측치 개수")
    print(df.isnull().sum())

    print("\n[INFO] 즉시구매가 원본 값")
    print(df["즉시구매가"])


def transform_data(df):
    df = df.copy()

    df["즉시구매가"] = (
        df["즉시구매가"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False)
    )

    df["즉시구매가"] = pd.to_numeric(
        df["즉시구매가"],
        errors="coerce"
    )

    df["최근거래가"] = (
        df["최근거래가"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("원", "", regex=False)
    )

    df["최근거래가"] = pd.to_numeric(
        df["최근거래가"],
        errors="coerce"
    )
    return df

def save_staging_data(df):
    df.to_csv(
        "data/staging/soldout_staging.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\n[INFO] Staging 데이터 저장 완료: "
        f"{len(df):,}건"
    )
    
if __name__ == "__main__":
    df = load_raw_data()

    inspect_data(df)

    df = transform_data(df)

    print("\n[INFO] 정제 후 즉시구매가")
    print(df["즉시구매가"])

    save_staging_data(df)