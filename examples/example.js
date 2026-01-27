// Example JavaScript file with various issues

// Console.log statement (Code Smell)
console.log("Debug message");

// Using var instead of let/const (Best Practice)
var oldStyle = "should use let or const";

// Loose equality comparison
function looseEquality(x) {
    if (x == 5) {  // Should use ===
        return true;
    }
    return false;
}

// Using eval (Security Risk)
function dangerousEval(userInput) {
    return eval(userInput);
}

// Hardcoded API key (Security Issue)
const API_KEY = "pk_live_51234567890abcdefghijklmnop";

// Function with many parameters
function tooManyParams(a, b, c, d, e, f, g, h) {
    return a + b + c + d + e + f + g + h;
}

// Empty catch block
try {
    riskyOperation();
} catch (error) {
    // Empty catch - should at least log
}

// TODO: Refactor this
// FIXME: Bug in this function
function buggyFunction() {
    // Implementation
}

export { looseEquality, dangerousEval, tooManyParams };
