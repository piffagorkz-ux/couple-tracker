const state = {
  mode: "login",
  page: "home",
  data: null,
  toast: "",
  promptModalOpen: false
};

const REFRESH_INTERVAL_MS = 7000;

const icons = {
  home: icon("M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-4.5v-5h-5v5H5a1 1 0 0 1-1-1z"),
  settings: icon("M12 3.75l1.14 2.45 2.68.3.71 2.61 2.25 1.51-.94 2.52.94 2.52-2.25 1.51-.71 2.61-2.68.3L12 20.25l-1.14-2.45-2.68-.3-.71-2.61-2.25-1.51.94-2.52-.94-2.52 2.25-1.51.71-2.61 2.68-.3z M12 15.5A3.5 3.5 0 1 0 12 8.5a3.5 3.5 0 0 0 0 7z"),
  back: icon("M15 18l-6-6 6-6"),
  heart: icon("M12 20.5s-6.5-4.35-8.5-8.15C1.8 9.14 3.42 5.5 7.2 5.5c1.96 0 3.2 1.03 4.02 2.23C12.04 6.53 13.28 5.5 15.24 5.5c3.78 0 5.4 3.64 3.7 6.85-2 3.8-8.5 8.15-8.5 8.15z"),
  goals: icon("M12 3l7 4v10l-7 4-7-4V7z M12 7.5v9"),
  places: icon("M12 21s-6-5.27-6-11a6 6 0 1 1 12 0c0 5.73-6 11-6 11z M12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"),
  dates: icon("M7 3v3M17 3v3M4 9h16M6 5h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"),
  activities: icon("M5 14c1.5-3 3.5-4.5 6-4.5s4.5 1.5 6 4.5M8 8.5h.01M16 8.5h.01M12 17v.01"),
  wishes: icon("M12 3.5l2.55 5.17 5.7.83-4.12 4.02.97 5.68L12 16.52 6.9 19.2l.97-5.68L3.75 9.5l5.7-.83z"),
  importantDates: icon("M8 3v2M16 3v2M5 7h14M6 5h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z M9 13h6")
};

const app = document.getElementById("app");
boot();

