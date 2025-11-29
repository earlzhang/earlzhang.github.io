import itertools
import re
import ast

# --- Canonicalization Logic using AST ---

def _get_op_symbol(op_node):
    """Maps an AST operator node to its string symbol."""
    if isinstance(op_node, ast.Add): return '+'
    if isinstance(op_node, ast.Sub): return '-'
    if isinstance(op_node, ast.Mult): return '*'
    if isinstance(op_node, ast.Div): return '/'
    return '?'

_canonical_visitor_memo = {}

def _collect_parts(node, op_type, parts_list):
    """
    For associative operators, recursively traverses and flattens a chain of
    the same operations (e.g., a+b+c) into a single list.
    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, op_type):
        _collect_parts(node.left, op_type, parts_list)
        _collect_parts(node.right, op_type, parts_list)
    else:
        parts_list.append(_canonical_visitor(node))

def _collect_mul_div(node, in_denominator=False):
    """
    收集乘除法链,返回 (numerators, denominators) 元组
    将 a*b/c*d/e 展开为分子分母形式以实现规范化
    """
    if isinstance(node, ast.Constant):
        val = str(node.value)
        if in_denominator:
            return ([], [val])
        else:
            return ([val], [])
    
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mult):
            # 乘法:两边都保持当前的分子/分母状态
            left_num, left_den = _collect_mul_div(node.left, in_denominator)
            right_num, right_den = _collect_mul_div(node.right, in_denominator)
            return (left_num + right_num, left_den + right_den)
        elif isinstance(node.op, ast.Div):
            # 除法:右边的分子分母状态翻转
            left_num, left_den = _collect_mul_div(node.left, in_denominator)
            right_num, right_den = _collect_mul_div(node.right, not in_denominator)
            return (left_num + right_num, left_den + right_den)
        else:
            # 其他运算符,递归处理
            canonical = _canonical_visitor(node)
            if in_denominator:
                return ([], [canonical])
            else:
                return ([canonical], [])
    
    # 其他节点类型
    canonical = _canonical_visitor(node)
    if in_denominator:
        return ([], [canonical])
    else:
        return ([canonical], [])

def _canonical_visitor(node):
    """
    Recursively traverses the AST and builds a canonical string representation.
    """
    if node in _canonical_visitor_memo:
        return _canonical_visitor_memo[node]

    if isinstance(node, ast.Constant):
        return str(node.value)
    
    if isinstance(node, ast.BinOp):
        op_symbol = _get_op_symbol(node.op)
        op_type = type(node.op)

        # 加法:展开并排序
        if op_type == ast.Add:
            parts = []
            _collect_parts(node, op_type, parts)
            sorted_parts = sorted(parts)
            res = f"({'+'.join(sorted_parts)})"
        # 乘法和除法:展开为分子分母形式
        elif op_type in (ast.Mult, ast.Div):
            numerators, denominators = _collect_mul_div(node)
            num_strs = sorted(numerators)
            den_strs = sorted(denominators)
            
            if not den_strs:
                res = f"(*{'*'.join(num_strs)})"
            else:
                res = f"(*{'*'.join(num_strs)}/{'*'.join(den_strs)})"
        # 减法:不可交换,保持原有顺序
        else:
            c_left = _canonical_visitor(node.left)
            c_right = _canonical_visitor(node.right)
            res = f"({c_left}{op_symbol}{c_right})"
        
        _canonical_visitor_memo[node] = res
        return res
    
    # Fallback for other node types if any
    return "<?>"

def get_canonical_form(expression_string):
    """
    Parses an expression string and returns its canonical form.
    """
    try:
        tree = ast.parse(expression_string, mode='eval').body
        _canonical_visitor_memo.clear()
        return _canonical_visitor(tree)
    except (SyntaxError, TypeError):
        return expression_string # Fallback for parsing errors

# --- 24 Game Logic ---

def solve_24(numbers):
    """
    Finds all unique expressions that evaluate to 24 given four numbers.
    """
    unique_solutions = {} # Use a dict to store canonical_form -> original_expression
    ops = ['+', '-', '*', '/']
    
    for p_nums in set(itertools.permutations(numbers)):
        for p_ops in itertools.product(ops, repeat=3):
            n1, n2, n3, n4 = p_nums
            op1, op2, op3 = p_ops

            # The 5 parenthesis structures
            expressions = [
                f"(({n1} {op1} {n2}) {op2} {n3}) {op3} {n4}",
                f"({n1} {op1} ({n2} {op2} {n3})) {op3} {n4}",
                f"{n1} {op1} (({n2} {op2} {n3}) {op3} {n4})",
                f"{n1} {op1} ({n2} {op2} ({n3} {op3} {n4}))",
                f"({n1} {op1} {n2}) {op2} ({n3} {op3} {n4})"
            ]
            
            for expr in expressions:
                try:
                    if abs(eval(expr) - 24) < 1e-9:
                        canonical_form = get_canonical_form(expr)
                        if canonical_form not in unique_solutions:
                            unique_solutions[canonical_form] = expr
                except ZeroDivisionError:
                    continue
                    
    return sorted(list(unique_solutions.values()))

def main():
    """
    Main function to run the 24-point game CLI.
    """
    print("欢迎来到24点游戏！")
    print("请输入4个1-10之间的数字，用空格或逗号分隔。")
    print("输入 'quit' 或 'exit' 退出程序。")
    
    while True:
        line = input("> ")
        if line.strip().lower() in ['exit', 'quit']:
            print("感谢游玩，再见！")
            break
        
        str_nums = re.split(r'[,\s]+', line.strip())
        
        if len(str_nums) != 4:
            print("错误：请输入恰好4个数字。")
            continue
            
        try:
            nums = [int(n) for n in str_nums]
            if not all(1 <= n <= 10 for n in nums):
                 print("错误：所有数字必须在1到10之间。")
                 continue
        except ValueError:
            print("错误：输入无效，请输入数字。")
            continue

        solutions = solve_24(nums)
        
        if solutions:
            print(f"\n成功！这4个数字可以算出24。共有 {len(solutions)} 种不同的算法：")
            for s in solutions:
                print(s)
        else:
            print("\n抱歉，这4个数字无法计算出24。")
        print("-" * 20)

if __name__ == '__main__':
    main()