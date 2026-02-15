//document.addEventListener("DOMContentLoaded", () => {
//  console.log("timer.js読み込み完了");
//
//const tasksTable = document.getElementById("tasksTable");
//  if (!tasksTable) {
//  console.log("tasksTableが見つかりません。tasks.jsの初期化をスキップします。");
//  return;
//  }
//
//  // 初期読み込み実行
//  loadTodayTasks();
//
//
//  // レポートセクションが表示されているかチェック
//  const timerSection = document.getElementById("timer");
//  if (timerSection && timerSection.classList.contains("active")) {
//    // 初期表示（一番上のタスク表示）
//  }
//});
//
//
//
//async function loadTodayTaska() {
//  try {
//    console.log("本日のタスクを読み込み中...");
//    const res = await fetch("/api/tasks");
//
//    if (!res.ok) {
//      throw new Error(`HTTP error! status: ${res.status}`);
//    }
//
//    const json = await res.json();
//
//    // 今日の日付を取得 (YYYY-MM-DD形式)
//    const todayStr = new Date().toISOString().split('T')[0];
//
//    // 今日のタスクのみに絞り込む
//    const todayTasks = json.data.filter(item => item.work_date === todayStr);
//
//    const tbody = document.getElementById("tasksBody");
//    tbody.innerHTML = "";
//
//    if (json.data && json.data.length > 0) {
//      json.data.forEach(item => {
//        const tr = document.createElement("tr");
//        tr.style.cursor = "pointer"; // クリックできることを示す
//
//        tr.innerHTML = `
//          <td>${item.task_name}</td>
//          <td>${item.category_name || '-'}</td>
//          <td>${item.work_date}</td>
//          <td>${item.ended_time || '0'}</td>
//          <td>${item.memo || ''}</td>
//        `;
//
//        // --- 行をクリックした時の処理 ---
//        tr.addEventListener("click", () => {
//          selectTask(item);
//        });
//
//        tbody.appendChild(tr);
//      });
//    } else {
//      tbody.innerHTML =
//        '<tr><td colspan="4">本日のタスクはありません</td></tr>';
//    }
//
//  } catch (error) {
//    console.error("タスクデータの読み込みエラー:", error);
//
//    const tbody = document.getElementById("tasksBody");
//    tbody.innerHTML =
//      '<tr><td colspan="4">データの読み込みに失敗しました</td></tr>';
//  }
//}
//
//
//// タイマーエリアにタスク情報をセットする関数
//function selectTask(task) {
//  document.getElementById("selectedTaskName").textContent = task.task_name;
//  document.getElementById("selectedTaskDate").textContent = `予定日: ${task.work_date}`;
//
//  // ここにタイマーの初期化処理などを書く
//  console.log("選択されたタスク:", task);
//
//  // 選択中であることがわかるようにスタイルを変える（任意）
//  const rows = document.querySelectorAll("#tasksBody tr");
//  rows.forEach(r => r.classList.remove("selected-row"));
//  // クリックされた行にクラスをつける処理などはCSSと組み合わせて調整してください
//}

// タイマーの状態管理用変数
let timerInterval = null;
let seconds = 0;
let selectedTaskId = null;

document.addEventListener("DOMContentLoaded", () => {
    console.log("timer.js読み込み完了");

    const tasksTable = document.getElementById("tasksTable");
    if (!tasksTable) {
        console.log("tasksTableが見つかりません。初期化をスキップします。");
        return;
    }

    // 初回読み込み
    loadTodayTasks();

    // ボタンのイベントリスナー設定
    document.getElementById("startTimer").addEventListener("click", startTimer);
    document.getElementById("stopTimer").addEventListener("click", stopTimer);
    document.getElementById("finishTimer").addEventListener("click", finishTimer);
});

/**
 * 本日のタスクをAPIから取得してテーブルに表示
 */
