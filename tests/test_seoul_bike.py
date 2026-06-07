"""Tests for seoul-bike commands in transit domain."""

import json
from unittest.mock import patch

from click.testing import CliRunner

from cli_anything.k_skill.cli import main


class TestSeoulBikeGroupRegistered:
    def test_seoul_bike_group_visible(self):
        runner = CliRunner()
        result = runner.invoke(main, ['transit', '--help'])
        assert result.exit_code == 0
        assert 'seoul-bike' in result.output

    def test_seoul_bike_subcommands_visible(self):
        runner = CliRunner()
        result = runner.invoke(main, ['transit', 'seoul-bike', '--help'])
        assert result.exit_code == 0
        assert 'nearby' in result.output
        assert 'info' in result.output
        assert 'availability' in result.output


class TestSeoulBikeNearby:
    @patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
    def test_nearby_calls_proxy(self, mock_proxy_get):
        mock_proxy_get.return_value = {"status": "success", "data": {"stations": []}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['transit', 'seoul-bike', 'nearby',
                   '--lat', '37.5665', '--lon', '126.9780', '-j']
        )
        assert result.exit_code == 0
        call_args = mock_proxy_get.call_args
        assert call_args[0][0] == "seoul-bike"
        assert call_args[0][1] == "/v1/seoul-bike/nearby"
        assert call_args[0][2]["lat"] == 37.5665
        assert call_args[0][2]["lon"] == 126.9780

    @patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
    def test_nearby_radius_clamps_to_min(self, mock_proxy_get):
        """radius=10 is below min(50), should be clamped to 50."""
        mock_proxy_get.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['transit', 'seoul-bike', 'nearby',
                   '--lat', '37.5665', '--lon', '126.9780',
                   '--radius', '10', '-j']
        )
        assert result.exit_code == 0
        assert mock_proxy_get.call_args[0][2]["radius"] == 50

    @patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
    def test_nearby_radius_clamps_to_max(self, mock_proxy_get):
        """radius=5000 is above max(2000), should be clamped to 2000."""
        mock_proxy_get.return_value = {"status": "success", "data": {}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['transit', 'seoul-bike', 'nearby',
                   '--lat', '37.5665', '--lon', '126.9780',
                   '--radius', '5000', '-j']
        )
        assert result.exit_code == 0
        assert mock_proxy_get.call_args[0][2]["radius"] == 2000


class TestSeoulBikeInfo:
    @patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
    def test_info_calls_proxy(self, mock_proxy_get):
        mock_proxy_get.return_value = {"status": "success", "data": {"name": "강남역"}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['transit', 'seoul-bike', 'info',
                   '--station-id', 'ST-1001', '-j']
        )
        assert result.exit_code == 0
        call_args = mock_proxy_get.call_args
        assert call_args[0][0] == "seoul-bike"
        assert call_args[0][1] == "/v1/seoul-bike/info"
        assert call_args[0][2]["stationId"] == "ST-1001"


class TestSeoulBikeAvailability:
    @patch("cli_anything.k_skill.skills.transit.safe_proxy_get")
    def test_availability_calls_proxy(self, mock_proxy_get):
        mock_proxy_get.return_value = {"status": "success", "data": {"available": 12}}
        runner = CliRunner()
        result = runner.invoke(
            main, ['transit', 'seoul-bike', 'availability',
                   '--lat', '37.5665', '--lon', '126.9780', '-j']
        )
        assert result.exit_code == 0
        call_args = mock_proxy_get.call_args
        assert call_args[0][0] == "seoul-bike"
        assert call_args[0][1] == "/v1/seoul-bike/availability"
        assert call_args[0][2]["lat"] == 37.5665
        assert call_args[0][2]["lon"] == 126.9780
