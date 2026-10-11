#include <algorithm>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

using namespace std;

struct RectangleResult {
    long long area = 0;
    int left = -1;
    int right = -1;
    int height = 0;
};

RectangleResult largestRectangle(const vector<int>& heights) {
    for (int height : heights) {
        if (height < 0) {
            throw invalid_argument("Histogram heights cannot be negative.");
        }
    }

    vector<int> stack;
    RectangleResult best;
    vector<int> extended = heights;
    extended.push_back(0);

    for (int i = 0; i < static_cast<int>(extended.size()); ++i) {
        while (!stack.empty() && extended[stack.back()] > extended[i]) {
            int top = stack.back();
            stack.pop_back();

            int left = stack.empty() ? 0 : stack.back() + 1;
            int right = i - 1;
            long long width = right - left + 1;
            long long area = width * extended[top];

            if (area > best.area) {
                best = {area, left, right, extended[top]};
            }
        }

        stack.push_back(i);
    }

    return best;
}

long long trappedRainwater(const vector<int>& heights) {
    for (int height : heights) {
        if (height < 0) {
            throw invalid_argument("Elevation cannot be negative.");
        }
    }

    if (heights.size() < 3) {
        return 0;
    }

    size_t left = 0;
    size_t right = heights.size() - 1;
    int leftMax = 0;
    int rightMax = 0;
    long long water = 0;

    while (left < right) {
        if (heights[left] <= heights[right]) {
            leftMax = max(leftMax, heights[left]);
            water += leftMax - heights[left];
            ++left;
        } else {
            rightMax = max(rightMax, heights[right]);
            water += rightMax - heights[right];
            --right;
        }
    }

    return water;
}

vector<int> stockSpan(const vector<int>& prices) {
    vector<int> result(prices.size());
    vector<int> stack;

    for (int day = 0; day < static_cast<int>(prices.size()); ++day) {
        while (!stack.empty() && prices[stack.back()] <= prices[day]) {
            stack.pop_back();
        }

        result[day] = stack.empty()
            ? day + 1
            : day - stack.back();

        stack.push_back(day);
    }

    return result;
}

vector<int> nextGreaterCircular(const vector<int>& values) {
    vector<int> result(values.size(), -1);
    vector<int> stack;

    for (int i = 0; i < static_cast<int>(values.size() * 2); ++i) {
        int index = i % static_cast<int>(values.size());

        while (!stack.empty() && values[stack.back()] < values[index]) {
            result[stack.back()] = values[index];
            stack.pop_back();
        }

        if (i < static_cast<int>(values.size())) {
            stack.push_back(index);
        }
    }

    return result;
}

vector<int> dailyTemperatureWaits(const vector<int>& temperatures) {
    vector<int> result(temperatures.size(), 0);
    vector<int> stack;

    for (int day = 0; day < static_cast<int>(temperatures.size()); ++day) {
        while (!stack.empty() &&
               temperatures[stack.back()] < temperatures[day]) {
            int previous = stack.back();
            stack.pop_back();
            result[previous] = day - previous;
        }

        stack.push_back(day);
    }

    return result;
}

