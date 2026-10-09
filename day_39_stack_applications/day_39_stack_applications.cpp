#include <algorithm>
#include <cmath>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

/*
 * Stack Applications Case Study
 *
 * Scenario:
 * A command-processing service evaluates expressions, validates nested
 * configuration syntax, models active function calls, and maintains an
 * editable command history.
 *
 * C++ is used here to emphasize explicit data structures, ownership,
 * exception-based validation, and predictable algorithmic complexity.
 */

class DelimiterValidator {
public:
    static bool balanced(const std::string& text) {
        const std::unordered_map<char, char> matching{
            {')', '('},
            {']', '['},
            {'}', '{'}
        };

        const std::unordered_map<char, char> opening{
            {'(', ')'},
            {'[', ']'},
            {'{', '}'}
        };

        std::vector<char> stack;
        char quote = '\0';
        bool escaped = false;

        for (char character : text) {
            if (quote != '\0') {
                if (escaped) {
                    escaped = false;
                } else if (character == '\\') {
                    escaped = true;
                } else if (character == quote) {
                    quote = '\0';
                }
                continue;
            }

            if (character == '"' || character == '\'') {
                quote = character;
            } else if (opening.contains(character)) {
                stack.push_back(character);
            } else if (matching.contains(character)) {
                if (stack.empty() || stack.back() != matching.at(character)) {
                    return false;
                }
                stack.pop_back();
            }
        }

        return quote == '\0' && stack.empty();
    }
};


// -----------------------------------------------------------------------------
// Expression Engine
// -----------------------------------------------------------------------------

enum class TokenType {
    Number,
    Operator,
    LeftParen,
    RightParen
};

struct Token {
    TokenType type;
    std::string value;
};

class ExpressionEngine {
private:
    static int precedence(char op) {
        switch (op) {
            case '+':
            case '-':
                return 1;
            case '*':
            case '/':
            case '%':
                return 2;
            case '^':
                return 3;
            default:
                return -1;
        }
    }

    static bool rightAssociative(char op) {
        return op == '^';
    }

    static bool isOperator(char character) {
        return std::string("+-*/%^").find(character) != std::string::npos;
    }

    static std::vector<Token> tokenize(const std::string& expression) {
        std::vector<Token> tokens;

        for (std::size_t i = 0; i < expression.size();) {
            char character = expression[i];

            if (std::isspace(static_cast<unsigned char>(character))) {
                ++i;
                continue;
            }

            if (std::isdigit(static_cast<unsigned char>(character)) || character == '.') {
                std::size_t start = i;
                bool decimalSeen = false;

                while (i < expression.size()) {
                    char current = expression[i];

                    if (current == '.') {
                        if (decimalSeen) {
                            throw std::invalid_argument("Invalid numeric literal.");
                        }
                        decimalSeen = true;
                        ++i;
                    } else if (std::isdigit(static_cast<unsigned char>(current))) {
                        ++i;
                    } else {
                        break;
                    }
                }

                if (expression.substr(start, i - start) == ".") {
                    throw std::invalid_argument("Invalid numeric literal.");
                }

                tokens.push_back({TokenType::Number, expression.substr(start, i - start)});
                continue;
            }

            if (character == '(') {
                tokens.push_back({TokenType::LeftParen, "("});
                ++i;
                continue;
            }

            if (character == ')') {
                tokens.push_back({TokenType::RightParen, ")"});
                ++i;
                continue;
            }

            if (isOperator(character)) {
                tokens.push_back({TokenType::Operator, std::string(1, character)});
                ++i;
                continue;
            }

            throw std::invalid_argument("Unsupported character in expression.");
        }

        if (tokens.empty()) {
            throw std::invalid_argument("Expression cannot be empty.");
        }

        return tokens;
    }

public:
    static std::vector<Token> toPostfix(const std::string& expression) {
        const auto tokens = tokenize(expression);
        std::vector<Token> output;
        std::vector<char> operators;
        std::optional<TokenType> previous;

        for (const Token& token : tokens) {
            if (token.type == TokenType::Number) {
                output.push_back(token);
                previous = TokenType::Number;
                continue;
            }

            if (token.type == TokenType::LeftParen) {
                operators.push_back('(');
                previous = TokenType::LeftParen;
                continue;
            }

            if (token.type == TokenType::RightParen) {
                bool foundOpening = false;

                while (!operators.empty()) {
                    char top = operators.back();
                    operators.pop_back();

                    if (top == '(') {
                        foundOpening = true;
                        break;
                    }

                    output.push_back({TokenType::Operator, std::string(1, top)});
                }

                if (!foundOpening) {
                    throw std::invalid_argument("Unmatched closing parenthesis.");
                }

                previous = TokenType::RightParen;
                continue;
            }

            char current = token.value[0];

            // Unary minus is normalized as 0 - expression so the evaluator
            // can remain a binary-operation stack machine.
            if (current == '-' &&
                (!previous.has_value() ||
                 previous == TokenType::Operator ||
                 previous == TokenType::LeftParen)) {
                output.push_back({TokenType::Number, "0"});
            }

            while (!operators.empty() && operators.back() != '(') {
                char top = operators.back();

                bool shouldPop =
                    precedence(top) > precedence(current) ||
                    (precedence(top) == precedence(current) &&
                     !rightAssociative(current));

                if (!shouldPop) {
                    break;
                }

                operators.pop_back();
                output.push_back(
                    {TokenType::Operator, std::string(1, top)}
                );
            }

            operators.push_back(current);
            previous = TokenType::Operator;
        }

        while (!operators.empty()) {
            char top = operators.back();
            operators.pop_back();

            if (top == '(') {
                throw std::invalid_argument("Unmatched opening parenthesis.");
            }

            output.push_back({TokenType::Operator, std::string(1, top)});
        }

        return output;
    }

