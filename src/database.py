import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def create_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("[INFO] MySQL 연결 성공")

    return connection


def create_table(connection):
    cursor = connection.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS soldout_products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        브랜드명 VARCHAR(50) NOT NULL,
        상품명 VARCHAR(255) NOT NULL,
        즉시구매가 INT NOT NULL,
        최근거래가 INT NULL,
        URL VARCHAR(500) NOT NULL UNIQUE
    )
    """

    cursor.execute(query)
    connection.commit()
    cursor.close()

    print("[INFO] 테이블 생성 완료")


def load_staging_data():
    df = pd.read_csv(
        "data/staging/soldout_staging.csv"
    )

    print(
        f"[INFO] Staging 데이터 불러오기 완료: "
        f"{len(df):,}건"
    )

    return df


def insert_data(connection, df):
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO soldout_products
    (브랜드명, 상품명, 즉시구매가, 최근거래가, URL)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        브랜드명 = VALUES(브랜드명),
        상품명 = VALUES(상품명),
        즉시구매가 = VALUES(즉시구매가),
        최근거래가 = VALUES(최근거래가)
    """

    for _, row in df.iterrows():
        recent_price = (
            None
            if pd.isna(row["최근거래가"])
            else int(row["최근거래가"])
        )

        values = (
            row["브랜드명"],
            row["상품명"],
            int(row["즉시구매가"]),
            recent_price,
            row["URL"]
        )

        cursor.execute(
            insert_query,
            values
        )

    connection.commit()
    cursor.close()

    print(
        f"[INFO] MySQL 데이터 적재 완료: "
        f"{len(df):,}건"
    )


if __name__ == "__main__":
    connection = create_connection()

    create_table(connection)

    df = load_staging_data()

    insert_data(
        connection,
        df
    )

    connection.close()

    print("[INFO] MySQL 연결 종료")

