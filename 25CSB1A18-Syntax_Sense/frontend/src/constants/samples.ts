import type { SupportedLanguage } from '../types';

export interface CodeSample {
  id: string;
  name: string;
  description: string;
  code: string;
}

export const DEFAULT_CPP_CODE = `#include <iostream>

int main() {
    // Write or paste C++ code here for syntax diagnosis
    int number = 10
    std::cout << "Number is: " << number << std::endl;
    return 0;
}
`;

export const DEFAULT_PYTHON_CODE = `def calculate_stats(numbers: list[int]) -> dict:
    # Write or paste Python code here for syntax diagnosis
    total = sum(numbers)
    count = len(numbers)
    return {
        "total": total,
        "average": total / count if count > 0 else 0
    }

data = [10, 20, 30, 40]
print(calculate_stats(data))
`;

export const DEFAULT_JAVA_CODE = `public class Main {
    public static void main(String[] args) {
        // Write or paste Java code here for syntax diagnosis
        int total = 100;
        System.out.println("Total: " + total);
    }
}
`;

export const CPP_SAMPLES: CodeSample[] = [
  {
    id: 'missing-semicolon',
    name: 'Missing Semicolon',
    description: 'Statement missing trailing semicolon on variable declaration',
    code: `#include <iostream>

int main() {
    int total = 100
    std::cout << "Total: " << total << std::endl;
    return 0;
}
`,
  },
  {
    id: 'unmatched-brace',
    name: 'Unmatched Opening Brace',
    description: 'Inner if-block opened but missing matching closing brace',
    code: `#include <iostream>

int main() {
    if (true) {
        int x = 1;
    return 0;
}
`,
  },
  {
    id: 'unmatched-closing-brace',
    name: 'Extra Closing Brace',
    description: 'Extraneous closing brace after main function block',
    code: `#include <iostream>

int main() {
    int a = 1;
    return 0;
}}
`,
  },
  {
    id: 'unmatched-paren',
    name: 'Unmatched Parenthesis',
    description: 'If-statement condition missing closing parenthesis',
    code: `#include <iostream>

int main() {
    int x = 10;
    if (x > 5 {
        std::cout << "Greater" << std::endl;
    }
    return 0;
}
`,
  },
  {
    id: 'invalid-assignment',
    name: 'Invalid Assignment',
    description: 'Literal constant used on left-hand side of assignment',
    code: `#include <iostream>

int main() {
    int x = 10;
    42 = x;
    return 0;
}
`,
  },
  {
    id: 'missing-operand',
    name: 'Missing Operand',
    description: 'Binary operator missing right-hand operand before semicolon',
    code: `#include <iostream>

int main() {
    int total = 10 + ;
    return 0;
}
`,
  },
  {
    id: 'unexpected-token',
    name: 'Unexpected Token',
    description: 'Stray illegal non-C++ token (@) inside declaration',
    code: `#include <iostream>

int main() {
    int x = 5 @ 10;
    return 0;
}
`,
  },
  {
    id: 'multiple-errors',
    name: 'Multiple Syntax Errors',
    description: 'Multiple independent syntactic issues in a single snippet',
    code: `#include <iostream>

int main() {
    int a = 10
    100 = a;
    if (a > 0 {
        return 1;
    }
    return 0;
}
`,
  },
  {
    id: 'valid-program',
    name: 'Valid C++ Code',
    description: 'Well-formed standard C++ program with 0 syntax errors',
    code: `#include <iostream>

int main() {
    int value = 42;
    std::cout << "The answer is: " << value << std::endl;
    return 0;
}
`,
  },
];