async function boot() {
  await refreshSession();
  render();
  startAutoRefresh();
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    headers: { "content-type": "application/json" },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

async function refreshSession() {
  const previousData = state.data;
  try {
    state.data = await api("/api/me", { method: "GET" });
    syncPromptModal();
    notifyAboutUpdates(previousData, state.data);
  } catch {
    state.data = null;
    state.promptModalOpen = false;
  }
}

function render() {
  const user = state.data?.user;
  const t = state.data?.t || fallbackT();
  document.body.className = user?.gender === "male" ? "theme-male" : "theme-female";

  app.innerHTML = `
    ${state.toast ? `<div class="toast">${escapeHtml(state.toast)}</div>` : ""}
    <div class="shell">
      <button class="brand brand-button" data-page="home" aria-label="Lovio home">
        <span class="brand-mark"></span>
        <span>Lovio</span>
      </button>
      ${user ? renderDashboard(t) : renderAuth(t)}
    </div>
    ${user ? renderNav(t) : ""}
    ${user && state.promptModalOpen ? renderPromptModal(state.data, t) : ""}
  `;

  bindEvents();
}

function startAutoRefresh() {
  clearInterval(startAutoRefresh.timer);
  startAutoRefresh.timer = setInterval(async () => {
    if (!state.data?.user || document.hidden) {
      return;
    }
    await refreshSession();
    render();
  }, REFRESH_INTERVAL_MS);
}

document.addEventListener("visibilitychange", async () => {
  if (!document.hidden && state.data?.user) {
    await refreshSession();
    render();
  }
});

window.addEventListener("focus", async () => {
  if (state.data?.user) {
    await refreshSession();
    render();
  }
});

function renderAuth(t) {
  return `
    <section class="auth-shell glass">
      <div class="auth-content">
        <div class="auth-badge">
          <span class="brand-mark"></span>
          <span>${escapeHtml(t.authBadge)}</span>
        </div>
        <h1 class="auth-title">${escapeHtml(t.authTitle)}</h1>
        <p class="auth-subtitle">${escapeHtml(t.authSubtitle)}</p>
        <div class="tabs">
          <button class="tab-btn ${state.mode === "login" ? "active" : ""}" data-mode="login">${escapeHtml(t.login)}</button>
          <button class="tab-btn ${state.mode === "register" ? "active" : ""}" data-mode="register">${escapeHtml(t.register)}</button>
        </div>
        <div class="auth-grid">
          ${state.mode === "login" ? renderLoginForm(t) : renderRegisterForm(t)}
          ${renderAuthPreview(t)}
        </div>
      </div>
    </section>
  `;
}

function renderLoginForm(t) {
  return `
    <form id="login-form" class="stack">
      <div class="field">
        <label>${escapeHtml(t.email)}</label>
        <input name="email" type="email" placeholder="${escapeHtml(t.emailPlaceholder)}" required>
      </div>
      <div class="field">
        <label>${escapeHtml(t.password)}</label>
        <input name="password" type="password" placeholder="${escapeHtml(t.passwordPlaceholder)}" required>
      </div>
      <button class="primary-btn" type="submit">${escapeHtml(t.login)}</button>
    </form>
  `;
}

function renderRegisterForm(t) {
  return `
    <form id="register-form" class="stack">
      <div class="field">
        <label>${escapeHtml(t.name)}</label>
        <input name="name" placeholder="${escapeHtml(t.namePlaceholder)}" required>
      </div>
      <div class="field">
        <label>${escapeHtml(t.username)}</label>
        <input name="username" placeholder="${escapeHtml(t.usernamePlaceholder)}" required>
      </div>
      <div class="field">
        <label>${escapeHtml(t.email)}</label>
        <input name="email" type="email" placeholder="${escapeHtml(t.emailPlaceholder)}" required>
      </div>
      <div class="field">
        <label>${escapeHtml(t.password)}</label>
        <input name="password" type="password" placeholder="${escapeHtml(t.passwordPlaceholder)}" required>
      </div>
      <div class="field">
        <label>${escapeHtml(t.gender)}</label>
        <select name="gender">
          <option value="female">${escapeHtml(t.female)}</option>
          <option value="male">${escapeHtml(t.male)}</option>
        </select>
      </div>
      <button class="primary-btn" type="submit">${escapeHtml(t.register)}</button>
    </form>
  `;
}

function renderAuthPreview(t) {
  return `
    <aside class="auth-preview glass">
      <div class="preview-phone">
        <div class="preview-topline">
          <span class="mini-pill">${escapeHtml(t.previewLabel)}</span>
          <span class="preview-time">09:41</span>
        </div>
        <div class="preview-orbit">
          <div class="preview-orbit-inner"></div>
        </div>
        <div class="preview-stats">
          <div class="preview-stat">
            <strong>2/2</strong>
            <span>${escapeHtml(t.previewAnswers)}</span>
          </div>
          <div class="preview-stat">
            <strong>6</strong>
            <span>${escapeHtml(t.previewChoices)}</span>
          </div>
        </div>
        <div class="preview-bubbles">
          <div class="preview-bubble preview-bubble-a">${escapeHtml(t.previewBubbleA)}</div>
          <div class="preview-bubble preview-bubble-b">${escapeHtml(t.previewBubbleB)}</div>
        </div>
      </div>
    </aside>
  `;
}

function renderDashboard(t) {
  const data = state.data;
  const sections = {
    home: renderHome(data, t),
    stats: renderStats(data, t),
    goals: renderGoals(data, t),
    places: renderPlaces(data, t),
    dates: renderDates(data, t),
    activities: renderActivities(data, t),
    wishes: renderWishes(data, t),
    importantDates: renderImportantDates(data, t),
    settings: renderSettings(data, t)
  };

  return `
    <div class="topbar">
      <div>
        <div class="section-kicker script-kicker">${escapeHtml(t.appTagline)}</div>
        ${state.page === "home" ? "" : `<h2 class="topbar-title">${escapeHtml(screenTitle(state.page, t))}</h2>`}
        ${state.page === "home" ? "" : `<p class="topbar-copy">${escapeHtml(screenSubtitleText(state.page, t, Boolean(data.partner)))}</p>`}
      </div>
      <div class="actions">
        ${state.page !== "home" ? `<button class="icon-btn back-btn" data-back="1" aria-label="${escapeHtml(t.back || "Назад")}">${icons.back}<span>${escapeHtml(t.back || "Назад")}</span></button>` : ""}
      </div>
    </div>
    ${sections[state.page] || sections.home}
  `;
}

function renderHome(data, t) {
  const ux = getUxCopy();
  const onboarding = renderOnboarding(data, t, ux);
  if (!data.partner) {
    return renderHomeEmpty(data, t, ux, onboarding);
  }

  const closeness = getClosenessScore(data);
  const answers = countAnswers(data.prompt);
  const bothAnswers = data.prompt?.bothAnswered ? 2 : answers;

  return `
    <div class="stack">
      ${onboarding}
      <section class="panel glass minimal-dashboard">
        <div class="dashboard-top">
          <button class="stat-card ring-card" data-page="stats">
            <div class="ring" style="--value:${closeness};">
              <div class="ring-inner">${closeness}%</div>
            </div>
            <span class="stat-card-label">${escapeHtml(t.closeness)}</span>
          </button>
          <button class="center-pill heart-pill" data-send-heart="1">
            <span class="heart-pill-icon">${icons.heart}</span>
          </button>
          <div class="stat-card stats-card">
            <strong>${escapeHtml(t.answerQuestion)}</strong>
            <span>${bothAnswers}/2</span>
            <span>${escapeHtml(t.answersStat)}</span>
          </div>
        </div>
        <div class="block-grid">
          ${renderHomeBlock("goals", icons.goals, t.goals, (data.goals || []).filter((item) => !item.completed).length, data.unreadCounts?.goals || 0)}
          ${renderHomeBlock("places", icons.places, t.places, (data.places || []).filter((item) => !item.visited).length, data.unreadCounts?.places || 0)}
          ${renderHomeBlock("dates", icons.dates, t.dates, (data.dates || []).length, data.unreadCounts?.dates || 0)}
          ${renderHomeBlock("activities", icons.activities, t.activities, data.activities?.mySelection ? 1 : 0, data.unreadCounts?.activities || 0)}
          ${renderHomeBlock("wishes", icons.wishes, t.wishes, (data.wishes || []).length, data.unreadCounts?.wishes || 0)}
          ${renderHomeBlock("importantDates", icons.importantDates, t.importantDates, (data.importantDates || []).length, data.unreadCounts?.importantDates || 0)}
        </div>
      </section>
    </div>
  `;
}

function renderStats(data, t) {
  const closeness = getClosenessScore(data);
  const answers = countAnswers(data.prompt);
  const completedGoals = (data.goals || []).filter((item) => item.completed).length;
  const visitedPlaces = (data.places || []).filter((item) => item.visited).length;
  const plannedDates = (data.dates || []).length;
  const answeredTogether = data.prompt?.bothAnswered ? 1 : 0;
  const activityProgress = data.activities?.selected?.length || 0;

  return `
    <div class="stack">
      <section class="panel glass stats-hero">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.closeness || "Близость")}</div>
            <h3>${escapeHtml(t.statsTitle || "Статистика отношений")}</h3>
            <p class="muted panel-copy">${escapeHtml(t.statsSubtitle || "Короткий срез вашей общей динамики и ритма.")}</p>
          </div>
        </div>
        <div class="stats-hero-grid">
          <div class="stats-orbit-card">
            <div class="stats-orbit" style="--value:${closeness};">
              <div class="stats-orbit-inner">
                <strong>${closeness}%</strong>
                <span>${escapeHtml(t.closeness || "Близость")}</span>
              </div>
            </div>
          </div>
          <div class="stats-mini-grid">
            <div class="insight">
              <span class="insight-label">${escapeHtml(t.answersStat || "Ответы")}</span>
              <strong class="insight-value">${answers}/2</strong>
            </div>
            <div class="insight">
              <span class="insight-label">${escapeHtml(t.activities || "Активности")}</span>
              <strong class="insight-value">${activityProgress}/2</strong>
            </div>
            <div class="insight">
              <span class="insight-label">${escapeHtml(t.statsGoalsDone || "Выполненные цели")}</span>
              <strong class="insight-value">${completedGoals}</strong>
            </div>
            <div class="insight">
              <span class="insight-label">${escapeHtml(t.statsPlacesVisited || "Посещенные места")}</span>
              <strong class="insight-value">${visitedPlaces}</strong>
            </div>
          </div>
        </div>
      </section>
      <section class="panel glass">
        <div class="stats-progress-list">
          ${renderStatRow(t.statsPromptTogether || "Вопросы дня вместе", answeredTogether, 1)}
          ${renderStatRow(t.statsGoalsDone || "Выполненные цели", completedGoals, Math.max((data.goals || []).length, 1))}
          ${renderStatRow(t.statsPlacesVisited || "Посещенные места", visitedPlaces, Math.max((data.places || []).length, 1))}
          ${renderStatRow(t.statsDatesPlanned || "Запланированные свидания", plannedDates, Math.max(plannedDates, 1))}
        </div>
      </section>
    </div>
  `;
}

function renderStatRow(label, value, total) {
  const safeTotal = Math.max(total, 1);
  const percent = Math.max(8, Math.min(100, Math.round((value / safeTotal) * 100)));
  return `
    <div class="stats-row">
      <div class="stats-row-head">
        <strong>${escapeHtml(label)}</strong>
        <span>${value}</span>
      </div>
      <div class="stats-bar">
        <div class="stats-bar-fill" style="width:${percent}%"></div>
      </div>
    </div>
  `;
}

function renderHomeEmpty(data, t, ux, onboarding = "") {
  return `
    <div class="stack">
      ${onboarding}
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.partner)}</div>
            <h3>${escapeHtml(t.inviteTitle)}</h3>
            <p class="muted panel-copy">${escapeHtml(t.noCouple)}</p>
          </div>
        </div>
        <form id="invite-form" class="stack">
          <div class="field">
            <label>${escapeHtml(t.email)}</label>
            <input name="email" type="email" placeholder="${escapeHtml(t.invitePlaceholder)}" required>
          </div>
          <button class="primary-btn" type="submit">${escapeHtml(t.sendInvite)}</button>
        </form>
      </section>
      ${(data.invitations || []).length ? `
        <section class="panel glass">
          <div class="panel-header">
            <div>
              <div class="section-kicker">${escapeHtml(ux.pendingInvitesKicker)}</div>
              <h3>${escapeHtml(ux.pendingInvitesTitle)}</h3>
            </div>
          </div>
          <div class="list">
            ${(data.invitations || []).map((invite) => `
              <div class="invite-card">
                <strong>${escapeHtml(invite.name)}</strong>
                <div class="muted">${escapeHtml(invite.email)}</div>
                <div class="row" style="margin-top:10px;">
                  <button class="primary-btn" data-invite="${invite.id}" data-value="accept">${escapeHtml(t.accept)}</button>
                  <button class="ghost-btn" data-invite="${invite.id}" data-value="decline">${escapeHtml(t.decline)}</button>
                </div>
              </div>
            `).join("")}
          </div>
        </section>
      ` : ""}
    </div>
  `;
}

function renderGoals(data, t) {
  const ux = getUxCopy();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.goals)}</div>
            <h3>${escapeHtml(t.goalsTitle)}</h3>
          </div>
          ${renderCounter((data.goals || []).filter((goal) => !goal.completed).length)}
        </div>
        <form id="goal-form" class="composer-grid">
          <input class="inline-input" name="text" placeholder="${escapeHtml(t.addGoal)}" required>
          <button class="primary-btn" type="submit">${escapeHtml(t.submit)}</button>
        </form>
      </section>
      <section class="panel glass">
        <div class="list">
          ${(data.goals || []).map((goal) => `
            <div class="item">
              <strong>${escapeHtml(goal.text)}</strong>
              <div class="item-meta">
                ${goal.completed
                  ? `<span class="pill accepted">${escapeHtml(t.done)}</span>`
                  : `<button class="ghost-btn" data-goal-complete="${goal.id}">${escapeHtml(t.submit)}</button>`}
              </div>
            </div>
          `).join("") || renderEmptyState({
            iconMarkup: icons.goals,
            title: ux.emptyGoalsTitle,
            copy: ux.emptyGoalsCopy,
            primaryLabel: ux.emptyGoalsPrimary,
            primaryScrollTarget: "goal-form",
            secondaryLabel: ux.emptyGoalsSecondary,
            secondaryPage: "dates"
          })}
        </div>
      </section>
    </div>
  `;
}

function renderPlaces(data, t) {
  const ux = getUxCopy();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.places)}</div>
            <h3>${escapeHtml(t.placesTitle)}</h3>
          </div>
        </div>
        <form id="place-form" class="composer-grid">
          <input class="inline-input" name="name" placeholder="${escapeHtml(t.addPlace)}" required>
          <button class="primary-btn" type="submit">${escapeHtml(t.submit)}</button>
        </form>
      </section>
      <section class="panel glass">
        <div class="list">
          ${(data.places || []).map((item) => `
            <div class="item">
              <strong>${escapeHtml(item.name)}</strong>
              <div class="item-meta">
                ${item.visited
                  ? `<span class="pill accepted">${escapeHtml(t.visited)}</span>`
                  : `<button class="ghost-btn" data-place-visit="${item.id}">${escapeHtml(t.markVisited)}</button>`}
              </div>
            </div>
          `).join("") || renderEmptyState({
            iconMarkup: icons.places,
            title: ux.emptyPlacesTitle,
            copy: ux.emptyPlacesCopy,
            primaryLabel: ux.emptyPlacesPrimary,
            primaryScrollTarget: "place-form"
          })}
        </div>
      </section>
    </div>
  `;
}

