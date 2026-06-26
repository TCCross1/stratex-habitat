// Lightweight in-app navigation history so the global Back button always
// returns to the real previous page and never bounces through /login.
let stack = [];

export function recordPath(path) {
  if (!path || path === "/login") return;
  if (stack[stack.length - 1] !== path) stack.push(path);
  if (stack.length > 40) stack.shift();
}

// Pops the current page and returns the previous one (or null if none).
export function popBack() {
  if (stack.length >= 2) {
    stack.pop();
    return stack[stack.length - 1];
  }
  return null;
}

export function canGoBack() {
  return stack.length >= 2;
}
