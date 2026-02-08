# Today's Task

**Note:** Ignore commented blocks (surrounded by <!-- -->).

## Bug reported by user

```bash
vscode ➜ /workspaces/taxos (2026-02-07) $  cd /workspaces/taxos ; /usr/bin/env /usr/local/python/current/bin/python /home/vscode/.vscode-server/extensions/ms-python.debugpy-2025.18.0-linux-x64/bundled/libs/debugpy/adapter/../../debugpy/launcher 38565 -- -m scaf -vvv /workspaces/taxos --call=backend/taxos/index_unallocated_receipts -- 069869b809e270a580006b58d97975f0 
2026-02-08 02:57:09 ℹ️  Calling action 'backend/taxos/index_unallocated_receipts' in domain at: /workspaces/taxos [scaf.cli]
2026-02-08 02:57:09 🐛 Handling command=LoadActionPackage(root=PosixPath('/workspaces/taxos'), action_folder=PosixPath('backend/taxos/index_unallocated_receipts')) [scaf.action_package.load.handler]
2026-02-08 02:57:09 🐛 ROOT_DIR=PosixPath('/workspaces/taxos') [scaf.config]
2026-02-08 02:57:09 ℹ️  Action package loaded from /workspaces/taxos/backend/taxos/index_unallocated_receipts [scaf.action_package.load.handler]
2026-02-08 02:57:09 🐛 Handling command=CallAction(action_package=ActionPackage(root=PosixPath('/workspaces/taxos'), action_folder=PosixPath('/workspaces/taxos/backend/taxos/index_unallocated_receipts'), init_module=<module 'module_6e4d82ff7b024bdbc1e045d8f7210e1ecaefca534cd8064fa4ec5184475d5dee' from '/workspaces/taxos/backend/taxos/index_unallocated_receipts/__init__.py'>, shape_module=<module 'module_745ea986147837db769fc43c6f9b24844f506f5ab30d14bdd2080df552e0719f' from '/workspaces/taxos/backend/taxos/index_unallocated_receipts/command.py'>, logic_module=<module 'module_ad84ac18497bb8e1dc73f125838646fedeb2c1b445f541b6af5ebc409d817ae0' from '/workspaces/taxos/backend/taxos/index_unallocated_receipts/handler.py'>, shape_class=<class 'module_745ea986147837db769fc43c6f9b24844f506f5ab30d14bdd2080df552e0719f.IndexUnallocatedReceipts'>), action_args=['069869b809e270a580006b58d97975f0']) [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 ROOT_DIR=PosixPath('/workspaces/taxos') [scaf.config]
2026-02-08 02:57:09 🐛 Building argparse parser from shape class <class 'module_745ea986147837db769fc43c6f9b24844f506f5ab30d14bdd2080df552e0719f.IndexUnallocatedReceipts'> with description: No comment. [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Processing field tenant of type typing.Union[taxos.tenant.entity.Tenant, taxos.tenant.entity.TenantRef] with default <dataclasses._MISSING_TYPE object at 0x7f71a0495d00> [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Normalizing type typing.Union[taxos.tenant.entity.Tenant, taxos.tenant.entity.TenantRef] for argparse [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 origin=typing.Union [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Normalizing type <class 'taxos.tenant.entity.TenantRef'> for argparse [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Normalized type for field 'tenant': <class 'taxos.tenant.entity.TenantRef'> [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Processing field receipt of type taxos.receipt.entity.ReceiptRef | None with default None [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Normalizing type taxos.receipt.entity.ReceiptRef | None for argparse [scaf.action.call.handler]
2026-02-08 02:57:09 🐛 Normalized type for field 'receipt': taxos.receipt.entity.ReceiptRef | None [scaf.action.call.handler]
2026-02-08 02:57:09 ❌ taxos.receipt.entity.ReceiptRef | None is not callable [scaf.cli]
```

this is their class:

```python
from dataclasses import dataclass
from typing import Union

from taxos.receipt.entity import ReceiptRef
from taxos.tenant.entity import Tenant, TenantRef


@dataclass
class IndexUnallocatedReceipts:
  """Index all unallocated receipts for a tenant, or just the one given."""

  tenant: Union[Tenant, TenantRef]
  receipt: ReceiptRef | None = None

  def execute(self):
    from taxos.index_unallocated_receipts.handler import handle

    return handle(self)

```

expectation: receipt should be optional (can specify with --receipt=receipt_ref123)


## Goals

- [ ] add an example to the `example` domain, if necessary
- [ ] write an integration test that proves the bug exists (name the test file bug/tests/test_<%Y%m%d%H%M>.py as in other bug tests)
- [ ] fix the bug
- [ ] ensure the test passes
- [ ] commit and push
