"""Install this native plugin in a temporary Codex Home, without an LLM turn.

--live-info uses an already provided service API key only for the static
information tool declared in service.json. It never submits media. For a service
without a static info tool, this option verifies connection/schema only.
"""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', required=True)
    parser.add_argument('--output')
    parser.add_argument('--live-info', action='store_true')
    args = parser.parse_args()
    spec = json.loads((ROOT / 'service.json').read_text())
    market = 'acedatacloud-' + spec['slug']
    selector = spec['slug'] + '@' + market
    result = {'service': spec['service'], 'version': subprocess.check_output(
        [args.codex, '--version'], text=True).strip(), 'llm_turns': 0,
        'generation_submissions': 0, 'commands': [], 'live_info': None}
    secret = os.environ.get('ACEDATACLOUD_API_TOKEN', '')
    if args.live_info and not secret:
        parser.error('--live-info requires an existing ACEDATACLOUD_API_TOKEN')
    with tempfile.TemporaryDirectory(prefix='ace-codex-native-') as home:
        env = os.environ.copy()
        env['CODEX_HOME'] = home
        Path(home, 'config.toml').write_text(
            'model_provider="verification-only"\nmodel="verification-only"\n'
            '[model_providers.verification-only]\nname="No inference requested"\n'
            'base_url="http://127.0.0.1:1/v1"\n[analytics]\nenabled=false\n')

        def cli(command):
            proc = subprocess.run([args.codex] + command, env=env, cwd='/tmp',
                                  text=True, capture_output=True, timeout=45)
            if proc.returncode:
                raise RuntimeError(proc.stderr.replace(secret, '[REDACTED]') if secret else proc.stderr)
            obj = json.loads(proc.stdout)
            result['commands'].append({'command': command, 'exit': proc.returncode, 'result': obj})
            return obj

        cli(['plugin', 'marketplace', 'add', str(ROOT), '--json'])
        available = cli(['plugin', 'list', '--marketplace', market, '--available', '--json'])
        assert any(p['pluginId'] == selector for p in available['available'])
        cli(['plugin', 'add', selector, '--json'])
        installed = cli(['plugin', 'list', '--marketplace', market, '--json'])
        assert any(p['pluginId'] == selector and p['enabled'] for p in installed['installed'])
        mcp = cli(['mcp', 'list', '--json'])
        assert any(s['name'] == spec['slug'] and s['transport']['url'] ==
                   f'https://{spec["mcp"]}.mcp.acedata.cloud/mcp' for s in mcp)
        if args.live_info:
            proc = subprocess.Popen([args.codex, 'app-server', '--strict-config', '--listen', 'stdio://'],
                                    env=env, cwd='/tmp', text=True, bufsize=1,
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            mailbox = queue.Queue()
            diagnostics = []

            def read_stdout():
                for line in proc.stdout:
                    try:
                        mailbox.put(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            def read_stderr():
                for line in proc.stderr:
                    if len(diagnostics) < 10:
                        diagnostics.append(line.replace(secret, '[REDACTED]').strip())

            threading.Thread(target=read_stdout, daemon=True).start()
            threading.Thread(target=read_stderr, daemon=True).start()
            request_id = 0

            def rpc(method, params):
                nonlocal request_id
                request_id += 1
                wanted = request_id
                proc.stdin.write(json.dumps({'id': wanted, 'method': method, 'params': params}) + '\n')
                proc.stdin.flush()
                end = time.monotonic() + 60
                while time.monotonic() < end:
                    try:
                        msg = mailbox.get(timeout=1)
                    except queue.Empty:
                        if proc.poll() is not None:
                            raise RuntimeError('app-server exited: ' + ' '.join(diagnostics))
                        continue
                    if msg.get('id') == wanted:
                        if 'error' in msg:
                            raise RuntimeError(json.dumps(msg['error']))
                        return msg['result']
                raise TimeoutError(method)

            try:
                rpc('initialize', {'clientInfo': {'name': 'ace_native_plugin_probe', 'version': '1'},
                                   'capabilities': {'experimentalApi': True}})
                proc.stdin.write('{"method":"initialized"}\n')
                proc.stdin.flush()
                thread = rpc('thread/start', {'cwd': '/tmp', 'ephemeral': True,
                                               'approvalPolicy': 'never', 'sandbox': 'read-only'})
                thread_id = thread['thread']['id']
                service = None
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    status = rpc('mcpServerStatus/list', {'threadId': thread_id})
                    service = next((s for s in status['data'] if s.get('pluginId') == selector), None)
                    if service and service.get('runtimeStatus') == 'connected':
                        break
                    if service and service.get('runtimeStatus') in ['failed', 'disabled']:
                        raise AssertionError(service)
                    time.sleep(1)
                assert service and service['runtimeStatus'] == 'connected', service
                names = set(service['tools'])
                assert names == set(spec['tools']), (names, spec['tools'])
                result['native_server'] = service
                if spec['info']:
                    # The server and tool are resolved from this installed plugin; never use a free-form tool name.
                    response = rpc('mcpServer/tool/call', {'threadId': thread_id,
                                   'server': service['name'], 'tool': spec['info'], 'arguments': {}})
                    assert not response.get('isError'), response
                    assert response.get('content') or response.get('structuredContent')
                    result['live_info'] = response
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                result['diagnostics'] = diagnostics
        cli(['plugin', 'remove', selector, '--json'])
        remaining = cli(['plugin', 'list', '--marketplace', market, '--json'])
        assert not remaining['installed']
    result['pass'] = True
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'service': result['service'], 'pass': True, 'version': result['version'],
                      'live_info_called': result['live_info'] is not None,
                      'llm_turns': 0, 'generation_submissions': 0}))


if __name__ == '__main__':
    run()