async function loadTodayTasks() {
    try {
        console.log("本日のタスクを読み込み中...");
        const res = await fetch("/api/tasks");

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const tasks = await res.json();
        console.log("取得した全タスク:", tasks);

        const tbody = document.getElementById("tasksBody");
        tbody.innerHTML = "";

        // 今日の日付 (YYYY-MM-DD) を取得
        const todayStr = new Date().toISOString().split('T')[0];
        console.log("比較対象（今日）:", todayStr);

        // 今日の日付に一致するタスクのみフィルタリング
        const todayTasks = tasks.filter(item => {
            const taskDate = item.start_time || item.start;
            if (!taskDate) return false;
            const taskDateStr = taskDate.split('T')[0];
            console.log(`タスク "${item.task_name}" の日付:`, taskDateStr, "今日:", todayStr);
            return taskDateStr === todayStr;
        });

        console.log("今日のタスク数:", todayTasks.length);

        if (todayTasks && todayTasks.length > 0) {
            todayTasks.forEach(item => {
                const tr = document.createElement("tr");
                tr.style.cursor = "pointer"; // クリック可能であることを示す

                // start_timeから日付を取得
                const workDate = item.start_time ? item.start_time.split('T')[0] : '-';

                // duration_secondsを分に変換
                const durationMinutes = item.duration_seconds ? Math.round(item.duration_seconds / 60) : 0;

                tr.innerHTML = `
                    <td>${item.task_name}</td>
                    <td>${item.category_name || '-'}</td>
                    <td>${workDate}</td>
                    <td><span id="task-time-${item.id}">${durationMinutes}</span> 分</td>
                    <td>${item.memo || ''}</td>
                `;

                // 行をクリックした時に上のタイマーエリアにセット
                tr.addEventListener("click", () => {
                    selectTask(item);
                    // 選択中の行をハイライト（CSSで.selected-rowを定義してください）
                    document.querySelectorAll("#tasksBody tr").forEach(r => r.classList.remove("selected-row"));
                    tr.classList.add("selected-row");
                });

                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5">本日のタスクはありません</td></tr>';
        }

    } catch (error) {
        console.error("タスクデータの読み込みエラー:", error);
        document.getElementById("tasksBody").innerHTML = '<tr><td colspan="5">読み込み失敗</td></tr>';
    }
}

/**
 * 選択されたタスクをタイマーエリアに反映
 */
function selectTask(task) {
    selectedTaskId = task.id;
    document.getElementById("selectedTaskName").textContent = task.task_name;

    // もし既存の実績時間(分)があれば秒に変換してセット（任意）
    // seconds = (task.ended_time || 0) * 60;
    // updateDisplay();

    console.log("タスクを選択しました:", task.task_name);
}

/**
 * タイマー処理
 */
async function startTimer() {
    if (!selectedTaskId) {
        alert("先に下のリストからタスクを選択してください。");
        return;
    }
    if (timerInterval) return; // 二重起動防止

    try {
        const res = await fetch(`/api/time/${selectedTaskId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) {
            alert("タイマー開始に失敗しました");
            return;
        }

        timerInterval = setInterval(() => {
            seconds++;
            updateDisplay();
        }, 1000);
    } catch (error) {
        console.error("タイマー開始エラー:", error);
        alert("タイマー開始に失敗しました");
    }
}

function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function updateDisplay() {
    const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
    const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
    const secs = String(seconds % 60).padStart(2, '0');
    document.getElementById("display").textContent = `${hrs}:${mins}:${secs}`;
}

/**
 * 終了処理
 */
async function finishTimer() {
    if (!selectedTaskId) {
        alert("タスクが選択されていません");
        return;
    }

    stopTimer();
    const finalMinutes = Math.round(seconds / 60);

    try {
        const res = await fetch(`/api/time/${selectedTaskId}/end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!res.ok) {
            alert("タイマー終了に失敗しました");
            return;
        }

        alert(`作業終了！経過時間: 約 ${finalMinutes} 分`);

        // タスク一覧を再読み込みして実績時間を更新
        await loadTodayTasks();

        // 秒数をリセット
        seconds = 0;
        updateDisplay();
        selectedTaskId = null;
        document.getElementById("selectedTaskName").textContent = "タスクを選択してください";
        document.getElementById("selectedTaskDate").textContent = "-";
    } catch (error) {
        console.error("タイマー終了エラー:", error);
        alert("タイマー終了に失敗しました");
    }
}