function renderDates(data, t) {
  const ux = getUxCopy();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.dates)}</div>
            <h3>${escapeHtml(t.datesTitle)}</h3>
          </div>
        </div>
        <form id="date-form" class="stack">
          <div class="field">
            <label>${escapeHtml(t.dateTitle)}</label>
            <input name="title" placeholder="${escapeHtml(t.dateTitle)}" required>
          </div>
          <div class="field">
            <label>${escapeHtml(t.description)}</label>
            <textarea name="description" placeholder="${escapeHtml(t.description)}"></textarea>
          </div>
          <div class="field">
            <label>${escapeHtml(t.dateValue)}</label>
            <input name="plannedDate" type="datetime-local" required>
          </div>
          <button class="primary-btn" type="submit">${escapeHtml(t.submit)}</button>
        </form>
      </section>
      <section class="panel glass">
        <div class="list">
          ${(data.dates || []).map((item) => `
            <div class="item">
              <strong>${escapeHtml(item.title)}</strong>
              <div class="muted">${escapeHtml(t.plannedFor)}: ${escapeHtml(item.planned_date)}</div>
              ${item.description ? `<div style="margin-top:8px;">${escapeHtml(item.description)}</div>` : ""}
              <div class="item-meta">
                <span class="pill ${pillClass(item.status)}">${escapeHtml(statusLabel(item.status, t))}</span>
                ${typeof item.expires_in_seconds === "number" ? `<span class="mini-pill">${escapeHtml(t.expiresIn)} ${formatDuration(item.expires_in_seconds)}</span>` : ""}
              </div>
              ${item.status === "pending" ? `
                <div class="row" style="margin-top:10px;">
                  <button class="primary-btn" data-date="${item.id}" data-value="accept">${escapeHtml(t.accept)}</button>
                  <button class="ghost-btn" data-date="${item.id}" data-value="decline">${escapeHtml(t.decline)}</button>
                </div>
              ` : ""}
            </div>
          `).join("") || renderEmptyState({
            iconMarkup: icons.dates,
            title: ux.emptyDatesTitle,
            copy: ux.emptyDatesCopy,
            primaryLabel: ux.emptyDatesPrimary,
            primaryScrollTarget: "date-form",
            secondaryLabel: ux.emptyDatesSecondary,
            secondaryPage: "goals"
          })}
        </div>
      </section>
    </div>
  `;
}

function renderActivities(data, t) {
  const activities = data.activities;
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.activities)}</div>
            <h3>${escapeHtml(t.activitiesTitle)}</h3>
          </div>
          ${renderCounter(activities?.mySelection ? 1 : 0, 1)}
        </div>
        ${activities?.mySelection ? `
          <div class="selected-grid">
            <div class="selected-chip">${escapeHtml(activities.mySelection.label)}</div>
          </div>
          <p class="muted panel-copy">${escapeHtml(t.activityLocked)}</p>
        ` : `
          <div class="choices">
            ${(activities?.choices || []).map((item) => `
              <div class="choice">
                <div class="choice-title">${escapeHtml(item.label)}</div>
                <button class="primary-btn" data-select-activity="${escapeHtml(item.code)}">${escapeHtml(t.choose)}</button>
              </div>
            `).join("")}
          </div>
        `}
      </section>
    </div>
  `;
}

