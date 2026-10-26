import reflex as rx
from pems.states.asset_state import AssetState
from pems.components.objects import Asset

class StationState(AssetState):
    """State for Tracking Changes to the Stations Structure"""
    parent_asset: Asset = None
    # TODO: implement the rest using AssetState as Template
