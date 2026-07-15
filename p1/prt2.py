#####################
# 작성일 : 2026-07-15
# 작성자 : 이준영
# 내용 : 파이썬 실습 2 - 파일 I/O, 예외 처리, pydantc 검증 파이프라인
#####################

import json
import logging
import csv
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

### 1) 예외 처리 + 파일 읽기
# logging 설정
logging.basicConfig(level=logging.INFO)

# json 파일 읽기
def safe_load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            sales = json.load(f)
            logging.info("파일 로딩 성공")
            return sales
    except FileNotFoundError:
        logging.error("None")
    finally:
        print("로딩 종료")

safe_load_json('Python_Practice1_Data.json')

### 2) pydantic v2 스키마 정의
# class 정의
class SalesRecord(BaseModel):
    # min_length=1 임으로 비어있을 수 없게 함
    month: str = Field(min_length=1)
    region: str = Field(min_length=1)
    amount: float = Field(gt=0)
    category: Optional[str] = None

### 3) 검증 파이프라인 (valid / errors 분리)
# 결과 저장 리스트 생성
valid, errors = [], []

# 파일 오픈
try:
    with open('Python_Practice1_Data.json', 'r', encoding='utf-8') as f:
        sales = json.load(f)
        for i in sales:
            # pydantic v2검증
            try:
                # valid
                valid.append(SalesRecord(**i).model_dump())
            except ValidationError as e:
                # errors
                errors.append({"record": i, "error": str(e)})
        print("유효:", len(valid), "건, 오류:", len(errors), "건")
except FileNotFoundError:
    logging.error("None")
finally:
    print("로딩 종료")

### 4) 결과 파일 저장 + 재로딩 확인

# 유효 csv 저장 
with open('valid.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["region", "category", "amount", "month"])
    writer.writeheader() 
    writer.writerows(valid) 

# 오류 json 저장
with open('errors.json', 'w', encoding='utf-8') as f:
    json.dump(errors, f, ensure_ascii=False, indent=4)

# valid.csv 다시 읽기
with open("valid.csv", "r", encoding="utf-8-sig") as f:
    valid_reload = list(csv.DictReader(f))

# errors.json 다시 읽기
with open("errors.json", "r", encoding="utf-8") as f:
    error_reload = json.load(f)

print(f"valid : {len(valid_reload)}건")
print(f"errors : {len(error_reload)}건")