function renderWishes(data, t) {
  const ux = getUxCopy();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.wishes)}</div>
            <h3>${escapeHtml(t.wishesTitle)}</h3>
          </div>
        </div>
        <form id="wish-form" class="stack">
          <div class="field">
            <label>${escapeHtml(t.addWish)}</label>
            <input name="text" placeholder="${escapeHtml(t.addWish)}" required>
          </div>
          <div class="field">
            <label>${escapeHtml(t.price)}</label>
            <input name="price" type="number" min="0" value="0">
          </div>
          <button class="primary-btn" type="submit">${escapeHtml(t.submit)}</button>
        </form>
      </section>
      <section class="panel glass">
        <div class="list">
          ${(data.wishes || []).map((item) => `
            <div class="item">
              <strong>${escapeHtml(item.text)}</strong>
              <div class="item-meta">
                <span class="mini-pill">${escapeHtml(t.price)} ${Number(item.price || 0)}</span>
              </div>
            </div>
          `).join("") || renderEmptyState({
            iconMarkup: icons.wishes,
            title: ux.emptyWishesTitle,
            copy: ux.emptyWishesCopy,
            primaryLabel: ux.emptyWishesPrimary,
            primaryScrollTarget: "wish-form"
          })}
        </div>
      </section>
    </div>
  `;
}

function renderImportantDates(data, t) {
  const ux = getUxCopy();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.importantDates)}</div>
            <h3>${escapeHtml(t.importantDatesTitle)}</h3>
          </div>
        </div>
        <form id="important-date-form" class="stack">
          <div class="field">
            <label>${escapeHtml(t.dateTitle)}</label>
            <input name="title" placeholder="${escapeHtml(t.dateTitle)}" required>
          </div>
          <div class="field">
            <label>${escapeHtml(t.dateValue)}</label>
            <input name="dateValue" type="date" required>
          </div>
          <button class="primary-btn" type="submit">${escapeHtml(t.submit)}</button>
        </form>
      </section>
      <section class="panel glass">
        <div class="list">
          ${(data.importantDates || []).map((item) => `
            <div class="item">
              <strong>${escapeHtml(item.title)}</strong>
              <div class="item-meta">
                <span class="mini-pill">${escapeHtml(item.date_value)}</span>
              </div>
            </div>
          `).join("") || renderEmptyState({
            iconMarkup: icons.importantDates,
            title: ux.emptyImportantDatesTitle,
            copy: ux.emptyImportantDatesCopy,
            primaryLabel: ux.emptyImportantDatesPrimary,
            primaryScrollTarget: "important-date-form"
          })}
        </div>
      </section>
    </div>
  `;
}

function renderSettings(data, t) {
  const user = data.user;
  const ux = getUxCopy();
  const notificationsAvailable = hasNotificationSupport();
  const notificationsEnabled = isNotificationsEnabled();
  return `
    <div class="stack">
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.settings)}</div>
            <h3>${escapeHtml(t.language)}</h3>
          </div>
        </div>
        <div class="segmented settings-language">
          <button class="chip ${user.language === "ru" ? "active" : ""}" data-language="ru">Русский</button>
          <button class="chip ${user.language === "en" ? "active" : ""}" data-language="en">English</button>
        </div>
      </section>
      <section class="panel glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(ux.notificationsKicker)}</div>
            <h3>${escapeHtml(ux.notificationsTitle)}</h3>
            <p class="muted panel-copy">${escapeHtml(
              notificationsAvailable
                ? notificationsEnabled
                  ? ux.notificationsEnabledCopy
                  : ux.notificationsDisabledCopy
                : ux.notificationsUnavailableCopy
            )}</p>
          </div>
          <span class="pill ${notificationsEnabled ? "accepted" : "pending"}">${escapeHtml(
            notificationsAvailable
              ? notificationsEnabled
                ? ux.notificationsEnabledBadge
                : ux.notificationsDisabledBadge
              : ux.notificationsUnavailableBadge
          )}</span>
        </div>
        ${notificationsAvailable && !notificationsEnabled ? `
          <button class="primary-btn settings-notify-btn" data-enable-notifications="1">${escapeHtml(ux.notificationsAction)}</button>
        ` : ""}
      </section>
      <section class="panel glass">
        <button class="ghost-btn settings-logout" data-action="logout">${escapeHtml(t.logout)}</button>
      </section>
    </div>
  `;
}

function renderPromptModal(data, t) {
  const prompt = data.prompt;
  return `
    <div class="modal-backdrop">
      <div class="modal-card glass">
        <div class="panel-header">
          <div>
            <div class="section-kicker">${escapeHtml(t.answerQuestion)}</div>
            <h3>${escapeHtml(t.dailyPromptTitle)}</h3>
          </div>
          <button class="icon-btn" data-close-prompt="1" aria-label="${escapeHtml(t.close)}">${closeIcon()}</button>
        </div>
        <p class="question-text">${escapeHtml(prompt.question)}</p>
        <form id="prompt-form" class="stack" style="margin-top:18px;">
          <div class="field">
            <label>${escapeHtml(t.answer)}</label>
            <textarea name="answerText" placeholder="${escapeHtml(t.answerPlaceholder)}" required>${escapeHtml(prompt.myResponse?.answer_text || "")}</textarea>
          </div>
          <div class="mood-meter">
            <div class="mood-header">
              <span class="section-kicker">${escapeHtml(t.mood)}</span>
              <span class="mini-pill">${prompt.myResponse?.mood_level || 3}/5</span>
            </div>
            <div class="range-shell">
              <input class="mood" name="moodLevel" type="range" min="1" max="5" value="${prompt.myResponse?.mood_level || 3}">
            </div>
          </div>
          <button class="primary-btn" type="submit">${escapeHtml(t.save)}</button>
        </form>
        <p class="muted panel-copy">${escapeHtml(prompt.bothAnswered ? t.dailyRevealReady : t.dailyRevealWaiting)}</p>
      </div>
    </div>
  `;
}