class ExpressionParser {
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

public:
    static string toPostfix(const string& expression) {
        vector<string> tokens;
        string token;

        for (size_t i = 0; i < expression.size();) {
            char c = expression[i];

            if (isspace(static_cast<unsigned char>(c))) {
                ++i;
                continue;
            }

            if (isdigit(static_cast<unsigned char>(c)) || c == '.') {
                token.clear();

                while (i < expression.size() &&
                       (isdigit(static_cast<unsigned char>(expression[i])) ||
                        expression[i] == '.')) {
                    token += expression[i++];
                }

                tokens.push_back(token);
                continue;
            }

            if (isalpha(static_cast<unsigned char>(c)) || c == '_') {
                token.clear();

                while (i < expression.size() &&
                       (isalnum(static_cast<unsigned char>(expression[i])) ||
                        expression[i] == '_')) {
                    token += expression[i++];
                }

                tokens.push_back(token);
                continue;
            }

            tokens.emplace_back(1, c);
            ++i;
        }

        vector<string> output;
        vector<char> operators;

        for (const string& current : tokens) {
            if (current.size() > 1 ||
                isdigit(static_cast<unsigned char>(current[0]))) {
                output.push_back(current);
                continue;
            }

            char symbol = current[0];

            if (isalpha(static_cast<unsigned char>(symbol)) ||
                symbol == '_') {
                output.push_back(current);
                continue;
            }

            if (symbol == '(') {
                operators.push_back(symbol);
                continue;
            }

            if (symbol == ')') {
                while (!operators.empty() && operators.back() != '(') {
                    output.emplace_back(1, operators.back());
                    operators.pop_back();
                }

                if (operators.empty()) {
                    throw invalid_argument("Mismatched parentheses.");
                }

                operators.pop_back();
                continue;
            }

            if (precedence(symbol) < 0) {
                throw invalid_argument("Unsupported operator.");
            }

            while (!operators.empty() && operators.back() != '(') {
                char top = operators.back();

                bool popOperator =
                    precedence(top) > precedence(symbol) ||
                    (precedence(top) == precedence(symbol) &&
                     !rightAssociative(symbol));

                if (!popOperator) {
                    break;
                }

                output.emplace_back(1, top);
                operators.pop_back();
            }

            operators.push_back(symbol);
        }

        while (!operators.empty()) {
            if (operators.back() == '(') {
                throw invalid_argument("Mismatched parentheses.");
            }

            output.emplace_back(1, operators.back());
            operators.pop_back();
        }

        ostringstream result;
        for (size_t i = 0; i < output.size(); ++i) {
            if (i != 0) {
                result << ' ';
            }
            result << output[i];
        }

        return result.str();
    }

    static double evaluatePostfix(
        const string& postfix,
        const unordered_map<string, double>& variables = {}
    ) {
        istringstream input(postfix);
        string token;
        vector<double> stack;

        while (input >> token) {
            if (token.size() == 1 && string("+-*/%^").find(token[0]) != string::npos) {
                if (stack.size() < 2) {
                    throw invalid_argument("Invalid postfix expression.");
                }

                double right = stack.back();
                stack.pop_back();

                double left = stack.back();
                stack.pop_back();

                switch (token[0]) {
                    case '+': stack.push_back(left + right); break;
                    case '-': stack.push_back(left - right); break;
                    case '*': stack.push_back(left * right); break;
                    case '/':
                        if (right == 0.0) {
                            throw domain_error("Division by zero.");
                        }
                        stack.push_back(left / right);
                        break;
                    case '%':
                        stack.push_back(fmod(left, right));
                        break;
                    case '^':
                        stack.push_back(pow(left, right));
                        break;
                }
            } else {
                try {
                    size_t consumed = 0;
                    double value = stod(token, &consumed);

                    if (consumed == token.size()) {
                        stack.push_back(value);
                        continue;
                    }
                } catch (const invalid_argument&) {
                }

                auto found = variables.find(token);
                if (found == variables.end()) {
                    throw invalid_argument("Unknown operand: " + token);
                }

                stack.push_back(found->second);
            }
        }

        if (stack.size() != 1) {
            throw invalid_argument("Invalid postfix expression.");
        }

        return stack.back();
    }
};

class MatrixRectangleAnalyzer {
public:
    static int maximalRectangle(const vector<vector<int>>& matrix) {
        if (matrix.empty()) {
            return 0;
        }

        const size_t width = matrix.front().size();
        if (width == 0) {
            return 0;
        }

        for (const auto& row : matrix) {
            if (row.size() != width) {
                throw invalid_argument("Matrix must be rectangular.");
            }

            for (int value : row) {
                if (value != 0 && value != 1) {
                    throw invalid_argument("Matrix must be binary.");
                }
            }
        }

        vector<int> heights(width, 0);
        int best = 0;

        for (const auto& row : matrix) {
            for (size_t column = 0; column < width; ++column) {
                heights[column] =
                    row[column] == 1 ? heights[column] + 1 : 0;
            }

            best = max(best, static_cast<int>(largestRectangle(heights).area));
        }

        return best;
    }
};

