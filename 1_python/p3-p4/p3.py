#####################
# 작성일 : 2026-07-16
# 작성자 : 이준영
# 내용 : 파이썬 실습 3 - Pandas, Polars, DuckDB SQL 비교
#      1. Pandas EDA 탐색 + 이상치 처리
#      2. Pandas groupby를 이용한 뒤 named aggregation 집계
#      3. Polars Lazy API로 동일 집계 작성
#      4. DuckDB SQL 동일 집계 작성
#      5. 위 세 도구 성능 비교(timeit)
# 중요 내용 : timeit 은 10번 실행하여 평균 시간을 비교
#           각 도구의 문법이 다른 부분에 집중
#           모든 결측치 제거는 IQR 이상치 계산값인 lo, hi를 재사용
#           Polars < Pandas < DuckDB 순으로 시간 결과
#####################

# import
import pandas as pd
import polars as pl
import duckdb
import timeit


### 1_1. Pandas EDA 탐색

# csv 파일 불러오기
try:
    df = pd.read_csv('sales_100k.csv')
    print("파일 로드 성공")
except Exception as e:
    print(f"오류 발생: {e}")

# EDA(탐색적 분석 기법) 탐색
df.info()         # 타입, 결측, 메모리
df.isnull().sum() # 널타입 수 확인

# 결측치 파악
print(df.isna().sum()) # region : 10000, category : 8000, amount : 5000

### 1_2. IQR 이상치 탐지 (숫자 데이터에서 사용)

Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1

# 정상 기준 최소(lo) 최대치(hi)
lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR

# 이상치 제거 : lo hi 값 사이만 남김
df_clean = df[df['amount'].between(lo, hi)]

print(f'이상치 {(~df["amount"].between(lo, hi)).sum()}건 제거')

### 2. Pandas groupby -> named aggregation 계산

group = df.groupby(['region', 'category']).agg(
    total=('amount', 'sum'),
    mean=('amount', 'mean'),
    count=('amount', 'count')
).reset_index() # groupby를 하면 해당 컬럼이 인덱스로 변환됨->reset_index함수로 다시 컬럼으로 사용가능

# 내림차순 정렬 (default는 오름차순임 (ascending-True))
# 컬럼을 여러 개 사용할 때 : 맨 앞 컬럼인 region 기준 정렬 이후 같은것은 category 기준 정렬됨 
group = group.sort_values(by='total', ascending=False)

print(f'Pandas 결과 {group}')

### 3. Polars Lazy API로 동일 집계 작성

# scancsv - filter - group by - agg - sort - collect
lazy_result = (
    pl.scan_csv('sales_100k.csv',
                schema_overrides={'amount': pl.Float64})
    .filter(pl.col('amount').is_between(lo, hi)) # 필터를 통해서 결측치 제거 (앞의 이상치 재사용)
    .group_by(['region', 'category'])
    .agg([pl.col('amount').sum().alias('total'),
          pl.col('amount').mean().alias('mean'),
          pl.len().alias('count')]) # pandas 버전 변경으로 count -> len
    # lazy 내림차순 descending=True, 오름차순 descending=False
    .sort('total', descending=True)
    .collect()
)
print(f'Lazy 결과 {lazy_result}')

### 4. DuckDB SQL 동일 집계 작성

duck_result = duckdb.sql(f"""
    select region, category,
        sum(amount) as total,
        avg(amount) as mean,
        count(*) as count
    from 'sales_100k.csv'
    where amount between {lo} and {hi}
    group by region, category
    order by total desc""").df()

print(f'DuckSQL 결과 {duck_result}')

### 5. timeit 시간 비교

# 모두 10번씩 실행
# pandas 시간
pandas_time = timeit.timeit(
    "df.groupby(['region','category']).agg(total=('amount','sum'), mean=('amount','mean'), count=('amount','count')).reset_index()",
    globals=globals(),
    number=10
)

# polars 시간
polars_time = timeit.timeit(
    "pl.scan_csv('sales_100k.csv', schema_overrides={'amount': pl.Float64}).group_by(['region','category']).agg(total=pl.col('amount').sum(), mean=pl.col('amount').mean(), count=pl.len()).collect()",
    globals=globals(),
    number=10
)

# duckdb 시간
duckdb_time = timeit.timeit(
    """
duckdb.sql(\"\"\"
SELECT region, category,
       SUM(amount) AS total,
       AVG(amount) AS mean,
       COUNT(*) AS count
FROM 'sales_100k.csv'
GROUP BY region, category
\"\"\").df()
""",
    globals=globals(),
    number=10
)
print('시간 비교')
print(f"Pandas : {pandas_time/10:.6f}s")
print(f"Polars : {polars_time/10:.6f}s")
print(f"DuckDB : {duckdb_time/10:.6f}s")