    static double evaluate(const std::vector<Token>& postfix) {
        std::vector<double> values;

        for (const Token& token : postfix) {
            if (token.type == TokenType::Number) {
                values.push_back(std::stod(token.value));
                continue;
            }

            if (values.size() < 2) {
                throw std::invalid_argument("Insufficient operands.");
            }

            const double right = values.back();
            values.pop_back();

            const double left = values.back();
            values.pop_back();

            double result = 0.0;

            switch (token.value[0]) {
                case '+':
                    result = left + right;
                    break;
                case '-':
                    result = left - right;
                    break;
                case '*':
                    result = left * right;
                    break;
                case '/':
                    if (right == 0.0) {
                        throw std::domain_error("Division by zero.");
                    }
                    result = left / right;
                    break;
                case '%':
                    if (right == 0.0) {
                        throw std::domain_error("Remainder by zero.");
                    }
                    result = std::fmod(left, right);
                    break;
                case '^':
                    result = std::pow(left, right);
                    break;
                default:
                    throw std::invalid_argument("Unknown operator.");
            }

            if (!std::isfinite(result)) {
                throw std::overflow_error("Non-finite expression result.");
            }

            values.push_back(result);
        }

        if (values.size() != 1) {
            throw std::invalid_argument("Malformed postfix expression.");
        }

        return values.back();
    }
};


// -----------------------------------------------------------------------------
// Function-Call Stack
// -----------------------------------------------------------------------------

struct ActivationRecord {
    std::string functionName;
    std::vector<std::string> arguments;
    std::unordered_map<std::string, std::string> locals;
};

class CallStack {
private:
    std::vector<ActivationRecord> frames;

public:
    void call(
        const std::string& functionName,
        std::vector<std::string> arguments = {}
    ) {
        frames.push_back({
            functionName,
            std::move(arguments),
            {}
        });
    }

    ActivationRecord returnFromCall() {
        if (frames.empty()) {
            throw std::underflow_error("Cannot return from empty call stack.");
        }

        ActivationRecord frame = std::move(frames.back());
        frames.pop_back();
        return frame;
    }

    std::size_t depth() const {
        return frames.size();
    }

    void print() const {
        for (std::size_t index = 0; index < frames.size(); ++index) {
            std::cout << "  frame[" << index << "] "
                      << frames[index].functionName << '\n';
        }
    }
};


// -----------------------------------------------------------------------------
// Undo / Redo Command History
// -----------------------------------------------------------------------------

struct DocumentState {
    std::string text;
};