function renderHomeBlock(page, iconMarkup, label, count, unreadCount = 0) {
  return `
    <button class="block-card" data-page="${page}">
      ${unreadCount ? `<span class="badge green-badge block-badge">${unreadCount}</span>` : ""}
      <span class="block-card-icon">${iconMarkup}</span>
      <span class="block-card-label">${escapeHtml(label)}</span>
      <strong>${count}</strong>
    </button>
  `;
}

function renderOnboarding(data, t, ux) {
  const steps = getOnboardingSteps(data, ux);
  const completed = steps.filter((step) => step.done).length;
  if (completed === steps.length) {
    return "";
  }
  return `
    <section class="panel glass onboarding-card">
      <div class="panel-header">
        <div>
          <div class="section-kicker">${escapeHtml(ux.onboardingKicker)}</div>
          <h3>${escapeHtml(ux.onboardingTitle)}</h3>
          <p class="muted panel-copy">${escapeHtml(ux.onboardingSubtitle)}</p>
        </div>
        <span class="badge">${completed}/${steps.length}</span>
      </div>
      <div class="onboarding-steps">
        ${steps.map((step, index) => `
          <div class="onboarding-step ${step.done ? "done" : step.locked ? "locked" : ""}">
            <div class="onboarding-step-index">${step.done ? "✓" : index + 1}</div>
            <div class="onboarding-step-body">
              <div class="onboarding-step-head">
                <strong>${escapeHtml(step.title)}</strong>
                <span class="mini-pill">${escapeHtml(step.status)}</span>
              </div>
              <p>${escapeHtml(step.copy)}</p>
              ${step.actionLabel ? `<button class="${step.primary ? "primary-btn" : "ghost-btn"} onboarding-action" ${step.actionAttr}>${escapeHtml(step.actionLabel)}</button>` : ""}
            </div>
          </div>
        `).join("")}
      </div>
    </section>
  `;
}

function renderEmptyState({
  iconMarkup,
  title,
  copy,
  primaryLabel,
  primaryScrollTarget,
  secondaryLabel,
  secondaryPage
}) {
  return `
    <div class="empty-state">
      <div class="empty-state-icon">${iconMarkup}</div>
      <div class="empty-state-title">${escapeHtml(title)}</div>
      <p class="empty-state-copy">${escapeHtml(copy)}</p>
      <div class="empty-state-actions">
        ${primaryLabel ? `<button class="primary-btn" data-scroll-target="${primaryScrollTarget}">${escapeHtml(primaryLabel)}</button>` : ""}
        ${secondaryLabel ? `<button class="ghost-btn" data-page="${secondaryPage}">${escapeHtml(secondaryLabel)}</button>` : ""}
      </div>
    </div>
  `;
}

function renderNav(t) {
  return `
    <div class="footer-nav">
      <div class="inner nav-minimal">
        <button class="nav-btn ${state.page === "home" ? "active" : ""}" data-page="home" aria-label="${escapeHtml(t.home)}">
          ${icons.home}
        </button>
        <button class="nav-btn ${state.page === "settings" ? "active" : ""}" data-page="settings" aria-label="${escapeHtml(t.settings)}">
          ${icons.settings}
        </button>
      </div>
    </div>
  `;
}

function bindEvents() {
  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.onclick = () => {
      state.mode = button.dataset.mode;
      render();
    };
  });

  document.querySelectorAll("[data-page]").forEach((button) => {
    button.onclick = () => {
      openPage(button.dataset.page);
    };
  });

  document.querySelectorAll("[data-back]").forEach((button) => {
    button.onclick = () => {
      openPage("home");
    };
  });

  document.querySelectorAll("[data-language]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api("/api/language", {
        method: "POST",
        body: JSON.stringify({ language: button.dataset.language })
      });
      await refreshSession();
    });
  });

  document.querySelectorAll("[data-open-prompt]").forEach((button) => {
    button.onclick = () => {
      state.promptModalOpen = true;
      render();
    };
  });

  document.querySelectorAll("[data-send-heart]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api("/api/heart-ping", { method: "POST" });
      await refreshSession();
      showToast((state.data?.t || fallbackT()).heartSent);
    });
  });

  document.querySelectorAll("[data-close-prompt]").forEach((button) => {
    button.onclick = () => {
      state.promptModalOpen = false;
      render();
    };
  });

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(loginForm);
      await api("/api/login", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      await refreshSession();
    });
  }

  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(registerForm);
      await api("/api/register", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      await refreshSession();
    });
  }

  document.querySelectorAll('[data-action="logout"]').forEach((button) => {
    button.onclick = () => perform(async () => {
      await api("/api/logout", { method: "POST" });
      state.data = null;
      state.promptModalOpen = false;
    });
  });

  const inviteForm = document.getElementById("invite-form");
  if (inviteForm) {
    inviteForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(inviteForm);
      await api("/api/invite/send", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      showToast((state.data?.t || fallbackT()).inviteSent);
      await refreshSession();
    });
  }

  document.querySelectorAll("[data-invite]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api(`/api/invite/${button.dataset.invite}/respond`, {
        method: "POST",
        body: JSON.stringify({ action: button.dataset.value })
      });
      await refreshSession();
    });
  });

  const promptForm = document.getElementById("prompt-form");
  if (promptForm) {
    promptForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(promptForm);
      await api("/api/daily-prompt/answer", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      state.promptModalOpen = false;
      await refreshSession();
    });
  }

  document.querySelectorAll("[data-select-activity]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api("/api/activities/select", {
        method: "POST",
        body: JSON.stringify({ code: button.dataset.selectActivity })
      });
      await refreshSession();
    });
  });

  const goalForm = document.getElementById("goal-form");
  if (goalForm) {
    goalForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(goalForm);
      await api("/api/goals", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      goalForm.reset();
      await refreshSession();
    });
  }

  const placeForm = document.getElementById("place-form");
  if (placeForm) {
    placeForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(placeForm);
      await api("/api/places", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      placeForm.reset();
      await refreshSession();
    });
  }

  document.querySelectorAll("[data-place-visit]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api(`/api/places/${button.dataset.placeVisit}/visit`, { method: "POST" });
      await refreshSession();
    });
  });

  document.querySelectorAll("[data-goal-complete]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api(`/api/goals/${button.dataset.goalComplete}/complete`, { method: "POST" });
      await refreshSession();
    });
  });

  const dateForm = document.getElementById("date-form");
  if (dateForm) {
    dateForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(dateForm);
      await api("/api/dates", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      dateForm.reset();
      await refreshSession();
    });
  }

  document.querySelectorAll("[data-date]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await api(`/api/dates/${button.dataset.date}/respond`, {
        method: "POST",
        body: JSON.stringify({ action: button.dataset.value })
      });
      await refreshSession();
    });
  });

  const wishForm = document.getElementById("wish-form");
  if (wishForm) {
    wishForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(wishForm);
      await api("/api/wishes", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      wishForm.reset();
      await refreshSession();
    });
  }

  const importantDateForm = document.getElementById("important-date-form");
  if (importantDateForm) {
    importantDateForm.onsubmit = (event) => perform(async () => {
      event.preventDefault();
      const form = new FormData(importantDateForm);
      await api("/api/important-dates", { method: "POST", body: JSON.stringify(Object.fromEntries(form.entries())) });
      importantDateForm.reset();
      await refreshSession();
    });
  }

  document.querySelectorAll("[data-enable-notifications]").forEach((button) => {
    button.onclick = () => perform(async () => {
      await enableNotifications();
    });
  });

  document.querySelectorAll("[data-scroll-target]").forEach((button) => {
    button.onclick = () => {
      const target = document.getElementById(button.dataset.scrollTarget);
      if (!target) return;
      target.scrollIntoView({ behavior: "smooth", block: "center" });
      const field = target.querySelector("input, textarea, select");
      field?.focus();
    };
  });

  const russianButton = document.querySelector('[data-language="ru"]');
  if (russianButton) {
    russianButton.textContent = "Русский";
  }
}

