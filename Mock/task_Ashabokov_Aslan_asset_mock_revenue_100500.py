from unittest.mock import Mock
mock_asset_class.calculate_revenue.return_value = 100500.0
mock_asset_class.__repr__ = Mock(return_value="AssetClass")
mock_asset_class.build_from_str.return_value = mock_asset_class