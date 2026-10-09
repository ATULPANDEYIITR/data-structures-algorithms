"use strict";

/*
 * Stack Applications
 *
 * This file uses JavaScript-specific features to demonstrate:
 * balanced delimiters, event-driven expression evaluation,
 * function-call simulation, and undo/redo history.
 */

// -----------------------------------------------------------------------------
// Balanced Parentheses
// -----------------------------------------------------------------------------

const openingBrackets = new Map([
  ["(", ")"],
  ["[", "]"],
  ["{", "}"],
]);

const closingBrackets = new Map([
  [")", "("],
  ["]", "["],
  ["}", "{"],
]);

function validateBrackets(text) {
  const stack = [];
  let quote = null;
  let escaped = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];

    if (quote !== null) {
      if (escaped) {
        escaped = false;
      } else if (character === "\\") {
        escaped = true;
      } else if (character === quote) {
        quote = null;
      }
      continue;
    }

    if (character === "'" || character === '"') {
      quote = character;
    } else if (openingBrackets.has(character)) {
      stack.push({ bracket: character, index });
    } else if (closingBrackets.has(character)) {
      if (stack.length === 0) {
        return {
          valid: false,
          message: `Unexpected ${character} at index ${index}`,
        };
      }

      const opening = stack.pop();
      if (opening.bracket !== closingBrackets.get(character)) {
        return {
          valid: false,
          message: `Expected ${openingBrackets.get(opening.bracket)} for ${opening.bracket} at index ${opening.index}`,
        };
      }
    }
  }

  if (quote !== null) {
    return { valid: false, message: "Unterminated quoted string" };
  }

  if (stack.length > 0) {
    const unmatched = stack[stack.length - 1];
    return {
      valid: false,
      message: `Unclosed ${unmatched.bracket} at index ${unmatched.index}`,
    };
  }

  return { valid: true, message: "Balanced" };
}

// -----------------------------------------------------------------------------
// Expression Evaluation
// -----------------------------------------------------------------------------

const precedence = new Map([
  ["+", 1],
  ["-", 1],
  ["*", 2],
  ["/", 2],
  ["%", 2],
  ["^", 3],
]);

const operators = {
  "+": (left, right) => left + right,
  "-": (left, right) => left - right,
  "*": (left, right) => left * right,
  "/": (left, right) => {
    if (right === 0) throw new RangeError("Division by zero");
    return left / right;
  },
  "%": (left, right) => {
    if (right === 0) throw new RangeError("Remainder by zero");
    return left % right;
  },
  "^": (left, right) => left ** right,
};

function tokenizeExpression(expression) {
  const tokens = [];
  let index = 0;

  while (index < expression.length) {
    const character = expression[index];

    if (/\s/.test(character)) {
      index += 1;
      continue;
    }

    const numberMatch = expression.slice(index).match(/^(?:\d+(?:\.\d*)?|\.\d+)/);
    if (numberMatch) {
      tokens.push({ type: "number", value: Number(numberMatch[0]) });
      index += numberMatch[0].length;
      continue;
    }

    if ("+-*/%^()".includes(character)) {
      tokens.push({ type: "operator", value: character });
      index += 1;
      continue;
    }

    throw new SyntaxError(`Unexpected character ${character} at index ${index}`);
  }

  return tokens;
}

function toPostfix(expression) {
  const tokens = tokenizeExpression(expression);
  const output = [];
  const stack = [];
  let previous = null;

  for (const token of tokens) {
    if (token.type === "number") {
      output.push(token);
      previous = "number";
      continue;
    }

    const symbol = token.value;

    if (symbol === "(") {
      stack.push(symbol);
      previous = "left-paren";
      continue;
    }

    if (symbol === ")") {
      let foundOpening = false;

      while (stack.length > 0) {
        const top = stack.pop();
        if (top === "(") {
          foundOpening = true;
          break;
        }
        output.push({ type: "operator", value: top });
      }

      if (!foundOpening) {
        throw new SyntaxError("Unmatched closing parenthesis");
      }

      previous = "right-paren";
      continue;
    }

    let currentOperator = symbol;

    // JavaScript does not need a special unary operator object here.
    // Converting unary minus to 0 - value keeps the evaluator intentionally
    // small while preserving the stack-based evaluation model.
    if (
      currentOperator === "-" &&
      (previous === null || previous === "operator" || previous === "left-paren")
    ) {
      output.push({ type: "number", value: 0 });
    }

    while (stack.length > 0 && stack[stack.length - 1] !== "(") {
      const top = stack[stack.length - 1];
      const shouldPop =
        precedence.get(top) > precedence.get(currentOperator) ||
        (precedence.get(top) === precedence.get(currentOperator) &&
          currentOperator !== "^");

      if (!shouldPop) break;
      output.push({ type: "operator", value: stack.pop() });
    }

    stack.push(currentOperator);
    previous = "operator";
  }

  while (stack.length > 0) {
    const top = stack.pop();
    if (top === "(") throw new SyntaxError("Unmatched opening parenthesis");
    output.push({ type: "operator", value: top });
  }

  return output;
}

