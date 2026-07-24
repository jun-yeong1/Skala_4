# 프로그래밍 기초 과제

> 작성일: 2026년 7월 24일

> 작성자: 울산-1반-이준영

---

## 1. 구현한 기능 목록

차별점 : 남은 시간 계산 후 출력

마감일과 현재 일수를 계산하여 며칠이 남았는지 알려주는 남은 시간 항목을 만들었음.

```javascript
function getDueText(due) {
  if (!due) return "";

  const [y, m, d] = due.split("-").map(Number);

  const target = new Date(y, m - 1, d);
  const today = new Date();

  // 시간 제거
  target.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);

  const diff = target - today;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days > 0) return `D-${days}`;
  if (days === 0) return "오늘";
  return `D+${Math.abs(days)}`;
}
```

- ***

## 2. 실행 방법

- ***

## 3. 어려웠던 점과 해결

1. 학습 목록 정렬화
   문제 : 학습 목록 요소 중 item-check, item-text는 왼쪽에 정렬을 하고, item-day, badge, item-del는 오른쪽 정렬하려 했지만 margin-left, margin-right: auto; 적용되지 않는 문제 발생.
   해결 : margin-right가 오른쪽 정렬이 아니라 오른쪽에 마진을 준다는 의미였고, 왼쪽에 정렬할 요소들도 margin-left를 통해 공간을 확보해줘야 정상 작동되는 것을 파악하여 해결.

- ***

## 4. 미완성 항목
