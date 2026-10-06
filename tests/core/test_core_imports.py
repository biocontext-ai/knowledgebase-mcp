import os
import subprocess
import sys


def test_core_survives_broken_scholarly():
    """A broken scholarly install disables the Google Scholar tools instead of crashing the server (#4)."""
    code = "import sys; sys.modules['scholarly'] = None; import biocontext_kb.core; print('ok')"
    env = {k: v for k, v in os.environ.items() if k != "MCP_ENVIRONMENT"}
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, check=False)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
    assert "Google Scholar tools disabled" in result.stderr
