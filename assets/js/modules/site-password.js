const STORAGE_KEY = "site-password-ok";
const PASSWORD = "test-server";

function isUnlocked() {
  try {
    return sessionStorage.getItem(STORAGE_KEY) === "1";
  } catch {
    return false;
  }
}

function unlock() {
  try {
    sessionStorage.setItem(STORAGE_KEY, "1");
  } catch {
    // Ignore storage errors; gate will reappear on next visit.
  }
}

function createGate() {
  const gate = document.createElement("div");
  gate.className = "site-password";
  gate.setAttribute("data-site-password", "");
  gate.setAttribute("role", "dialog");
  gate.setAttribute("aria-modal", "true");
  gate.setAttribute("aria-labelledby", "site-password-title");

  gate.innerHTML = `
    <div class="site-password__card">
      <h1 class="site-password__title" id="site-password-title">Вход на сайт</h1>
      <p class="site-password__text">Введите пароль для просмотра тестовой версии.</p>
      <form class="site-password__form" data-site-password-form novalidate>
        <div class="site-password__field">
          <label class="site-password__label" for="site-password-input">Пароль</label>
          <input
            class="site-password__input"
            id="site-password-input"
            name="password"
            type="password"
            autocomplete="current-password"
            required
            data-site-password-input
          >
        </div>
        <p class="site-password__error" data-site-password-error hidden>Неверный пароль</p>
        <button class="site-password__submit button button--light" type="submit">
          Войти
        </button>
      </form>
    </div>
  `;

  return gate;
}

function showGate() {
  const gate = createGate();
  const form = gate.querySelector("[data-site-password-form]");
  const input = gate.querySelector("[data-site-password-input]");
  const error = gate.querySelector("[data-site-password-error]");

  document.body.classList.add("body--lock");
  document.body.append(gate);

  if (input instanceof HTMLInputElement) {
    input.focus();
  }

  if (!(form instanceof HTMLFormElement)) {
    return;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();

    const value = input instanceof HTMLInputElement ? input.value.trim() : "";

    if (value !== PASSWORD) {
      if (error) {
        error.hidden = false;
      }

      if (input instanceof HTMLInputElement) {
        input.value = "";
        input.focus();
      }

      return;
    }

    unlock();
    document.body.classList.remove("body--lock");
    gate.remove();
  });
}

export function initSitePassword() {
  if (isUnlocked()) {
    return;
  }

  if (document.querySelector("[data-site-password]")) {
    return;
  }

  showGate();
}
