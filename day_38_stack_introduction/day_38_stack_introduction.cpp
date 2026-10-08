#include <algorithm>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

class StackError : public std::runtime_error {
public:
    explicit StackError(const std::string& message) : std::runtime_error(message) {}
};

class ArrayStack {
private:
    std::vector<std::string> items_;
    std::size_t capacity_;

public:
    explicit ArrayStack(std::size_t capacity = 0)
        : capacity_(capacity) {}

    void push(const std::string& value) {
        if (capacity_ != 0 && items_.size() >= capacity_) {
            throw StackError("stack capacity exceeded");
        }
        items_.push_back(value);
    }

    std::string pop() {
        if (items_.empty()) {
            throw StackError("cannot pop from an empty stack");
        }

        std::string value = std::move(items_.back());
        items_.pop_back();
        return value;
    }

    const std::string& peek() const {
        if (items_.empty()) {
            throw StackError("cannot peek at an empty stack");
        }
        return items_.back();
    }

    bool empty() const {
        return items_.empty();
    }

    std::size_t size() const {
        return items_.size();
    }
};

struct WorkflowEvent {
    int id;
    std::string type;
    std::string payload;
};

class WorkflowEngine {
private:
    std::vector<WorkflowEvent> pending_;
    std::vector<WorkflowEvent> processed_;

public:
    void submit(WorkflowEvent event) {
        pending_.push_back(std::move(event));
    }

    std::optional<WorkflowEvent> processLatest() {
        if (pending_.empty()) {
            return std::nullopt;
        }

        WorkflowEvent event = std::move(pending_.back());
        pending_.pop_back();
        processed_.push_back(event);
        return event;
    }

    const std::vector<WorkflowEvent>& processed() const {
        return processed_;
    }

    std::size_t pendingCount() const {
        return pending_.size();
    }
};

bool balancedDelimiters(const std::string& expression) {
    ArrayStack stack;

    const std::unordered_map<char, char> closingToOpening{
        {')', '('},
        {']', '['},
        {'}', '{'}
    };

    for (char character : expression) {
        if (character == '(' || character == '[' || character == '{') {
            stack.push(std::string(1, character));
        } else if (closingToOpening.contains(character)) {
            if (stack.empty()) {
                return false;
            }

            std::string expected(1, closingToOpening.at(character));
            if (stack.pop() != expected) {
                return false;
            }
        }
    }

    return stack.empty();
}

std::string reverseText(const std::string& text) {
    ArrayStack stack;

    for (char character : text) {
        stack.push(std::string(1, character));
    }

    std::string result;

    while (!stack.empty()) {
        result += stack.pop();
    }

    return result;
}

int main() {
    std::cout << "=== LIFO workflow case study ===\n";

    WorkflowEngine engine;

    engine.submit({101, "load", "customer-profile"});
    engine.submit({102, "validate", "customer-profile"});
    engine.submit({103, "audit", "customer-profile"});
    engine.submit({104, "retry", "customer-profile"});

    std::cout << "Pending events: " << engine.pendingCount() << '\n';

    while (engine.pendingCount() > 0) {
        auto event = engine.processLatest();

        if (event.has_value()) {
            std::cout << "Processing event " << event->id
                      << " [" << event->type << "] "
                      << event->payload << '\n';
        }
    }

    std::cout << "\n=== Balanced expression validation ===\n";

    for (const std::string& expression : {
             "({[]})",
             "([)]",
             "function(a[0])",
             "{missing-bracket"
         }) {
        std::cout << expression << " -> "
                  << (balancedDelimiters(expression) ? "balanced" : "invalid")
                  << '\n';
    }

    std::cout << "\n=== Reverse operation ===\n";
    std::cout << "LIFO -> " << reverseText("LIFO") << '\n';

    std::cout << "\n=== Fixed-capacity behavior ===\n";

    ArrayStack stack(2);
    stack.push("first");
    stack.push("second");

    std::cout << "Top: " << stack.peek() << '\n';

    try {
        stack.push("third");
    } catch (const StackError& error) {
        std::cout << "Expected overflow: " << error.what() << '\n';
    }

    std::cout << "Pop: " << stack.pop() << '\n';
    std::cout << "Pop: " << stack.pop() << '\n';

    try {
        stack.pop();
    } catch (const StackError& error) {
        std::cout << "Expected underflow: " << error.what() << '\n';
    }

    std::cout << "\n=== Complexity ===\n";
    std::cout << "std::vector-backed push/pop/peek: O(1) amortized / O(1) / O(1)\n";
    std::cout << "Workflow event submission and latest-event processing: O(1) amortized\n";
    std::cout << "Delimiter validation: O(n) time and O(n) auxiliary space\n";
    std::cout << "Text reversal: O(n) time and O(n) auxiliary space\n";
    std::cout << "A linked implementation can avoid vector resizing but adds per-node allocation overhead.\n";

    return 0;
}