class DocumentHistory {
private:
    DocumentState current;
    std::vector<DocumentState> undoStack;
    std::vector<DocumentState> redoStack;

public:
    explicit DocumentHistory(std::string initial = "")
        : current{std::move(initial)} {}

    void edit(std::string nextText) {
        if (nextText == current.text) {
            return;
        }

        undoStack.push_back(current);
        current.text = std::move(nextText);

        // Editing after undo creates a new timeline, so redo states become
        // unreachable and must be discarded.
        redoStack.clear();
    }

    bool undo() {
        if (undoStack.empty()) {
            return false;
        }

        redoStack.push_back(current);
        current = std::move(undoStack.back());
        undoStack.pop_back();
        return true;
    }

    bool redo() {
        if (redoStack.empty()) {
            return false;
        }

        undoStack.push_back(current);
        current = std::move(redoStack.back());
        redoStack.pop_back();
        return true;
    }

    const std::string& text() const {
        return current.text;
    }
};


// -----------------------------------------------------------------------------
// Repository-like Command Processing Scenario
// -----------------------------------------------------------------------------

class CommandProcessor {
public:
    static void execute(const std::string& command) {
        // A command is accepted only when its nested argument syntax is valid.
        if (!DelimiterValidator::balanced(command)) {
            throw std::invalid_argument(
                "Command rejected because nested delimiters are unbalanced."
            );
        }

        std::cout << "Accepted command: " << command << '\n';
    }
};


int main() {
    std::cout << "=== Balanced Delimiter Validation ===\n";

    for (const std::string& input : {
        "process([1, 2, {value: 3}])",
        "process([1, 2, {value: 3})",
        "print(\"array[0]\")"
    }) {
        std::cout << input << " -> "
                  << (DelimiterValidator::balanced(input) ? "valid" : "invalid")
                  << '\n';
    }

    std::cout << "\n=== Expression Evaluation ===\n";

    for (const std::string& expression : {
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "2 ^ 3 ^ 2",
        "-5 + 3 * 4"
    }) {
        try {
            auto postfix = ExpressionEngine::toPostfix(expression);
            double result = ExpressionEngine::evaluate(postfix);

            std::cout << expression << " = " << result << '\n';
        } catch (const std::exception& error) {
            std::cout << expression << " rejected: "
                      << error.what() << '\n';
        }
    }

    std::cout << "\n=== Function Call Simulation ===\n";

    CallStack callStack;
    callStack.call("main");
    callStack.call("handleRequest", {"REQ-2048"});
    callStack.call("evaluateExpression", {"3 * (4 + 2)"});

    std::cout << "Active frames:\n";
    callStack.print();

    auto completed = callStack.returnFromCall();
    std::cout << "Returned from " << completed.functionName << '\n';

    callStack.returnFromCall();
    callStack.returnFromCall();

    std::cout << "Remaining stack depth: "
              << callStack.depth() << '\n';

    std::cout << "\n=== Undo / Redo ===\n";

    DocumentHistory history;
    history.edit("Draft expression");
    history.edit("Draft expression with validation");
    history.edit("Draft expression with validation and logging");

    std::cout << "Current: " << history.text() << '\n';

    history.undo();
    std::cout << "After undo: " << history.text() << '\n';

    history.undo();
    std::cout << "After second undo: " << history.text() << '\n';

    history.redo();
    std::cout << "After redo: " << history.text() << '\n';

    history.edit("New document branch");
    std::cout << "After new edit: " << history.text() << '\n';

    std::cout << "\n=== Command Validation ===\n";

    try {
        CommandProcessor::execute(
            "deploy(environment[production], options({safe: true}))"
        );

        CommandProcessor::execute(
            "deploy(environment[production], options({safe: true})"
        );
    } catch (const std::exception& error) {
        std::cout << "Command failure: " << error.what() << '\n';
    }

    /*
     * Complexity:
     * Delimiter validation is O(n) time and O(n) auxiliary stack space.
     * Infix-to-postfix conversion is O(n) time and O(n) space.
     * Postfix evaluation is O(n) time and O(n) space.
     * Call-stack push/pop are amortized O(1).
     * Undo/redo push/pop are amortized O(1), excluding state-copy cost.
     *
     * Production systems often store commands or immutable deltas instead of
     * complete document snapshots when states are large.
     */
    return 0;
}
