#####################
# 작성일 : 2026-07-15
# 작성자 : 이준영
# 내용 : 파이썬 실습 1 - 리스트/딕셔너리 컴프리헨션, Counter, defaultdict, 제너레이터
#####################

import json
import sys
from collections import Counter, defaultdict
    
### 1) 리스트/딕셔너리 컴프리헨션

# json 파일 읽기
try:
    with open('Python_Practice1_Data.json', 'r', encoding='utf-8') as f:
        sales = json.load(f)
except FileNotFoundError:
    print("파일을 찾을 수 없습니다.")
except PermissionError:
    print("파일을 읽을 권한이 없습니다.")
except json.JSONDecodeError:
    print("JSON 파일 형식이 올바르지 않습니다.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")

# 지역 별 매출 합계 계산 (1000 이상만)
regions = {sale['region'] for sale in sales}
dict = {
    region: sum(int(sale["amount"]) for sale in sales if int(sale["amount"]) >= 1000)
    for region in regions
}
print("지역별 총매출", dict)

### 2) Counter + defaultdict
count = Counter(sale['region'] for sale in sales)
group = defaultdict(list)
for sale in sales:
    group[sale['region']].append(sale['amount'])

print("Counter 지역별 거래 건수", count)
print("defaultdict 카테고리별 amount 리스트", group)

### 3) 제너레이터 - 메모리 비교
def read_rows(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for row in data:
                if row["amount"] > 1000:
                    yield row
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    except PermissionError:
        print("파일을 읽을 권한이 없습니다.")
    except json.JSONDecodeError:
        print("JSON 파일 형식이 올바르지 않습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

total = sum(row["amount"] for row in read_rows('Python_Practice1_Data.json'))
print("total:", total)
# 메모리 비교
# 제너레이터로 메모리 계산
gen = read_rows('Python_Practice1_Data.json')
print("Generator 메모리:", sys.getsizeof(gen), "bytes")

# 리스트로 메모리 계산
with open('Python_Practice1_Data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    rows = [row for row in data if row["amount"] > 1000]
print("List 메모리:", sys.getsizeof(rows), "bytes")

### 4) 종합 - 월별 카테고리 매출 집계

grouped = defaultdict(int)

for sale in sales:
    grouped[(sale["month"], sale["category"])] += sale["amount"]

result = {k: v for k, v in grouped.items()}

print("월별 카테고리 매출 집계", result)