from src.crawler import create_driver, crawl_soldout, save_raw_data
from src.transform import load_raw_data, transform_data, save_staging_data
from src.quality import (
    load_staging_data,
    validate_row_count,
    validate_required_columns,
    validate_price,
    validate_duplicate_url
)
from src.database import (
    create_connection,
    create_table,
    load_staging_data as load_db_staging_data,
    insert_data
)

def run_crawler():
    driver = create_driver()

    try:
        results = crawl_soldout(driver)
        df = save_raw_data(results)

        print(f"[PIPELINE] 크롤링 단계 완료: {len(df):,}건")

    finally:
        driver.quit()

def run_transform():
    df = load_raw_data()

    df = transform_data(df)

    save_staging_data(df)

    print(f"[PIPELINE] Transform 단계 완료: {len(df):,}건")
    
def run_quality():
    df = load_staging_data()

    validate_row_count(df)
    validate_required_columns(df)
    validate_price(df)
    validate_duplicate_url(df)

    print("[PIPELINE] Quality 단계 완료")

def run_database():
    connection = create_connection()

    try:
        create_table(connection)

        df = load_db_staging_data()

        insert_data(connection, df)

        print("[PIPELINE] Database 단계 완료")

    finally:
        connection.close()
        
if __name__ == "__main__":
    run_crawler()
    run_transform()
    run_quality()
    run_database()