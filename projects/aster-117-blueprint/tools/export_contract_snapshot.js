'use strict';

const path = require('path');
const { createTavo, makeContext, runFile, runFragment, waitFor, loadBooks } = require('../tests/harness');

async function main() {
  const root = path.resolve(__dirname, '..');
  const books = loadBooks(root);
  const mock = createTavo(books);
  const dom = makeContext(mock.tavo, 390, 844);
  runFragment(dom.context, path.join(root, 'plugin-runtime/ui/shell.html'));
  runFile(dom.context, path.join(root, 'plugin-runtime/entry.js'));
  await waitFor(() => dom.window.Aster && !dom.window.Aster.boot.state().scanning && dom.window.Aster.boot.index().length, 'contract snapshot boot');
  const Aster = dom.window.Aster;
  const audit = Aster.contractAudit.audit();
  const parameters = Aster.params.list().map((row) => ({
    id: row.id, label: row.label, category: row.category || 'general', type: row.type,
    scope: row.scope, default: row.default, developer: !!row.developer
  }));
  const output = {
    runtimeVersion: Aster.version,
    modules: Aster.boot.index().length,
    blueprintModules: Aster.blueprintModules.list().map((row) => ({
      sourceId: row.sourceId, ownerBook: row.ownerBook, sourceOrder: row.sourceOrder,
      source: row.source, coverage: row.coverage, targets: row.targets
    })),
    interfaceContracts: Aster.interfaceContracts.list().map((row) => {
      const status = audit.interfaces.find((item) => item.id === row.id);
      return {
        id: row.id, contractVersion: row.contractVersion, methods: row.methods,
        source: row.source, coverage: row.coverage, targetPath: row.targetPath,
        ready: status && status.ready, missing: status && status.missing || []
      };
    }),
    contractSummary: audit.summary,
    parameters
  };
  process.stdout.write(JSON.stringify(output));
}

main().catch((error) => { console.error(error.stack || error); process.exitCode = 1; });
