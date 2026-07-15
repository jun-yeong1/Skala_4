#####################
# 작성일 : 2026-07-15
# 작성자 : 이준영
# 내용 : 파이썬 통합 실습 1 - 데이터 수집 파이프라인
#      1. 가상환경 세팅
#      2. 비동기로 api 수집
#      3. Pydantic v2로 스키마 검증
#      4. 검증 완료 데이터 -> csv, Parquet 저장 -> 두 파일 읽기/쓰기 시간 비교
#      5. Pytest 스키마 검증 테스트 -> ruff 로 코드 스타일 검사
#####################

import asyncio, httpx
import pandas as pd
import time
from pydantic import BaseModel, ValidationError

### 2. 비동기로 api 호출 및 데이터 수집
# api 호출 함수 정의
async def fetch(client,url):
    try:
        r = await client.get(url, timeout=10)
        return r.json()
    except Exception as e:
        return {'error':str(e)}
    
async def fetch_all(urls):
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# api url 리스트 선언    
urls = ['https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul',
        'https://restcountries.com/v3.1/alpha/KR',
        'http://ip-api.com/json/8.8.8.8']


### 3. Pydantic v2로 스키마 검증

# 서울 3일 시간대별 기온, 강수확률
class Hourly(BaseModel):
    temperature_2m: list[float]
    precipitation_probability: list[int]
class Weather(BaseModel):
    latitude: float
    longitude: float
    hourly: Hourly

# 한국 국가 정보
class CountryName(BaseModel):
    common: str
class Country(BaseModel):
    name: CountryName
    population: int

# ip 기반 지역 정보
class IPInfo(BaseModel):
    country: str
    city: str
    query: str

### 5) 테스트 코드

# 스키마 함수로 변경함 -> 테스트로 이용
def validate_weather(data):
    weather = Weather.model_validate(data).model_dump()
    weather.update(weather.pop("hourly"))
    return weather

def validate_country(data):
    country = Country.model_validate(data).model_dump()
    country["common"] = country.pop("name")["common"]
    return country

def validate_ip(data):
    return IPInfo.model_validate(data).model_dump()

def main():
    results = asyncio.run(fetch_all(urls))

    valid = []
    errors = []

    try:
        valid.append(validate_weather(results[0]))
    except ValidationError as e:
        errors.append(e.errors())

    try:
        # countries API가 리스트를 반환하는 경우
        data = results[1][0] if isinstance(results[1], list) else results[1]
        valid.append(validate_country(data))
    except ValidationError as e:
        errors.append(e.errors())

    try:
        valid.append(validate_ip(results[2]))
    except ValidationError as e:
        errors.append(e.errors())

    df = pd.DataFrame(valid)

    # ---------------- CSV 저장 ----------------
    start = time.perf_counter()
    df.to_csv("valid.csv", index=False, encoding="utf-8-sig")
    csv_write = time.perf_counter() - start

    # ---------------- Parquet 저장 ----------------
    start = time.perf_counter()
    df.to_parquet("valid.parquet", index=False)
    parquet_write = time.perf_counter() - start

    # ---------------- CSV 읽기 ----------------
    start = time.perf_counter()
    csv_df = pd.read_csv("valid.csv")
    csv_read = time.perf_counter() - start

    # ---------------- Parquet 읽기 ----------------
    start = time.perf_counter()
    parquet_df = pd.read_parquet("valid.parquet")
    parquet_read = time.perf_counter() - start

    assert len(csv_df) == len(valid), "CSV 건수 불일치"
    assert len(parquet_df) == len(valid), "Parquet 건수 불일치"

    print(f"Valid : {len(valid)}")
    print(f"Errors : {len(errors)}")

    print("\n===== 결과 =====")
    print("CSV 건수 :", len(csv_df))
    print("Parquet 건수 :", len(parquet_df))

    print("\n===== 쓰기 시간 =====")
    print(f"CSV : {csv_write:.6f} sec")
    print(f"Parquet : {parquet_write:.6f} sec")

    print("\n===== 읽기 시간 =====")
    print(f"CSV : {csv_read:.6f} sec")
    print(f"Parquet : {parquet_read:.6f} sec")


if __name__ == "__main__":
    main()