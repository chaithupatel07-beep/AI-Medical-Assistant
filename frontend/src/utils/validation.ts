export interface PasswordCheckResult {
  valid: boolean;
  checks: {
    length: boolean;
    upper: boolean;
    lower: boolean;
    digit: boolean;
    special: boolean;
  };
  message: string;
}

export function evaluatePassword(password: string): PasswordCheckResult {
  const checks = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };

  const missing: string[] = [];
  if (!checks.length) missing.push("8+ characters");
  if (!checks.upper) missing.push("uppercase letter");
  if (!checks.lower) missing.push("lowercase letter");
  if (!checks.digit) missing.push("number");
  if (!checks.special) missing.push("special character");

  return {
    valid: missing.length === 0,
    checks,
    message: missing.length === 0 ? "Strong password" : `Requires ${missing.join(", ")}`,
  };
}

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}
