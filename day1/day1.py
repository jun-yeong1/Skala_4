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
from pydantic import BaseModel, ValidationError, Field

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

results = asyncio.run(fetch_all(urls))

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

# valid, errors 리스트 선언
valid = []
errors = []

# 검증

# 서울 3일 시간대별 기온, 강수확률 검증
try:
    weather = Weather.model_validate(results[0])
    valid.append(weather.model_dump())
except ValidationError as e:
    errors.append(e.errors())

try:
    country = Country.model_validate(results[1])
    valid.append(country.model_dump())
except ValidationError as e:
    errors.append(e.errors())

try:
    ip = IPInfo.model_validate(results[2])
    valid.append(ip.model_dump())
except ValidationError as e:
    errors.append(e.errors())


# 이중 dict 풀어주기 (csv 저장 시, dict 안에 dict가 있으면 오류 발생)
records = []

for item in valid:
    record = {}
    # 서울 3일 시간대별 기온, 강수확률 api 에서 hourly dict 풀기
    if "hourly" in item:
        record["latitude"] = item["latitude"]
        record["longitude"] = item["longitude"]
        record["temperature_count"] = len(item["hourly"]["temperature_2m"])
        record["precipitation_count"] = len(item["hourly"]["precipitation_probability"])
    # 한국 국가 정보 api 에서 name dict 풀기
    elif "name" in item:
        record["country"] = item["name"]["common"]
        record["population"] = item["population"]
    else:
        record = item

    records.append(record)

df = pd.DataFrame(records)

# CSV 저장 시간

start = time.perf_counter()

df.to_csv("valid.csv", index=False, encoding="utf-8-sig")

csv_write = time.perf_counter() - start

# Parquet 저장 시간
start = time.perf_counter()

df.to_parquet("valid.parquet", index=False)

parquet_write = time.perf_counter() - start


# CSV 읽기 시간
start = time.perf_counter()

csv_df = pd.read_csv("valid.csv")

csv_read = time.perf_counter() - start


# Parquet 읽기 시간
start = time.perf_counter()

parquet_df = pd.read_parquet("valid.parquet")

parquet_read = time.perf_counter() - start

# 건수 검증
assert len(csv_df) == len(valid)
assert len(parquet_df) == len(valid)

print("\n===== 결과 =====")
print("CSV 건수      :", len(csv_df))
print("Parquet 건수  :", len(parquet_df))

print("\n===== 쓰기 시간 =====")
print(f"CSV      : {csv_write:.6f} sec")
print(f"Parquet  : {parquet_write:.6f} sec")

print("\n===== 읽기 시간 =====")
print(f"CSV      : {csv_read:.6f} sec")
print(f"Parquet  : {parquet_read:.6f} sec")