function evaluatePostfix(postfix) {
  const stack = [];

  for (const token of postfix) {
    if (token.type === "number") {
      stack.push(token.value);
      continue;
    }

    if (!(token.value in operators)) {
      throw new TypeError(`Unsupported operator ${token.value}`);
    }

    if (stack.length < 2) {
      throw new SyntaxError("Insufficient operands");
    }

    const right = stack.pop();
    const left = stack.pop();
    const result = operators[token.value](left, right);

    if (!Number.isFinite(result)) {
      throw new RangeError("Expression produced a non-finite result");
    }

    stack.push(result);
  }

  if (stack.length !== 1) {
    throw new SyntaxError("Malformed expression");
  }

  return stack[0];
}

// -----------------------------------------------------------------------------
// Event-Driven Function Call Simulation
// -----------------------------------------------------------------------------

class CallStack {
  #frames = [];

  push(functionName, args = []) {
    const frame = {
      functionName,
      args: [...args],
      localVariables: new Map(),
      enteredAt: Date.now(),
    };

    this.#frames.push(frame);
    return frame;
  }

  pop(returnValue = undefined) {
    if (this.#frames.length === 0) {
      throw new Error("Cannot return from an empty call stack");
    }

    const frame = this.#frames.pop();
    frame.returnValue = returnValue;
    return frame;
  }

  get depth() {
    return this.#frames.length;
  }

  snapshot() {
    return this.#frames.map((frame) => ({
      functionName: frame.functionName,
      args: [...frame.args],
      localVariables: Object.fromEntries(frame.localVariables),
    }));
  }
}

function simulateFunctionCalls() {
  const stack = new CallStack();

  stack.push("main");
  stack.push("handleRequest", [2048]);
  stack.push("parseExpression", ["3 * (4 + 2)"]);

  console.log("Call stack before returns:", stack.snapshot());

  stack.pop(18);
  stack.pop({ status: 200 });
  stack.pop("completed");

  return stack.snapshot();
}

// -----------------------------------------------------------------------------
// Undo / Redo with Event-Driven History
// -----------------------------------------------------------------------------

class HistoryEditor extends EventTarget {
  #current;
  #undoStack = [];
  #redoStack = [];

  constructor(initialValue = "") {
    super();
    this.#current = initialValue;
  }

  get value() {
    return this.#current;
  }

  #emit(action) {
    this.dispatchEvent(
      new CustomEvent("historychange", {
        detail: {
          action,
          value: this.#current,
          undoDepth: this.#undoStack.length,
          redoDepth: this.#redoStack.length,
        },
      })
    );
  }

  edit(nextValue) {
    if (typeof nextValue !== "string") {
      throw new TypeError("Editor values must be strings");
    }

    if (nextValue === this.#current) return;

    this.#undoStack.push(this.#current);
    this.#current = nextValue;
    this.#redoStack.length = 0;
    this.#emit("edit");
  }

  undo() {
    if (this.#undoStack.length === 0) return false;

    this.#redoStack.push(this.#current);
    this.#current = this.#undoStack.pop();
    this.#emit("undo");
    return true;
  }

  redo() {
    if (this.#redoStack.length === 0) return false;

    this.#undoStack.push(this.#current);
    this.#current = this.#redoStack.pop();
    this.#emit("redo");
    return true;
  }
}

// -----------------------------------------------------------------------------
// Practical Demonstration
// -----------------------------------------------------------------------------

function main() {
  console.log("=== Balanced Parentheses ===");

  for (const sample of [
    "({[]})",
    "([)]",
    'call("array[0]")',
    "{missing",
  ]) {
    console.log(sample, "=>", validateBrackets(sample));
  }

  console.log("\n=== Expression Evaluation ===");

  for (const expression of [
    "3 + 4 * 2",
    "(3 + 4) * 2",
    "2 ^ 3 ^ 2",
    "-5 + 4 * 3",
  ]) {
    try {
      const postfix = toPostfix(expression);
      console.log(
        expression,
        "=>",
        postfix.map((token) => token.value),
        "=>",
        evaluatePostfix(postfix)
      );
    } catch (error) {
      console.error(`Expression error: ${error.message}`);
    }
  }

  console.log("\n=== Function Call Simulation ===");
  console.log("Remaining frames:", simulateFunctionCalls());

  console.log("\n=== Undo / Redo ===");

  const editor = new HistoryEditor();

  editor.addEventListener("historychange", (event) => {
    console.log(
      `${event.detail.action}: "${event.detail.value}" ` +
        `(undo=${event.detail.undoDepth}, redo=${event.detail.redoDepth})`
    );
  });

  editor.edit("Stack");
  editor.edit("Stack applications");
  editor.edit("Stack applications are useful");
  editor.undo();
  editor.undo();
  editor.redo();
  editor.edit("New history branch");

  console.log("Final editor value:", editor.value);
}

main();
