from unittest.mock import patch

from click.testing import CliRunner

from cli_anything.k_skill.cli import main


class TestMessaging:
    @patch("cli_anything.k_skill.skills.messaging.run_script")
    def test_kakaotalk_calls_script(self, mock_run):
        mock_run.return_value = {"status": "success", "data": {}}
        r = CliRunner()
        res = r.invoke(main, ["messaging", "kakaotalk-mac", "index", "--query", "회의록", "-j"])
        assert res.exit_code == 0, res.output
        mock_run.assert_called_once()
        # first positional arg to run_script is the script name
        assert mock_run.call_args[0][0] == "kakaotalk_mac.py"