class WarehouseMonitoringEngine {
private:
    vector<int> hourlyLoad;

public:
    explicit WarehouseMonitoringEngine(vector<int> load)
        : hourlyLoad(std::move(load)) {}

    void printCapacityAnalysis() const {
        RectangleResult result = largestRectangle(hourlyLoad);

        cout << "Peak sustained load area: " << result.area << '\n';
        cout << "Window: " << result.left << " through "
             << result.right << '\n';
        cout << "Sustained load level: " << result.height << '\n';
    }

    long long estimatedIdleCapacity() const {
        return trappedRainwater(hourlyLoad);
    }
};

template <typename T>
void printVector(const vector<T>& values) {
    cout << '[';

    for (size_t i = 0; i < values.size(); ++i) {
        if (i != 0) {
            cout << ", ";
        }
        cout << values[i];
    }

    cout << "]\n";
}

void runCaseStudy() {
    cout << "=== Histogram capacity analysis ===\n";

    vector<int> warehouseLoad = {2, 1, 5, 6, 2, 3};
    WarehouseMonitoringEngine engine(warehouseLoad);
    engine.printCapacityAnalysis();

    cout << "\n=== Rainwater capacity ===\n";
    vector<int> elevation = {4, 2, 0, 3, 2, 5};
    cout << "Trapped volume: "
         << trappedRainwater(elevation) << '\n';

    cout << "\n=== Stock span ===\n";
    vector<int> prices = {100, 80, 60, 70, 60, 75, 85};
    printVector(stockSpan(prices));

    cout << "\n=== Circular next greater values ===\n";
    printVector(nextGreaterCircular({1, 2, 1, 3}));

    cout << "\n=== Temperature waits ===\n";
    printVector(dailyTemperatureWaits({73, 74, 75, 71, 69, 72, 76, 73}));

    cout << "\n=== Expression engine ===\n";
    string expression = "3 + 4 * 2 / (1 - 5) ^ 2";
    string postfix = ExpressionParser::toPostfix(expression);

    cout << "Expression: " << expression << '\n';
    cout << "Postfix: " << postfix << '\n';
    cout << fixed << setprecision(6)
         << "Value: " << ExpressionParser::evaluatePostfix(postfix) << '\n';

    cout << "\n=== Binary matrix rectangle ===\n";
    vector<vector<int>> matrix = {
        {1, 0, 1, 0, 0},
        {1, 0, 1, 1, 1},
        {1, 1, 1, 1, 1},
        {1, 0, 0, 1, 0}
    };

    cout << "Maximum rectangle area: "
         << MatrixRectangleAnalyzer::maximalRectangle(matrix) << '\n';
}

void runFailureTests() {
    cout << "\n=== Failure handling ===\n";

    try {
        largestRectangle({2, -1, 3});
    } catch (const exception& error) {
        cout << "Rejected invalid histogram: "
             << error.what() << '\n';
    }

    try {
        MatrixRectangleAnalyzer::maximalRectangle({
            {1, 0},
            {1}
        });
    } catch (const exception& error) {
        cout << "Rejected ragged matrix: "
             << error.what() << '\n';
    }

    try {
        ExpressionParser::evaluatePostfix("10 0 /");
    } catch (const exception& error) {
        cout << "Rejected division by zero: "
             << error.what() << '\n';
    }
}

int main() {
    try {
        runCaseStudy();
        runFailureTests();

        cout << "\nAlgorithmic characteristics:\n";
        cout << "Histogram rectangle: O(n) time, O(n) stack space\n";
        cout << "Rainwater two-pointer: O(n) time, O(1) auxiliary space\n";
        cout << "Stock span: O(n) time, O(n) stack space\n";
        cout << "Next greater circular: O(n) amortized time, O(n) space\n";
        cout << "Maximal matrix rectangle: O(rows * columns) time, O(columns) stack space\n";
    } catch (const exception& error) {
        cerr << "Fatal error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
