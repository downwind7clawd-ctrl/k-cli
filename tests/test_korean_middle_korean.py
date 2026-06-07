"""Tests for korean-middle-korean command in document domain."""

from unittest.mock import patch

from click.testing import CliRunner

from cli_anything.k_skill.cli import main


class TestKoreanMiddleKoreanRegistered:
    def test_command_visible(self):
        runner = CliRunner()
        result = runner.invoke(main, ['document', '--help'])
        assert result.exit_code == 0
        assert 'korean-middle-korean' in result.output


class TestKoreanMiddleKoreanValidTypes:
    @patch("cli_anything.k_skill.skills.document.run_script")
    def test_word_type(self, mock_run_script):
        mock_run_script.return_value = {"status": "success", "data": {"forms": []}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['document', 'korean-middle-korean', 'word', '가다', '-j']
        )
        assert result.exit_code == 0
        call_args = mock_run_script.call_args
        assert call_args[0][0] == 'korean_middle_korean_search.js'
        assert 'word' in call_args[0][1]
        assert '가다' in call_args[0][1]

    @patch("cli_anything.k_skill.skills.document.run_script")
    def test_origin_type(self, mock_run_script):
        mock_run_script.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['document', 'korean-middle-korean', 'origin', '나아가다', '-j']
        )
        assert result.exit_code == 0
        call_args = mock_run_script.call_args
        assert 'origin' in call_args[0][1]

    @patch("cli_anything.k_skill.skills.document.run_script")
    def test_limit_clamps_to_max(self, mock_run_script):
        mock_run_script.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['document', 'korean-middle-korean', 'word', '가다',
                   '--limit', '100', '-j']
        )
        assert result.exit_code == 0
        # Find --limit arg
        args = mock_run_script.call_args[0][1]
        idx = args.index('--limit')
        assert args[idx + 1] == '50'

    @patch("cli_anything.k_skill.skills.document.run_script")
    def test_limit_clamps_to_min(self, mock_run_script):
        mock_run_script.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['document', 'korean-middle-korean', 'word', '가다',
                   '--limit', '0', '-j']
        )
        assert result.exit_code == 0
        args = mock_run_script.call_args[0][1]
        idx = args.index('--limit')
        assert args[idx + 1] == '1'


class TestKoreanMiddleKoreanInvalid:
    def test_invalid_search_type_rejected(self):
        runner = CliRunner()
        result = runner.invoke(
            main, ['document', 'korean-middle-korean', 'invalid_type', '가다', '-j']
        )
        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'invalid' in result.output.lower()
