"""
Complex Program Evaluation Dataset (Phase 6)
Addressing Professor Feedback:
"Have observed most of students are tried with simple programs.
Please try with complex programs in different programming languages."

Curated multi-language benchmark suite categorized across 3 difficulty tiers:
- Level 1: Basic (single statement/function, typos, missing punctuation)
- Level 2: Intermediate (multi-function pipelines, collections, recursion)
- Level 3: Complex (classes/inheritance, templates/generics, nested state machines, multi-method structures)
"""

from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ProgramBenchmark:
    id: str
    language: str                # 'python', 'cpp', 'java'
    complexity_level: int        # 1: Basic, 2: Intermediate, 3: Complex
    title: str
    description: str
    code: str
    expected_status: str         # 'ERROR' or 'BLOCKED'
    expected_error_type: str
    expected_line_number: int


COMPLEX_EVALUATION_DATASET: List[ProgramBenchmark] = [
    # =========================================================================
    # PYTHON FIXTURES
    # =========================================================================
    # Level 1: Basic Python
    ProgramBenchmark(
        id="PY_L1_01",
        language="python",
        complexity_level=1,
        title="Misspelled Builtin in Arithmetic Function",
        description="Single function calculating tax with a typo in the print statement.",
        code=(
            "def calculate_tax(amount, rate):\n"
            "    tax = amount * rate\n"
            "    prnt(f'Tax: {tax}')\n"
            "    return tax\n"
            "calculate_tax(100, 0.08)\n"
        ),
        expected_status="ERROR",
        expected_error_type="NameError",
        expected_line_number=3
    ),
    ProgramBenchmark(
        id="PY_L1_02",
        language="python",
        complexity_level=1,
        title="Type Concatenation Mismatch",
        description="Direct string and integer concatenation.",
        code=(
            "def format_score(player, score):\n"
            "    message = player + ' has score: ' + score\n"
            "    return message\n"
            "format_score('Alice', 95)\n"
        ),
        expected_status="ERROR",
        expected_error_type="TypeError",
        expected_line_number=2
    ),

    # Level 2: Intermediate Python
    ProgramBenchmark(
        id="PY_L2_01",
        language="python",
        complexity_level=2,
        title="Recursive Tree Path Accumulator with Unbound Variable",
        description="Binary tree recursive sum accumulator referencing an undefined helper variable.",
        code=(
            "class TreeNode:\n"
            "    def __init__(self, val=0, left=None, right=None):\n"
            "        self.val = val\n"
            "        self.left = left\n"
            "        self.right = right\n"
            "\n"
            "def max_path_sum(root):\n"
            "    def dfs(node):\n"
            "        if not node:\n"
            "            return 0\n"
            "        left_gain = max(dfs(node.left), 0)\n"
            "        right_gain = max(dfs(node.right), 0)\n"
            "        current_path = node.val + left_gain + right_gain\n"
            "        max_sum[0] = max(max_sum[0], current_path)\n"
            "        return node.val + max(left_gain, right_gain)\n"
            "    dfs(root)\n"
            "    return max_sum[0]\n"
            "root = TreeNode(10, TreeNode(2), TreeNode(10))\n"
            "max_path_sum(root)\n"
        ),
        expected_status="ERROR",
        expected_error_type="NameError",
        expected_line_number=14
    ),
    ProgramBenchmark(
        id="PY_L2_02",
        language="python",
        complexity_level=2,
        title="Transaction Ledger Processing with Key Exception",
        description="Processes a list of financial transactions and attempts to read a nonexistent key.",
        code=(
            "def process_transactions(records):\n"
            "    balances = {}\n"
            "    for tx in records:\n"
            "        user = tx['user']\n"
            "        amount = tx['amt']\n"
            "        if user not in balances:\n"
            "            balances[user] = 0.0\n"
            "        balances[user] += amount\n"
            "        fee = tx['transaction_fee']\n"
            "        balances[user] -= fee\n"
            "    return balances\n"
            "data = [{'user': 'usr_1', 'amt': 150.0}]\n"
            "process_transactions(data)\n"
        ),
        expected_status="ERROR",
        expected_error_type="KeyError",
        expected_line_number=9
    ),

    # Level 3: Complex Python
    ProgramBenchmark(
        id="PY_L3_01",
        language="python",
        complexity_level=3,
        title="Dijkstra Shortest Path with Min-Priority Queue Heap",
        description="Graph traversal algorithm with custom heap comparator having an attribute typo.",
        code=(
            "class PriorityNode:\n"
            "    def __init__(self, node_id, distance):\n"
            "        self.node_id = node_id\n"
            "        self.distance = distance\n"
            "    def __lt__(self, other):\n"
            "        return self.distance < other.distance\n"
            "\n"
            "class DijkstraSolver:\n"
            "    def __init__(self, adj_list):\n"
            "        self.adj = adj_list\n"
            "    def find_shortest(self, start, target):\n"
            "        import heapq\n"
            "        distances = {start: 0}\n"
            "        pq = [PriorityNode(start, 0)]\n"
            "        while pq:\n"
            "            curr = heapq.heappop(pq)\n"
            "            if curr.node_id == target:\n"
            "                return curr.distane\n"
            "            for nxt, weight in self.adj.get(curr.node_id, []):\n"
            "                d = curr.distance + weight\n"
            "                if d < distances.get(nxt, float('inf')):\n"
            "                    distances[nxt] = d\n"
            "                    heapq.heappush(pq, PriorityNode(nxt, d))\n"
            "        return -1\n"
            "solver = DijkstraSolver({'A': [('B', 5)], 'B': []})\n"
            "solver.find_shortest('A', 'B')\n"
        ),
        expected_status="ERROR",
        expected_error_type="AttributeError",
        expected_line_number=18
    ),
    ProgramBenchmark(
        id="PY_L3_02",
        language="python",
        complexity_level=3,
        title="LRU Cache with Doubly-Linked List and Sentinel Nodes",
        description="Full LRU cache implementation with custom doubly-linked nodes and boundary bug.",
        code=(
            "class DNode:\n"
            "    def __init__(self, key=0, val=0):\n"
            "        self.key = key\n"
            "        self.val = val\n"
            "        self.prev = None\n"
            "        self.next = None\n"
            "\n"
            "class LRUCache:\n"
            "    def __init__(self, capacity: int):\n"
            "        self.cap = capacity\n"
            "        self.cache = {}\n"
            "        self.head = DNode()\n"
            "        self.tail = DNode()\n"
            "        self.head.next = self.tail\n"
            "        self.tail.prev = self.head\n"
            "    def remove(self, node):\n"
            "        node.prev.next = node.nxt\n"
            "        node.next.prev = node.prev\n"
            "    def add_to_head(self, node):\n"
            "        node.next = self.head.next\n"
            "        node.prev = self.head\n"
            "        self.head.next.prev = node\n"
            "        self.head.next = node\n"
            "cache = LRUCache(2)\n"
            "n = DNode(1, 10)\n"
            "cache.add_to_head(n)\n"
            "cache.remove(n)\n"
        ),
        expected_status="ERROR",
        expected_error_type="AttributeError",
        expected_line_number=17
    ),

    # =========================================================================
    # C++ FIXTURES
    # =========================================================================
    # Level 1: Basic C++
    ProgramBenchmark(
        id="CPP_L1_01",
        language="cpp",
        complexity_level=1,
        title="Missing Statement Semicolon",
        description="Elementary variable declaration missing terminating semicolon.",
        code=(
            "#include <iostream>\n"
            "int main() {\n"
            "    int total_score = 42\n"
            "    std::cout << \"Score: \" << total_score << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingSemicolon",
        expected_line_number=3
    ),
    ProgramBenchmark(
        id="CPP_L1_02",
        language="cpp",
        complexity_level=1,
        title="Undeclared Scope Identifier",
        description="Referencing an undeclared symbol in standard output.",
        code=(
            "#include <iostream>\n"
            "int main() {\n"
            "    std::cout << \"Result: \" << undefined_variable << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="UndeclaredIdentifier",
        expected_line_number=3
    ),

    # Level 2: Intermediate C++
    ProgramBenchmark(
        id="CPP_L2_01",
        language="cpp",
        complexity_level=2,
        title="Inverted Stream Operator with Vector Traversal",
        description="Iterating over an integer vector and using >> with cout.",
        code=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "using namespace std;\n"
            "void print_elements(const vector<int>& nums) {\n"
            "    for (int n : nums) {\n"
            "        cout >> n >> \" \";\n"
            "    }\n"
            "}\n"
            "int main() {\n"
            "    vector<int> v = {1, 2, 3};\n"
            "    print_elements(v);\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="StreamOperatorError",
        expected_line_number=6
    ),
    ProgramBenchmark(
        id="CPP_L2_02",
        language="cpp",
        complexity_level=2,
        title="Missing Header for Dynamic String",
        description="C++ string class used without including <string> header or using std::.",
        code=(
            "#include <iostream>\n"
            "int main() {\n"
            "    string greeting = \"Welcome student!\";\n"
            "    std::cout << greeting << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="UndeclaredIdentifier",
        expected_line_number=3
    ),

    # Level 3: Complex C++
    ProgramBenchmark(
        id="CPP_L3_01",
        language="cpp",
        complexity_level=3,
        title="Templated Binary Search Tree with Syntax Error in Struct",
        description="Generic BST class template with struct definition missing terminating semicolon.",
        code=(
            "#include <iostream>\n"
            "template<typename T>\n"
            "struct BSTNode {\n"
            "    T data;\n"
            "    BSTNode* left;\n"
            "    BSTNode* right;\n"
            "    BSTNode(T val) : data(val), left(nullptr), right(nullptr) {}\n"
            "}\n"
            "template<typename T>\n"
            "class BinarySearchTree {\n"
            "    BSTNode<T>* root;\n"
            "public:\n"
            "    BinarySearchTree() : root(nullptr) {}\n"
            "    void insert(T val) {\n"
            "        // insertion logic\n"
            "    }\n"
            "};\n"
            "int main() {\n"
            "    BinarySearchTree<int> tree;\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingSemicolon",
        expected_line_number=8
    ),
    ProgramBenchmark(
        id="CPP_L3_02",
        language="cpp",
        complexity_level=3,
        title="Matrix Multiplication Class with Missing Curly Brace",
        description="Multi-method matrix class with inner product calculation missing closing scope brace.",
        code=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "class Matrix2D {\n"
            "    int rows, cols;\n"
            "    std::vector<std::vector<double>> mat;\n"
            "public:\n"
            "    Matrix2D(int r, int c) : rows(r), cols(c), mat(r, std::vector<double>(c, 0.0)) {}\n"
            "    void multiply(const Matrix2D& other) {\n"
            "        for (int i = 0; i < rows; ++i) {\n"
            "            for (int j = 0; j < other.cols; ++j) {\n"
            "                double sum = 0;\n"
            "                for (int k = 0; k < cols; ++k) {\n"
            "                    sum += mat[i][k] * other.mat[k][j];\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "int main() {\n"
            "    Matrix2D a(2, 2);\n"
            "    return 0;\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="UnmatchedBrace",
        expected_line_number=21
    ),

    # =========================================================================
    # JAVA FIXTURES
    # =========================================================================
    # Level 1: Basic Java
    ProgramBenchmark(
        id="JAVA_L1_01",
        language="java",
        complexity_level=1,
        title="Typo in System.out Print Call",
        description="Simple console output with misspelled 'printl'.",
        code=(
            "public class GreetingApp {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.printl(\"Welcome to Error Tutor!\");\n"
            "    }\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="TypoError",
        expected_line_number=3
    ),
    ProgramBenchmark(
        id="JAVA_L1_02",
        language="java",
        complexity_level=1,
        title="Missing Semicolon on Variable Statement",
        description="Local variable declaration missing terminating semicolon.",
        code=(
            "public class Counter {\n"
            "    public static void main(String[] args) {\n"
            "        int totalItems = 50\n"
            "        System.out.println(\"Items: \" + totalItems);\n"
            "    }\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingSemicolon",
        expected_line_number=3
    ),

    # Level 2: Intermediate Java
    ProgramBenchmark(
        id="JAVA_L2_01",
        language="java",
        complexity_level=2,
        title="Missing Scanner Package Import",
        description="Reading user input with Scanner without importing java.util.Scanner.",
        code=(
            "public class UserInput {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner scanner = new Scanner(System.in);\n"
            "        System.out.println(\"Enter name:\");\n"
            "    }\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingImport",
        expected_line_number=1
    ),
    ProgramBenchmark(
        id="JAVA_L2_02",
        language="java",
        complexity_level=2,
        title="Missing Outer Class Wrapper",
        description="Pure procedural Java statements without class declaration.",
        code=(
            "public static void main(String[] args) {\n"
            "    int a = 10;\n"
            "    int b = 20;\n"
            "    System.out.println(a + b);\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingClassDeclaration",
        expected_line_number=1
    ),

    # Level 3: Complex Java
    ProgramBenchmark(
        id="JAVA_L3_01",
        language="java",
        complexity_level=3,
        title="Abstract Employee Hierarchy with Missing Method Return",
        description="Multi-class OOP architecture where concrete subclass misses a return value.",
        code=(
            "abstract class Employee {\n"
            "    protected String name;\n"
            "    protected double baseSalary;\n"
            "    public Employee(String name, double baseSalary) {\n"
            "        this.name = name;\n"
            "        this.baseSalary = baseSalary;\n"
            "    }\n"
            "    public abstract double calculateBonus();\n"
            "}\n"
            "\n"
            "public class Manager extends Employee {\n"
            "    private int teamSize;\n"
            "    public Manager(String name, double baseSalary, int teamSize) {\n"
            "        super(name, baseSalary);\n"
            "        this.teamSize = teamSize;\n"
            "    }\n"
            "    @Override\n"
            "    public double calculateBonus() {\n"
            "        double bonus = this.baseSalary * 0.15 + (this.teamSize * 50);\n"
            "        // Missing return statement!\n"
            "    }\n"
            "}\n"
        ),
        expected_status="ERROR",
        expected_error_type="MissingReturnStatement",
        expected_line_number=17
    ),
    ProgramBenchmark(
        id="JAVA_L3_02",
        language="java",
        complexity_level=3,
        title="Generic Priority Queue Task Scheduler with Unclosed Brace",
        description="Generics task queue with custom comparator class having missing closing brace.",
        code=(
            "import java.util.ArrayList;\n"
            "import java.util.List;\n"
            "\n"
            "public class TaskScheduler<T extends Comparable<T>> {\n"
            "    private List<T> tasks;\n"
            "    public TaskScheduler() {\n"
            "        this.tasks = new ArrayList<>();\n"
            "    }\n"
            "    public void schedule(T task) {\n"
            "        this.tasks.add(task);\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        TaskScheduler<String> s = new TaskScheduler<>();\n"
            "        s.schedule(\"Job 1\");\n"
            "        System.out.println(\"Scheduled successfully\");\n"
            "    }\n"
        ),
        expected_status="ERROR",
        expected_error_type="UnclosedBlock",
        expected_line_number=16
    ),
]


def get_benchmarks_by_language(language: str) -> List[ProgramBenchmark]:
    return [b for b in COMPLEX_EVALUATION_DATASET if b.language.lower() == language.lower()]


def get_benchmarks_by_complexity(level: int) -> List[ProgramBenchmark]:
    return [b for b in COMPLEX_EVALUATION_DATASET if b.complexity_level == level]
