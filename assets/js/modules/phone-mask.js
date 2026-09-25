function getDigits(value) {
  return String(value || "").replace(/\D/g, "");
}

function formatPhone(digits) {
  if (!digits) {
    return "";
  }

  let normalized = digits;

  if (normalized[0] === "9") {
    normalized = "7" + normalized;
  }

  const firstSymbols = normalized[0] === "8" ? "8" : "+7";
  let result = firstSymbols + " ";

  if (normalized.length > 1) {
    result += "(" + normalized.substring(1, 4);
  }

  if (normalized.length >= 5) {
    result += ") " + normalized.substring(4, 7);
  }

  if (normalized.length >= 8) {
    result += "-" + normalized.substring(7, 9);
  }

  if (normalized.length >= 10) {
    result += "-" + normalized.substring(9, 11);
  }

  return result;
}

function isValidPhone(value) {
  return /^(?:\+7|7|8)?[\s-]?\(?[489]\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$/.test(
    value
  );
}

function onPhonePaste(event) {
  const input = event.target;
  const pasted = event.clipboardData || window.clipboardData;

  if (!pasted) {
    return;
  }

  const pastedText = pasted.getData("Text");

  if (/\D/g.test(pastedText)) {
    event.preventDefault();
    input.value = formatPhone(getDigits(input.value));
  }
}

function onPhoneInput(event) {
  const input = event.target;
  const digits = getDigits(input.value);
  const selectionStart = input.selectionStart;

  if (!digits) {
    input.value = "";
    return;
  }

  if (input.value.length !== selectionStart) {
    if (event.data && /\D/g.test(event.data)) {
      input.value = formatPhone(digits);
    }
    return;
  }

  if (["+", "7", "8", "9"].indexOf(input.value[0]) === -1) {
    input.value = "";
    return;
  }

  input.value = formatPhone(digits);
}

function onPhoneKeyDown(event) {
  const digits = getDigits(event.target.value);

  if (event.key === "Backspace" && digits.length <= 1) {
    event.target.value = "";
  }
}

export function initPhoneMask(root = document) {
  const phoneInputs = Array.from(root.querySelectorAll('input[type="tel"]'));

  phoneInputs.forEach((input) => {
    if (input.dataset.phoneMaskBound === "true") {
      return;
    }

    input.dataset.phoneMaskBound = "true";
    input.setAttribute("maxlength", "18");
    input.addEventListener("keydown", onPhoneKeyDown);
    input.addEventListener("input", onPhoneInput);
    input.addEventListener("paste", onPhonePaste);
  });
}

export { isValidPhone, getDigits as getPhoneDigits };
