from solcx import compile_standard, install_solc
import os
import sys
import json


def editor(line: str) -> str:
    if line.startswith('import') and '@' not in line:
        line = "import './%s';\n" % os.path.basename(
            line.replace("import ", '').replace("'", '').replace('"', '').replace(";", '').strip()
        )

    return line


def run():
    # Validation
    try:
        contract_name = sys.argv[1]
        contracts_files = config['contracts'][contract_name]
    except (IndexError, KeyError):
        raise KeyError("Contract name is not found!")

    # Initialize
    build_dir = os.path.join('build', contract_name)
    os.makedirs(build_dir, exist_ok=True)
    sources = {}

    # Build sol files
    for name, path in contracts_files.items():
        sources.update({name: {'content': ''}})
        with open(os.path.abspath(path), 'r') as reader:
            with open(os.path.join(build_dir, name), 'w') as writer:
                for line in reader.readlines():
                    line = editor(line)
                    writer.write(line)
                    sources[name]['content'] += line

    # Compile all contracts to "compiled.json" file
    with open(os.path.join(build_dir, 'compiled.json'), 'w') as file:
        compiled_sol = compile_standard({
            'language': 'Solidity',
            'sources': sources,
            'settings': {
                'outputSelection': {'*': {'*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']}}
            }},
            solc_version=config['compilerVersion']
        )
        json.dump(compiled_sol, file)


if __name__ == '__main__':
    config = json.load(open('config.json'))
    install_solc(version=config['compilerVersion'])
    run()
