document.addEventListener("DOMContentLoaded", () => {
  console.log("report.js読み込み完了");

  const projectBtn = document.getElementById("projectBtn");
  const categoryBtn = document.getElementById("categoryBtn");
  const reportTable = document.getElementById("reportTable");
  const yearSelect = document.getElementById("yearSelect");
  const monthSelect = document.getElementById("monthSelect");

  // reportTableが存在しない場合は何もしない（index.htmlでの誤動作を防ぐ）
  if (!reportTable) {
    console.log("reportTableが見つかりません。report.jsの初期化をスキップします。");
    return;
  }

  initYearMonthSelect(yearSelect, monthSelect);

  if (yearSelect && monthSelect) {
    yearSelect.addEventListener("change", () => {
      refreshReport();
    });
    monthSelect.addEventListener("change", () => {
      refreshReport();
    });
  }

  if (projectBtn && categoryBtn) {

    projectBtn.addEventListener("click", () => {
      switchTab("project");
    });

    categoryBtn.addEventListener("click", () => {
      switchTab("category");
    });

  }

  // レポートセクションが表示されているかチェック
  const reportSection = document.getElementById("report");
  if (reportSection && reportSection.classList.contains("active")) {
    // 初期表示（プロジェクト表示）
    switchTab("project");

    const now = new Date();
    loadMonthly(
      now.getFullYear(),
      now.getMonth() + 1
    );
  }
});

let currentTab = "project";

function initYearMonthSelect(yearSelect, monthSelect) {
  if (!yearSelect || !monthSelect) {
    return;
  }

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;

  const years = [];
  for (let y = currentYear - 3; y <= currentYear + 1; y += 1) {
    years.push(y);
  }

  yearSelect.innerHTML = years
    .map(year => `<option value="${year}">${year}年</option>`)
    .join("");

  monthSelect.innerHTML = Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    return `<option value="${month}">${month}月</option>`;
  }).join("");

  yearSelect.value = String(currentYear);
  monthSelect.value = String(currentMonth);
}

function getSelectedYearMonth() {
  const yearSelect = document.getElementById("yearSelect");
  const monthSelect = document.getElementById("monthSelect");

  return {
    year: yearSelect ? yearSelect.value : "",
    month: monthSelect ? monthSelect.value : ""
  };
}

function buildYearMonthQuery() {
  const { year, month } = getSelectedYearMonth();
  const params = new URLSearchParams();

  if (year) {
    params.set("year", year);
  }
  if (month) {
    params.set("month", month);
  }

  const query = params.toString();
  return query ? `?${query}` : "";
}

function refreshReport() {
  const { year, month } = getSelectedYearMonth();
  loadMonthly(year, month);

  if (currentTab === "project") {
    loadProject();
  } else {
    loadCategory();
  }
}

function switchTab(type) {

  const headerRow = document.querySelector("#reportTable thead tr");

  // active解除
  document
    .querySelectorAll(".toggle button")
    .forEach(btn => btn.classList.remove("active"));

  currentTab = type;

  if (type === "project") {

    document
      .getElementById("projectBtn")
      .classList.add("active");

    // ===== ヘッダー変更 =====
    headerRow.innerHTML = `
      <th>タスク名</th>
      <th>予定日</th>
      <th>終了日</th>
      <th>作業時間(h)</th>
      <th>割合(%)</th>
    `;

    loadProject();   // ← 追加

  } else {

    document
      .getElementById("categoryBtn")
      .classList.add("active");

    // ===== ヘッダー戻す =====
    headerRow.innerHTML = `
      <th id="groupHeader">カテゴリ名</th>
      <th>作業時間(h)</th>
      <th>割合(%)</th>
    `;

    loadCategory();
  }
}

async function loadCategory() {
  try {
    console.log("カテゴリ別データを読み込み中...");
    const res = await fetch(`/api/report/category${buildYearMonthQuery()}`);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const json = await res.json();
    console.log("カテゴリ別データ:", json);

    const tbody = document.getElementById("reportBody");
    tbody.innerHTML = ""; // 初期化

    if (json.data && json.data.length > 0) {
      json.data.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${item.category_name}</td>
          <td>${(item.total_hour !== null && item.total_hour !== undefined && isFinite(Number(item.total_hour))) ? Number(item.total_hour).toFixed(1) : ''}</td>
          <td>${(item.progress !== null && item.progress !== undefined && isFinite(Number(item.progress))) ? Number(item.progress).toFixed(1) + '%' : ''}</td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      tbody.innerHTML = '<tr><td colspan="3">データがありません</td></tr>';
    }
  } catch (error) {
    console.error("カテゴリデータの読み込みエラー:", error);
    const tbody = document.getElementById("reportBody");
    tbody.innerHTML = '<tr><td colspan="3">データの読み込みに失敗しました</td></tr>';
  }
}

async function loadMonthly(year, month) {
  try {
    const selected = getSelectedYearMonth();
    const targetYear = year || selected.year;
    const targetMonth = month || selected.month;

    const params = new URLSearchParams();
    if (targetYear) {
      params.set("year", targetYear);
    }
    if (targetMonth) {
      params.set("month", targetMonth);
    }

    const query = params.toString();
    console.log(`月次データを読み込み中... (${targetYear}年${targetMonth}月)`);
    const res = await fetch(
      `/api/report/monthly${query ? `?${query}` : ""}`
    );

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    console.log("月次データ:", data);

    // HTMLへ反映（数値を常に小数点第一位で表示）
    const totalHoursEl = document.getElementById("totalHours");
    const workDaysEl = document.getElementById("workDays");
    const th = (data && data.total_hour !== null && data.total_hour !== undefined && isFinite(Number(data.total_hour))) ? Number(data.total_hour).toFixed(1) : "";
    const wd = (data && (data.total_day !== undefined && data.total_day !== null)) ? String(data.total_day) : "0";
    totalHoursEl.textContent = th;
    workDaysEl.textContent = wd;
  } catch (error) {
    console.error("月次データの読み込みエラー:", error);
    document.getElementById("totalHours").textContent = "0.0";
    document.getElementById("workDays").textContent = "0";
  }
}

async function loadProject() {

  try {
    console.log("プロジェクト別データを読み込み中...");

    const res = await fetch(`/api/report/project${buildYearMonthQuery()}`);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const json = await res.json();
    console.log("プロジェクト別データ:", json);

    const tbody = document.getElementById("reportBody");
    tbody.innerHTML = "";

    if (json.data && json.data.length > 0) {

      json.data.forEach(item => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
          <td>${item.task_name}</td>
          <td>${item.work_date}</td>
          <td>${item.ended_date}</td>
          <td>${(item.total_hour !== null && item.total_hour !== undefined && isFinite(Number(item.total_hour))) ? Number(item.total_hour).toFixed(1) : ''}</td>
          <td>${(item.progress !== null && item.progress !== undefined && isFinite(Number(item.progress))) ? Number(item.progress).toFixed(1) + '%' : ''}</td>
        `;

        tbody.appendChild(tr);
      });

    } else {

      tbody.innerHTML =
        '<tr><td colspan="5">データがありません</td></tr>';
    }

  } catch (error) {

    console.error("プロジェクトデータの読み込みエラー:", error);

    const tbody = document.getElementById("reportBody");
    tbody.innerHTML =
      '<tr><td colspan="5">データの読み込みに失敗しました</td></tr>';
  }
}