async function perform(fn) {
  try {
    await fn();
    render();
  } catch (error) {
    showToast(error.message || "Ошибка");
  }
}

function showToast(message) {
  state.toast = message;
  render();
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    state.toast = "";
    render();
  }, 2600);
}

async function enableNotifications() {
  const ux = getUxCopy();
  if (!hasNotificationSupport()) {
    throw new Error(ux.notificationsUnavailableBadge);
  }
  const permission = await Notification.requestPermission();
  if (permission === "granted") {
    showToast(ux.notificationsEnabledToast);
    return;
  }
  showToast(ux.notificationsDeniedToast);
}

function syncPromptModal() {
  const user = state.data?.user;
  const prompt = state.data?.prompt;
  if (!user || !prompt || user.couple_id == null || prompt.myResponse) {
    state.promptModalOpen = false;
    return;
  }
  const today = new Date().toISOString().slice(0, 10);
  const key = `lovio-prompt-seen-${user.id}-${today}`;
  if (!localStorage.getItem(key)) {
    localStorage.setItem(key, "1");
    state.promptModalOpen = true;
  }
}

async function openPage(page) {
  state.page = page;
  if (state.data?.user) {
    if (["goals", "places", "dates", "activities", "wishes", "importantDates"].includes(page)) {
      await api(`/api/sections/${page}/seen`, { method: "POST" }).catch(() => {});
      await refreshSession();
    }
  }
  render();
}

function fallbackT() {
  return {
    appTagline: "Пространство для двоих",
    login: "Войти",
    register: "Регистрация",
    email: "Почта",
    username: "Логин",
    password: "Пароль",
    name: "Имя",
    gender: "Пол",
    female: "Девушка",
    male: "Парень",
    home: "Главная",
    settings: "Настройки",
    partner: "Партнер",
    goals: "Цели",
    places: "Места",
    dates: "Свидания",
    activities: "Активности",
    wishes: "Желания",
    importantDates: "Важные даты",
    save: "Сохранить",
    logout: "Выйти",
    sendInvite: "Отправить приглашение",
    invitePlaceholder: "Почта партнера",
    inviteSent: "Приглашение отправлено",
    inviteTitle: "Пригласи партнера",
    answerQuestion: "Вопрос дня",
    dailyPromptTitle: "Вопрос дня",
    mood: "Настроение",
    answer: "Ответ",
    answerPlaceholder: "Напиши ответ",
    noCouple: "Пригласи партнера, чтобы открыть общее пространство.",
    addGoal: "Добавить цель",
    addPlace: "Добавить место",
    addWish: "Добавить желание",
    plannedFor: "Запланировано",
    price: "Цена",
    dateTitle: "Название",
    description: "Описание",
    dateValue: "Дата",
    accept: "Принять",
    decline: "Отклонить",
    submit: "Сохранить",
    dailyRevealWaiting: "Ответы откроются, когда ответят оба.",
    dailyRevealReady: "Оба ответа уже открыты.",
    statusPending: "Ожидает",
    statusAccepted: "Принято",
    statusDeclined: "Отклонено",
    expiresIn: "Исчезнет через",
    noItems: "Пока пусто.",
    you: "Вы",
    done: "Готово",
    visited: "Были",
    markVisited: "Отметить",
    activityLocked: "Активность на сегодня уже выбрана.",
    choose: "Выбрать",
    closeness: "Близость",
    answersStat: "Ответы",
    activityStat: "Активности",
    language: "Язык",
    authBadge: "Личное пространство для двоих",
    authTitle: "Ближе друг к другу каждый день",
    authSubtitle: "Вопрос дня, планы, желания и теплые маленькие ритуалы в одном месте.",
    emailPlaceholder: "you@email.com",
    passwordPlaceholder: "Пароль",
    namePlaceholder: "Ваше имя",
    usernamePlaceholder: "your_username",
    previewLabel: "Сегодня",
    previewAnswers: "ответили",
    previewChoices: "вариантов",
    previewBubbleA: "Что сделает сегодняшний вечер теплее?",
    previewBubbleB: "Прогулка, чай и без телефонов.",
    goalsTitle: "Общие цели",
    placesTitle: "Места для двоих",
    datesTitle: "Свидания и планы",
    activitiesTitle: "Активность на сегодня",
    wishesTitle: "Желания",
    importantDatesTitle: "Важные даты",
    close: "Закрыть"
  };
}

function screenTitle(page, t) {
  const map = {
    home: "lovio",
    stats: t.statsTitle || "Статистика отношений",
    goals: t.goals,
    places: t.places,
    dates: t.dates,
    activities: t.activities,
    wishes: t.wishes,
    importantDates: t.importantDates,
    settings: t.settings
  };
  return map[page] || "lovio";
}

