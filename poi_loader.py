"""
poi_loader.py - POI Loader for ENGI

Loads hand-crafted POI templates from poi_data and stamps them onto a LocalMap.
Supports location-specific overrides for scaling and customization.
"""

import math

from poi_data import TEMPLATES, OVERRIDES
from z_level import ZTile


class POILoader:
    """Load and place POI templates onto local maps.

    Usage::

        loader = POILoader()
        result = loader.place_poi(local_map, "small_house", 10, 10)
        # result contains npc_spawns and item_spawns for the caller to populate
    """

    def __init__(self):
        self._templates = dict(TEMPLATES)
        self._overrides = dict(OVERRIDES)

    def get_template(self, template_name):
        """Return the template dict for *template_name*, or None."""
        return self._templates.get(template_name)

    def list_templates(self):
        """Return a sorted list of all available template names."""
        return sorted(self._templates.keys())

    def get_override(self, location_name):
        """Return the override dict for *location_name*, or None."""
        return self._overrides.get(location_name)

    def place_poi(self, local_map, template_name, x, y, z=0, override_name=None):
        """Stamp a POI template onto *local_map* at world position (x, y, z).

        If *override_name* is given and found in the overrides table, the
        override's scale factor is applied to tile positions.

        Returns a dict with:
            - ``npc_spawns``: list of (world_x, world_y, world_z, npc_type)
            - ``item_spawns``: list of (world_x, world_y, world_z, item_name, chance)
            - ``entrances``: list of (world_x, world_y, world_z)
            - ``template``: the template name used
            - ``override``: the override dict if applied, else None

        Returns None if the template is not found.
        """
        template = self.get_template(template_name)
        if template is None:
            return None

        override = None
        scale = 1.0
        if override_name is not None:
            override = self.get_override(override_name)
            if override is not None:
                scale = override.get("scale", 1.0)

        # Place tiles
        for rel_x, rel_y, rel_z, terrain_type in template["tiles"]:
            wx = x + _scale_coord(rel_x, scale)
            wy = y + _scale_coord(rel_y, scale)
            wz = z + rel_z
            tile = ZTile(terrain=terrain_type)
            local_map.set_tile(wx, wy, wz, tile)

        # Build absolute spawn lists for the caller
        npc_spawns = []
        for rel_x, rel_y, rel_z, npc_type in template["npc_spawns"]:
            wx = x + _scale_coord(rel_x, scale)
            wy = y + _scale_coord(rel_y, scale)
            wz = z + rel_z
            npc_spawns.append((wx, wy, wz, npc_type))

        item_spawns = []
        for rel_x, rel_y, rel_z, item_name, chance in template["item_spawns"]:
            wx = x + _scale_coord(rel_x, scale)
            wy = y + _scale_coord(rel_y, scale)
            wz = z + rel_z
            item_spawns.append((wx, wy, wz, item_name, chance))

        entrances = []
        for rel_x, rel_y, rel_z in template["entrances"]:
            wx = x + _scale_coord(rel_x, scale)
            wy = y + _scale_coord(rel_y, scale)
            wz = z + rel_z
            entrances.append((wx, wy, wz))

        return {
            "npc_spawns": npc_spawns,
            "item_spawns": item_spawns,
            "entrances": entrances,
            "template": template_name,
            "override": override,
        }


def _scale_coord(coord, scale):
    """Scale a relative coordinate by *scale*, rounding to int."""
    if scale == 1.0:
        return coord
    return int(math.floor(coord * scale))
