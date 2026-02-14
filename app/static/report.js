document.addEventListener("DOMContentLoaded", () => {
  console.log("report.js読み込み完了");

  const projectBtn = document.getElementById("projectBtn");
  const categoryBtn = document.getElementById("categoryBtn");
  const reportTable = document.getElementById("reportTable");

  // reportTableが存在しない場合は何もしない（index.htmlでの誤動作を防ぐ）
  if (!reportTable) {
    console.log("reportTableが見つかりません。report.jsの初期化をスキップします。");
    return;
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
    // 初期表示（カテゴリ表示）
    loadCategory();

    const now = new Date();
    loadMonthly(
      now.getFullYear(),
      now.getMonth() + 1
    );
  }
});

function switchTab(type) {

  const headerRow = document.querySelector("#reportTable thead tr");

  // active解除
  document
    .querySelectorAll(".toggle button")
    .forEach(btn => btn.classList.remove("active"));

  if (type === "project") {

    document
      .getElementById("projectBtn")
      .classList.add("active");

    // ===== ヘッダー変更 =====
    headerRow.innerHTML = `
      <th>タスク名</th>
      <th>日付</th>
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
    const res = await fetch("/api/report/category");

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
          <td>${item.total_hour}</td>
          <td>${item.progress}%</td>
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
    console.log(`月次データを読み込み中... (${year}年${month}月)`);
    const res = await fetch(
      `/api/report/monthly?year=${year}&month=${month}`
    );

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    console.log("月次データ:", data);

    // HTMLへ反映
    document.getElementById("totalHours").textContent =
      data.total_hour || "0.0";

    document.getElementById("workDays").textContent =
      data.total_day || "0";
  } catch (error) {
    console.error("月次データの読み込みエラー:", error);
    document.getElementById("totalHours").textContent = "0.0";
    document.getElementById("workDays").textContent = "0";
  }
}

async function loadProject() {

  try {
    console.log("プロジェクト別データを読み込み中...");

    const res = await fetch("/api/report/project");

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
          <td>${item.total_hour}</td>
          <td>${item.progress}%</td>
        `;

        tbody.appendChild(tr);
      });

    } else {

      tbody.innerHTML =
        '<tr><td colspan="4">データがありません</td></tr>';
    }

  } catch (error) {

    console.error("プロジェクトデータの読み込みエラー:", error);

    const tbody = document.getElementById("reportBody");
    tbody.innerHTML =
      '<tr><td colspan="4">データの読み込みに失敗しました</td></tr>';
  }
}