function screenSubtitle(page, t, hasPartner) {
  if (page === "stats") return t.statsSubtitle || "Короткий срез вашей общей динамики и привычек.";
  if (page === "goals") return "Общие ориентиры и то, что хочется успеть вместе.";
  if (page === "places") return "Сохраняйте места, куда хотите сходить вдвоем.";
  if (page === "dates") return "Планы на встречи и ближайшие свидания.";
  if (page === "activities") return "Одна активность в день, без случайной смены.";
  if (page === "wishes") return "Небольшие желания и идеи для заботы.";
  if (page === "importantDates") return "Даты, которые важно помнить.";
  if (page === "settings") return "Язык приложения и базовые настройки.";
  return hasPartner ? "Ежедневная близость, планы и один общий ритм." : "Сначала пригласите партнера в приложение.";
}

function screenSubtitleText(page, t, hasPartner) {
  const ru = (state.data?.user?.language || "ru") === "ru";
  if (page === "stats") return t.statsSubtitle || (ru ? "Короткий срез вашей общей динамики и привычек." : "A quick view of your shared rhythm and habits.");
  if (page === "goals") return ru ? "Общие ориентиры и то, что хочется успеть вместе." : "Shared goals and things you want to reach together.";
  if (page === "places") return ru ? "Сохраняйте места, куда хотите сходить вдвоем." : "Keep the places you want to visit together.";
  if (page === "dates") return ru ? "Планы на встречи и ближайшие свидания." : "Plans for your next dates and shared time.";
  if (page === "activities") return ru ? "Одна активность в день без случайной смены." : "One activity per day with no random switching.";
  if (page === "wishes") return ru ? "Небольшие желания и идеи для заботы." : "Small wishes and ideas for thoughtful moments.";
  if (page === "importantDates") return ru ? "Даты, которые важно помнить." : "Dates that matter and should stay remembered.";
  if (page === "settings") return ru ? "Язык приложения и базовые настройки." : "App language and core preferences.";
  return hasPartner
    ? (ru ? "Ежедневная близость, планы и один общий ритм." : "Daily closeness, plans, and one shared rhythm.")
    : (ru ? "Сначала пригласите партнера в приложение." : "Invite your partner first to unlock the shared space.");
}

function hasNotificationSupport() {
  return typeof window !== "undefined" && "Notification" in window;
}

function isNotificationsEnabled() {
  return hasNotificationSupport() && Notification.permission === "granted";
}

function notifyAboutUpdates(previousData, nextData) {
  if (!previousData?.user || !nextData?.user || previousData.user.id !== nextData.user.id) {
    return;
  }
  if (!isNotificationsEnabled()) {
    return;
  }
  if (!document.hidden && document.hasFocus()) {
    return;
  }

  const ux = getUxCopy();
  const previousInvites = previousData.invitations?.length || 0;
  const nextInvites = nextData.invitations?.length || 0;
  if (nextInvites > previousInvites) {
    sendBrowserNotification(ux.browserInviteTitle, ux.browserInviteBody);
    return;
  }

  const sections = [
    ["goals", nextData.t?.goals || "Goals"],
    ["places", nextData.t?.places || "Places"],
    ["dates", nextData.t?.dates || "Dates"],
    ["activities", nextData.t?.activities || "Activities"],
    ["wishes", nextData.t?.wishes || "Wishes"],
    ["importantDates", nextData.t?.importantDates || "Important dates"]
  ];

  for (const [key, label] of sections) {
    const before = Number(previousData.unreadCounts?.[key] || 0);
    const after = Number(nextData.unreadCounts?.[key] || 0);
    if (after > before) {
      sendBrowserNotification(ux.browserUpdateTitle, `${label}: +${after - before}`);
      return;
    }
  }

  if (previousData.prompt?.myResponse && !nextData.prompt?.myResponse) {
    sendBrowserNotification(ux.browserPromptTitle, ux.browserPromptBody);
  }
}

function sendBrowserNotification(title, body) {
  try {
    new Notification(title, { body, silent: false });
  } catch {}
}

function getOnboardingSteps(data, ux) {
  return [
    {
      title: ux.stepInviteTitle,
      copy: data.partner ? ux.stepInviteDone : ux.stepInviteCopy,
      status: data.partner ? ux.stepDone : ux.stepStart,
      done: Boolean(data.partner),
      locked: false,
      actionLabel: data.partner ? "" : ux.stepInviteAction,
      actionAttr: 'data-scroll-target="invite-form"',
      primary: true
    },
    {
      title: ux.stepPromptTitle,
      copy: !data.partner ? ux.stepPromptLocked : data.prompt?.myResponse ? ux.stepPromptDone : ux.stepPromptCopy,
      status: data.prompt?.myResponse ? ux.stepDone : !data.partner ? ux.stepSoon : ux.stepStart,
      done: Boolean(data.prompt?.myResponse),
      locked: !data.partner,
      actionLabel: data.partner && !data.prompt?.myResponse ? ux.stepPromptAction : "",
      actionAttr: 'data-open-prompt="1"',
      primary: false
    },
    {
      title: ux.stepNotificationsTitle,
      copy: isNotificationsEnabled() ? ux.stepNotificationsDone : ux.stepNotificationsCopy,
      status: isNotificationsEnabled() ? ux.stepDone : ux.stepOptional,
      done: isNotificationsEnabled(),
      locked: false,
      actionLabel: isNotificationsEnabled() ? "" : ux.stepNotificationsAction,
      actionAttr: 'data-enable-notifications="1"',
      primary: false
    }
  ];
}

