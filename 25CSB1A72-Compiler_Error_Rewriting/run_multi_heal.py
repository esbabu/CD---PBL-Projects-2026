import pathlib, sys, traceback, os
# Ensure src is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from heal_agent import HealingAgent, make_compiler, VERDICT_ALREADY_CLEAN, VERDICT_FIXED_AND_VERIFIED, VERDICT_COMPILES_UNVERIFIED, VERDICT_NOT_FIXABLE

def run_file(path: pathlib.Path):
    source = path.read_text(encoding='utf-8')
    compile_fn = make_compiler(working_dir=path.parent)
    agent = HealingAgent(
        source,
        compile_fn=compile_fn,
        pre_scan=None,
        max_attempts=4,
        classify_fn=None,
    )
    try:
        result = agent.run()
        verdict = getattr(result, 'verdict_label', getattr(result, 'verdict', ''))
        changed = getattr(result, 'changed', False)
        lines_fixed = getattr(result, 'lines_fixed', None)
        print(f"{path.name}: verdict={verdict}, changed={changed}, lines_fixed={lines_fixed}")
    except Exception as e:
        print(f"{path.name}: error {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_dir = pathlib.Path(__file__).parent / 'test_cases' / 'multi_error'
    for fp in sorted(test_dir.iterdir()):
        if fp.is_file() and fp.suffix in {'.cpp', '.py'}:
            run_file(fp)

from heal_agent import HealingAgent, make_compiler, VERDICT_ALREADY_CLEAN, VERDICT_FIXED_AND_VERIFIED, VERDICT_COMPILES_UNVERIFIED, VERDICT_NOT_FIXABLE

def run_file(path: pathlib.Path):
    source = path.read_text(encoding='utf-8')
    compile_fn = make_compiler(working_dir=path.parent)
    agent = HealingAgent(
        source,
        compile_fn=compile_fn,
        pre_scan=None,
        max_attempts=4,
        classify_fn=None,
    )
    try:
        result = agent.run()
        verdict = getattr(result, 'verdict_label', getattr(result, 'verdict', ''))
        changed = getattr(result, 'changed', False)
        lines_fixed = getattr(result, 'lines_fixed', None)
        print(f"{path.name}: verdict={verdict}, changed={changed}, lines_fixed={lines_fixed}")
    except Exception as e:
        print(f"{path.name}: error {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_dir = pathlib.Path(__file__).parent / 'test_cases' / 'multi_error'
    for fp in sorted(test_dir.iterdir()):
        if fp.is_file() and fp.suffix in {'.cpp', '.py'}:
            run_file(fp)
