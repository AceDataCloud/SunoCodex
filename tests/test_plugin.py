import hashlib
import json
import re
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]


class NativePackageTests(unittest.TestCase):
    def test_native_components_have_one_service_identity(self):
        spec = json.loads((ROOT / 'service.json').read_text())
        manifest = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        marketplace = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        self.assertEqual(manifest['name'], spec['slug'])
        self.assertEqual(manifest['interface']['displayName'], spec['service'] + ' by Ace Data Cloud')
        self.assertEqual(manifest['interface']['developerName'], 'Ace Data Cloud')
        self.assertIn(spec['service'].lower(), manifest['keywords'])
        self.assertEqual(len(marketplace['plugins']), 1)
        entry = marketplace['plugins'][0]
        self.assertEqual(entry['name'], spec['slug'])
        self.assertEqual(entry['source'], {'source': 'local', 'path': './'})
        self.assertEqual(entry['policy']['installation'], 'AVAILABLE')
        self.assertNotEqual(entry['policy']['installation'], 'INSTALLED_BY_DEFAULT')
        self.assertTrue((ROOT / 'skills' / spec['slug'] / 'SKILL.md').is_file())
        for field in ['composerIcon', 'logo']:
            self.assertTrue((ROOT / manifest['interface'][field]).is_file())
        self.assertEqual(manifest['interface']['screenshots'], [])
        self.assertLessEqual(len(manifest['interface']['defaultPrompt']), 3)
        self.assertTrue(all(len(p) <= 128 for p in manifest['interface']['defaultPrompt']))

    def test_mcp_secret_and_service_tool_scope(self):
        spec = json.loads((ROOT / 'service.json').read_text())
        servers = json.loads((ROOT / '.mcp.json').read_text())['mcpServers']
        self.assertEqual(list(servers), [spec['slug']])
        server = servers[spec['slug']]
        self.assertEqual(server['url'], f'https://{spec["mcp"]}.mcp.acedata.cloud/mcp')
        self.assertEqual(server['bearer_token_env_var'], 'ACEDATACLOUD_API_TOKEN')
        self.assertNotIn('http_headers', server)
        self.assertNotIn('headers', server)
        self.assertEqual(server['enabled_tools'], spec['tools'])
        self.assertIn(spec['query'], server['enabled_tools'])
        self.assertFalse(any(name in server['enabled_tools'] for name in
                             ['openai_chat_completion', 'openai_create_response', 'openai_text_to_speech']))
        text = (ROOT / 'skills' / spec['slug'] / 'SKILL.md').read_text()
        self.assertIn('submit once', text)
        self.assertIn('same task ID', text)
        self.assertIn('approved', text)
        self.assertIn('Never', text)

    def test_website_ctas_follow_current_acquisition_contract(self):
        contract = json.loads((ROOT / 'attribution-contract.json').read_text())
        texts = [(ROOT / 'README.md').read_text(), (ROOT / 'readme/README_zh_Hans.md').read_text(),
                 json.dumps(json.loads((ROOT / '.codex-plugin/plugin.json').read_text()))]
        count = 0
        for text in texts:
            for url in re.findall(r'https://platform\.acedata\.cloud[^\s)"<>]+', text):
                params = parse_qs(urlparse(url).query)
                self.assertEqual(set(params), set(contract['utm_keys']))
                self.assertIn(params['utm_source'][0], contract['sources'])
                self.assertEqual(params['utm_medium'][0], contract['sources'][params['utm_source'][0]])
                for vals in params.values():
                    self.assertRegex(vals[0], contract['tag_pattern'])
                    self.assertLessEqual(len(vals[0]), contract['max_tag_length'])
                count += 1
        self.assertGreaterEqual(count, 7)

    def test_onboarding_provenance_and_listing_boundary(self):
        for item in json.loads((ROOT / 'assets/sources.json').read_text()):
            asset = ROOT / item['path']
            self.assertTrue(asset.is_file())
            self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(), item['sha256'])
            self.assertTrue(item['source_url'].startswith('https://raw.githubusercontent.com/'))
            self.assertTrue(item['limits'])
        english = (ROOT / 'README.md').read_text()
        for phrase in ['Official listing is not live', 'General application', 'Manage Keys',
                       'Allowed APIs', 'current price', 'same ID', 'not an Ace execution screenshot']:
            self.assertIn(phrase, english)
        self.assertNotIn('Bearer sk-', english)
        self.assertNotIn('platform-v1-', english)


if __name__ == '__main__':
    unittest.main()