function getUxCopy() {
  const ru = (state.data?.user?.language || "ru") === "ru";
  return ru
    ? {
        onboardingKicker: "Первый запуск",
        onboardingTitle: "Давайте быстро настроим Lovio",
        onboardingSubtitle: "Три спокойных шага, чтобы приложение сразу стало полезным для вас обоих.",
        stepInviteTitle: "Пригласи партнера",
        stepInviteCopy: "Отправь приглашение и открой общее пространство для двоих.",
        stepInviteDone: "Партнер уже подключен. Теперь можно двигаться дальше.",
        stepInviteAction: "Пригласить",
        stepPromptTitle: "Ответь на вопрос дня",
        stepPromptCopy: "Первый ответ задаст ритм вашему общению уже сегодня.",
        stepPromptDone: "Ответ сохранен. Когда ответит партнер, вы увидите оба ответа.",
        stepPromptLocked: "Этот шаг откроется сразу после подключения партнера.",
        stepPromptAction: "Ответить",
        stepNotificationsTitle: "Включи уведомления",
        stepNotificationsCopy: "Так будет проще не пропускать новые записи и приглашения.",
        stepNotificationsDone: "Уведомления разрешены на этом устройстве.",
        stepNotificationsAction: "Включить",
        stepDone: "Готово",
        stepStart: "Следующий",
        stepSoon: "Скоро",
        stepOptional: "Желательно",
        notificationsKicker: "Устройство",
        notificationsTitle: "Уведомления",
        notificationsEnabledCopy: "Браузерные уведомления уже разрешены. Новые события будут заметнее.",
        notificationsDisabledCopy: "Разреши уведомления, чтобы быстрее замечать новые ответы, записи и приглашения.",
        notificationsUnavailableCopy: "На этом устройстве браузер не дает включить уведомления из текущего режима.",
        notificationsEnabledBadge: "Включены",
        notificationsDisabledBadge: "Выключены",
        notificationsUnavailableBadge: "Недоступно",
        notificationsAction: "Разрешить уведомления",
        notificationsEnabledToast: "Уведомления включены",
        notificationsDeniedToast: "Разрешение не выдано",
        pendingInvitesKicker: "Ожидают ответа",
        pendingInvitesTitle: "Приглашения от партнера",
        emptyGoalsTitle: "Пока нет ни одной общей цели",
        emptyGoalsCopy: "Добавьте первую маленькую цель или сразу запланируйте свидание.",
        emptyGoalsPrimary: "Добавить цель",
        emptyGoalsSecondary: "Открыть свидания",
        emptyPlacesTitle: "Список мест пока пуст",
        emptyPlacesCopy: "Сохраните первое место, куда хочется выбраться вдвоем.",
        emptyPlacesPrimary: "Добавить место",
        emptyDatesTitle: "Свидания еще не запланированы",
        emptyDatesCopy: "Назначьте первое свидание или начните с общей цели.",
        emptyDatesPrimary: "Запланировать свидание",
        emptyDatesSecondary: "Открыть цели",
        emptyWishesTitle: "Желаний пока нет",
        emptyWishesCopy: "Запишите маленькую мечту, подарок или идею для заботы.",
        emptyWishesPrimary: "Добавить желание",
        emptyImportantDatesTitle: "Здесь еще нет важных дат",
        emptyImportantDatesCopy: "Добавьте годовщину, день рождения или любой особенный день.",
        emptyImportantDatesPrimary: "Добавить дату",
        browserInviteTitle: "Lovio",
        browserInviteBody: "У вас новое приглашение.",
        browserUpdateTitle: "Lovio: новое обновление",
        browserPromptTitle: "Lovio: вопрос дня",
        browserPromptBody: "Появился новый вопрос дня."
      }
    : {
        onboardingKicker: "First launch",
        onboardingTitle: "Let’s set up Lovio",
        onboardingSubtitle: "Three calm steps so the app feels useful right away.",
        stepInviteTitle: "Invite your partner",
        stepInviteCopy: "Send an invite to unlock your shared space.",
        stepInviteDone: "Your partner is already connected.",
        stepInviteAction: "Invite",
        stepPromptTitle: "Answer today’s question",
        stepPromptCopy: "Your first answer sets the tone for today.",
        stepPromptDone: "Your answer is saved. Both answers open once your partner replies.",
        stepPromptLocked: "This step unlocks after your partner joins.",
        stepPromptAction: "Answer",
        stepNotificationsTitle: "Enable notifications",
        stepNotificationsCopy: "This helps you notice new updates and invites faster.",
        stepNotificationsDone: "Notifications are already enabled on this device.",
        stepNotificationsAction: "Enable",
        stepDone: "Done",
        stepStart: "Next",
        stepSoon: "Soon",
        stepOptional: "Optional",
        notificationsKicker: "Device",
        notificationsTitle: "Notifications",
        notificationsEnabledCopy: "Browser notifications are already enabled.",
        notificationsDisabledCopy: "Allow notifications to notice new answers, invites, and updates faster.",
        notificationsUnavailableCopy: "Notifications are not available in the current browser mode on this device.",
        notificationsEnabledBadge: "Enabled",
        notificationsDisabledBadge: "Off",
        notificationsUnavailableBadge: "Unavailable",
        notificationsAction: "Allow notifications",
        notificationsEnabledToast: "Notifications enabled",
        notificationsDeniedToast: "Permission was not granted",
        pendingInvitesKicker: "Waiting",
        pendingInvitesTitle: "Partner invitations",
        emptyGoalsTitle: "No shared goals yet",
        emptyGoalsCopy: "Add your first small goal or jump straight to planning a date.",
        emptyGoalsPrimary: "Add goal",
        emptyGoalsSecondary: "Open dates",
        emptyPlacesTitle: "No places saved yet",
        emptyPlacesCopy: "Save the first place you want to visit together.",
        emptyPlacesPrimary: "Add place",
        emptyDatesTitle: "No dates planned yet",
        emptyDatesCopy: "Plan your first date or start with a shared goal.",
        emptyDatesPrimary: "Plan date",
        emptyDatesSecondary: "Open goals",
        emptyWishesTitle: "No wishes yet",
        emptyWishesCopy: "Add a little dream, gift idea, or thoughtful wish.",
        emptyWishesPrimary: "Add wish",
        emptyImportantDatesTitle: "No important dates yet",
        emptyImportantDatesCopy: "Save an anniversary, birthday, or any meaningful day.",
        emptyImportantDatesPrimary: "Add date",
        browserInviteTitle: "Lovio",
        browserInviteBody: "You have a new invitation.",
        browserUpdateTitle: "Lovio: new update",
        browserPromptTitle: "Lovio: daily question",
        browserPromptBody: "A new question of the day is ready."
      };
}

function countAnswers(prompt) {
  return prompt?.bothAnswered ? prompt.responses.length : prompt?.myResponse ? 1 : 0;
}

function getClosenessScore(data) {
  let score = 22;
  if (data.partner) score += 18;
  if (data.prompt?.myResponse) score += 20;
  if (data.prompt?.bothAnswered) score += 14;
  if (data.activities?.mySelection) score += 12;
  score += Math.min(12, Math.floor((Number(data.coupleXp || 0) / 2)));
  const openGoals = (data.goals || []).filter((item) => !item.completed).length;
  score += Math.max(0, 18 - openGoals * 3);
  return Math.max(18, Math.min(100, score));
}

function statusLabel(status, t) {
  if (status === "accepted") return t.statusAccepted;
  if (status === "declined") return t.statusDeclined;
  return t.statusPending;
}

function pillClass(status) {
  if (status === "accepted") return "accepted";
  if (status === "declined") return "declined";
  return "pending";
}

function renderCounter(value, total = null) {
  if (!value) return "";
  return `<span class="badge">${total ? `${value}/${total}` : value}</span>`;
}

function formatDuration(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

function icon(path) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${path}"></path></svg>`;
}

function closeIcon() {
  return icon("M6 6l12 12M18 6 6 18");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