export const PYTHON_SAMPLES: CodeSample[] = [
  {
    id: 'valid-python',
    name: 'Valid Python Program',
    description: 'Well-formed Python function and loop with 0 syntax errors',
    code: `def greet(name: str, count: int = 1) -> None:
    for i in range(count):
        print(f"Hello, {name}! ({i + 1})")

greet("SyntaxSense", 3)
`,
  },
  {
    id: 'missing-colon-py',
    name: 'Missing Colon',
    description: 'If-statement header missing terminating colon',
    code: `def check_number(val: int) -> str:
    if val > 0
        return "Positive"
    return "Non-positive"

print(check_number(10))
`,
  },
  {
    id: 'indentation-error-py',
    name: 'Indentation Error',
    description: 'Misaligned statement where unindent does not match outer block',
    code: `def process_items(items):
    results = []
    for item in items:
        results.append(item * 2)
      print("Processed item")
    return results

print(process_items([1, 2, 3]))
`,
  },
  {
    id: 'unmatched-delimiter-py',
    name: 'Unmatched Delimiter',
    description: 'List bracket opened but never closed before newline',
    code: `scores = [98, 85, 92, 77
average = sum(scores) / len(scores)
print(f"Average: {average}")
`,
  },
  {
    id: 'unclosed-string-py',
    name: 'Unclosed String Literal',
    description: 'String missing closing double quotation mark',
    code: `greeting = "Welcome to SyntaxSense
print(greeting)
`,
  },
  {
    id: 'invalid-assignment-py',
    name: 'Invalid Assignment',
    description: 'Literal constant used on left-hand side of assignment',
    code: `total = 50
100 = total
print(total)
`,
  },
];

export const JAVA_SAMPLES: CodeSample[] = [
  {
    id: 'valid-java',
    name: 'Valid Java Class',
    description: 'Standard Java class with static helper and main method',
    code: `public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }

    public static void main(String[] args) {
        System.out.println("Result: " + add(5, 7));
    }
}
`,
  },
  {
    id: 'missing-semicolon-java',
    name: 'Missing Semicolon',
    description: 'Variable declaration missing terminating semicolon',
    code: `public class Main {
    public static void main(String[] args) {
        int x = 10
        System.out.println(x);
    }
}
`,
  },
  {
    id: 'unmatched-brace-java',
    name: 'Unmatched Opening Brace',
    description: 'Block statement missing closing curly brace',
    code: `public class UnmatchedBrace {
    public static void main(String[] args) {
        if (true) {
            System.out.println("Missing closing brace");
    }
}
`,
  },
  {
    id: 'unmatched-paren-java',
    name: 'Unmatched Parenthesis',
    description: 'Conditional expression missing closing parenthesis',
    code: `public class UnmatchedParen {
    public static void main(String[] args) {
        int x = 10;
        if (x > 5 {
            System.out.println("Missing closing parenthesis");
        }
    }
}
`,
  },
  {
    id: 'invalid-conditional-java',
    name: 'Invalid Conditional',
    description: 'If statement condition missing enclosing parentheses',
    code: `public class InvalidConditional {
    public static void main(String[] args) {
        int x = 10;
        if x > 5 {
            System.out.println("Missing parentheses around condition");
        }
    }
}
`,
  },
  {
    id: 'invalid-assignment-java',
    name: 'Invalid Assignment',
    description: 'Numeric literal on left-hand side of assignment operator',
    code: `public class InvalidAssignment {
    public static void main(String[] args) {
        int count = 5;
        10 = count;
        System.out.println(count);
    }
}
`,
  },
];

/**
 * Returns the default starter code for the specified language.
 */
export function getDefaultCodeForLanguage(language: SupportedLanguage): string {
  switch (language) {
    case 'python':
      return DEFAULT_PYTHON_CODE;
    case 'java':
      return DEFAULT_JAVA_CODE;
    case 'cpp':
    default:
      return DEFAULT_CPP_CODE;
  }
}

/**
 * Returns available code samples for the specified language.
 */
export function getSamplesForLanguage(language: SupportedLanguage): CodeSample[] {
  switch (language) {
    case 'python':
      return PYTHON_SAMPLES;
    case 'java':
      return JAVA_SAMPLES;
    case 'cpp':
    default:
      return CPP_SAMPLES;
  }
}

// Backward-compatible default export
export const SAMPLE_SNIPPETS: CodeSample[] = CPP_SAMPLES;
