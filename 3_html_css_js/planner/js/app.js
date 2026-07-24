const form = document.getElementById("goal-form");
const input = document.getElementById("goal-input");
const category = document.getElementById("goal-category");
const dueInput = document.getElementById("goal-due");
const listEl = document.getElementById("goal-list");
const emptyEl = document.getElementById("list-empty");
const errorEl = document.getElementById("form-error");
const tabsEl = document.getElementById("filter-tabs");
const fillEl = document.getElementById("progress-fill");
const textEl = document.getElementById("progress-text");
const searchInput = document.getElementById("goal-search");
const countsEl = document.getElementById("category-counts");

const STORAGE_KEY = "skala-planner";

let goals = load();

let filter = "all";
let searchTerm = "";

// 저장 불러오기 함수
function load() {
    // localStorage : 브라우저에 클라이언트 데이터를 영구 저장하는 빌트인 객체
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : []; // 문자열 → 배열
}

function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(goals));
}

function updateProgress() {
    const total = goals.length;
    const done = goals.filter((g) => g.done).length;
    const percent = total === 0 ? 0 : Math.round((done / total) * 100);

    fillEl.style.width = percent + "%";
    textEl.textContent = `전체 ${total}개 중 ${done}개 완료 (${percent}%)`;
}

const li = document.createElement("li");    // <li></li> 생성
li.className = "item";                      // 클래스 지정
li.textContent = "새 목표";                   // 내용 지정
listEl.appendChild(li);                     // #goal-list의 자식으로 추가
listEl.innerHTML = "";                      // 자식 전체 비우기

// 날짜 업데이트
const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1;
const date = today.getDate();
document.getElementById("today").innerText = `${year}년 ${month}월 ${date}일`;

form.addEventListener("submit", (event) => {
    event.preventDefault(); // 새로고침 방지
    console.log(event.type); // "submit"
});

listEl.addEventListener("click", (event) => {
    console.log(event.target); // 클릭된 바로 그 요소
});

input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") input.value = ""; // Esc로 입력 지우기
})

// 목표 추가
form.addEventListener("submit", (event) => {
    event.preventDefault();
    const title = input.value.trim();
    if (title === "") {
        errorEl.hidden = false;
        input.focus();
        return; // 여기서 중단
    }
    errorEl.hidden = true;
    goals.push({ 
        id: Date.now(),
        title: title,
        category: category.value,
        due: dueInput.value,
        done: false });
    input.value = "";
    save();
    render();
});

// 토글 삭제
listEl.addEventListener("click", (event) => {
    const li = event.target.closest(".item");
    if (!li) return;                          // 목록 여백 클릭이면 무시
    const id = Number(li.dataset.id);
    if (event.target.matches(".item-check")) { // 완료 토글
        const goal = goals.find((g) => g.id === id);
        goal.done = event.target.checked;
        save();
        render();
    }
    if (event.target.matches(".item-del")) {
        goals = goals.filter((g) => g.id !== id);
        save();
        render();
    };
});

// 필터 탭
tabsEl.addEventListener("click", (event) => {
    const tab = event.target.closest(".tab");
    if (!tab) return;
    filter = tab.dataset.filter; // "all" | "active" | "done"
    document.querySelectorAll(".tab").forEach((t) => {
        t.classList.toggle("is-active", t === tab);
    });
    render();
});

// 검색어 입력
searchInput.addEventListener("input", (event) => {
    searchTerm = event.target.value.trim().toLowerCase();
    render();
});

function visible() {
    let items = goals;
    if (filter === "active") return items.filter((g) => !g.done);
    if (filter === "done") return items.filter((g) => g.done);
    if (searchTerm) {
        items = items.filter((g) => g.title.toLowerCase().includes(searchTerm));
    }
    return items;
}

// 분류(HTML/CSS/JS)별 남은(미완료) 개수 집계
function updateCategoryCounts() {
    const categories = ["HTML", "CSS", "JS"];
    countsEl.innerHTML = categories
        .map((cat) => {
            const remaining = goals.filter((g) => g.category === cat && !g.done).length;
            return `<span class="category-count">${cat} 남은 개수: ${remaining}</span>`;
        })
        .join("");
}
// escape : 들어가지 못하는 텍스트 변환해주는 함수
function escapeHtml(text) {
  var map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// 오늘의 팁 불러오기
async function loadTip() {
    const tipEl = document.getElementById("tip");
    try {
        const response = await fetch("data/tips.json");
        if (!response.ok) throw new Error("HTTP " + response.status);
        const tips = await response.json();
        const today = new Date().getDate() % tips.length;
        tipEl.textContent = tips[today];
    } catch (error) {
        tipEl.textContent = "팁을 불러오지 못했습니다.";
        console.error(error);
    }
}

// 마감일에서 남은 일수 계산, 마감일이 오늘이라면 시간 계산 
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

// 랜더링
function render() {
    const items = visible();
    listEl.innerHTML = "";
    items.forEach((goal) => {
        const li = document.createElement("li");
        li.className = goal.done ? "item is-done" : "item";
        li.dataset.id = goal.id;
        li.innerHTML = `
            <label>
                <input type="checkbox" class="item-check" ${goal.done ? "checked" : ""}>
            </label>
            <span class="item-text">${escapeHtml(goal.title)}</span>
            <small class="item-day">남은 시간: ${getDueText(goal.due)} 마감일: ${goal.due}</small>
            <span class="badge">${goal.category}</span>
            <button class="item-del">삭제</button>
        `;
        listEl.appendChild(li);
    });
    emptyEl.hidden = items.length > 0;
    updateProgress();
    updateCategoryCounts();
}
loadTip();
render();