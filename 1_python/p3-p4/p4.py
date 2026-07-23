#####################
# 작성일 : 2026-07-16
# 작성자 : 이준영
# 내용 : 파이썬 실습 4 - 시각화 4종, 통계 검정, sklearn pipeline
#      1. Pandas EDA 시각화 4종 (히스토그램+KDE, 박스플롯, 월별 라인, 상관 히트맵)
#      2. 통계 검정 (t-test, 카이제곱)
#      3. sklearn Pipeline 구성과 저장
#      4. Plotly 인터랙티브 차트 저장
# 중요 내용 : 폰트 오류 발생 -> mac 전용 한글 폰트 불러오기로 해결
#          서브 플롯 2x2 등 생성했을 때 axes[0,0] 처럼 겹치지 않는 위치로 정의
#          t-test, 카이제곱의 p_value의 의미 0.05 보다 작아야 통계적 의미 
#####################

# import
import pandas as pd
import polars as pl
import duckdb
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats # t-test
from scipy.stats import chi2_contingency # 카이제곱
import plotly.express as px  # plotly 인터랙티브 시각화

# 폰트 오류 해결
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# csv 파일 불러오기
try:
    df = pd.read_csv('sales_100k.csv')
    print("파일 로드 성공")
except Exception as e:
    print(f"오류 발생: {e}")

# EDA(탐색적 분석 기법) 탐색
#df.info()         # 타입, 결측, 메모리
#df.isnull().sum() # 널타입 수 확인

# 결측치 파악
# region : 10000, category : 8000, amount : 5000

# IQR 이상치 탐지 (숫자 데이터에서 사용)
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1

# 정상 기준 최소(lo) 최대치(hi)
lo, hi = Q1 - 1.5*IQR, Q3 + 1.5*IQR

# 이상치 제거 : lo hi 값 사이만 남김
df = df[df['amount'].between(lo, hi)]

### 1. Pandas EDA 시각화 (2x2 서브플롯)

# 2x2 서브플롯으로 사이즈 정의
fig, axes = plt.subplots(2,2,figsize=(12,10))

# 1.1 히스토그램 + KDE (0,0 위치)
sns.histplot(data=df, x='amount', kde=True, ax=axes[0,0])

# 1.2 박스플롯 (0,1 위치)
sns.boxplot(data=df, x='amount', hue='category', ax=axes[0,1])

# 1.3 월별 라인 (바 차트) (1,0 위치)

# 1.3.1. 'data' 컬럼에서 월 추출
df['order_date'] = pd.to_datetime(df['order_date'])

# 1.3.2. 해당 월 전체 amount 값 구하기
monthly = (
    df.groupby(df['order_date'].dt.month)['amount']
      .sum()
)
months = monthly.index
revenue = monthly.values
axes[1,0].bar(months, revenue, color='steelblue', alpha=0.8)

# 1.3.1 그래프 이름 설정
axes[1,0].set_title('월별 매출 추이')

# 1.4 상관 히트맵 (1,1 위치)
corr = df.select_dtypes('number').corr() # corr 설정
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=axes[1,1])

# plt 출력
plt.tight_layout(); #plt.show()


### 2. 통계 검정 t-test + 카이제곱

# 2.1. 서울 부산 평균 매출 차이 ttest

# 각 지역별 평균 매출 구하기
group_seoul = df[df['region']=='서울']['amount']
group_busan = df[df['region']=='부산']['amount']

# t-test
t, p = stats.ttest_ind(group_seoul, group_busan)
print(f't={t:.3f}, p={p:.3f}')

# t-test 결과 분석
print('t-test 결과 분석: ', end="")
if p < 0.05:
    print('통계적 유의미한 차이')
else:
    print('차이 없음')

# 2.2 카이제곱 (지역과 카테고리 독립성)

ct = pd.crosstab(df['region'], df['category'])
chi2, p_value, dof, expected = chi2_contingency(ct)

# 카이제곱 값이 크면 처이가 크다.
# p_value
print(f'카이제곱={chi2:.3f}, p_value={p_value:.3f}')
# 카이제곱 p_value 결과 분석
print('카이제곱 p_value 결과 분석: ', end="")
if p_value < 0.05:
    print('통계적 유의미한 차이')
else:
    print('차이 없음')


### 3. sklearn Pipeline 구성 및 저장

# import
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
import joblib
from sklearn.model_selection import train_test_split


# 테스트 사용 컬럼 지정
X = df[['region', 'category']]
y = df['amount']

# 학습 테스트 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

num_cols = []
cat_cols = ['region', 'category']

# 전처리
preproc = ColumnTransformer([
    ('num', StandardScaler(), num_cols),
    ('cat', OneHotEncoder(), cat_cols)])

# 모델 (파이프라인 생성)
model = Pipeline([
    ('prep', preproc),
    ('reg', Ridge(alpha=1.0))])

# 모델 학습 및 테스트 결과 출력
model.fit(X_train, y_train)
print(f'R2: {model.score(X_test, y_test):.3f}')
joblib.dump(model, 'model.pkl')   # 저장
loaded = joblib.load('model.pkl') # 로딩

### 4. Plotly 인터랙티브 차트 저장

# 바 차트에서 사용한 monthly 변수 응용
monthly_2 = (
    df.groupby([
        df['order_date'].dt.month,
        'region',
        'category'
    ])['amount']
    .sum()
    .reset_index()
)
# 사용될 컬럼 제정의
monthly_2.columns = ['months', 'region', 'category', 'revenue']

# 지역 카테고리별 총매출 express 막대 차트
fig2 = px.bar(monthly_2, 
    x='months',
    y='revenue',
    color='category',
    facet_col='region',
    title='지역.카테고리별 월 매출')

# HTML 저장
fig2.write_html('p4.html')