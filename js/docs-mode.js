(function () {
    var STORAGE_KEY = 'kcoreDocsExampleMode';
    var VALID = { cli: true, yaml: true };

    function readMode() {
        try {
            var v = localStorage.getItem(STORAGE_KEY);
            if (v === 'cli' || v === 'yaml') return v;
        } catch (e) {}
        return 'yaml';
    }

    document.documentElement.setAttribute('data-docs-example-mode', readMode());

    function setMode(mode) {
        if (!VALID[mode]) mode = 'yaml';
        document.documentElement.setAttribute('data-docs-example-mode', mode);
        try {
            localStorage.setItem(STORAGE_KEY, mode);
        } catch (e) {}
        document.querySelectorAll('.docs-mode-tab').forEach(function (btn) {
            var val = btn.getAttribute('data-docs-mode-value');
            var on = val === mode;
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
    }

    function wire() {
        setMode(readMode());
        document.querySelectorAll('.docs-mode-tab').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var mode = btn.getAttribute('data-docs-mode-value');
                setMode(mode || 'yaml');
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wire);
    } else {
        wire();
    }
})();
