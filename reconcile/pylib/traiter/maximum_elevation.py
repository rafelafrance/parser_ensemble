from typing import Any, ClassVar

from reconcile.pylib import util
from reconcile.pylib.base import Base


class MaximumElevationInMeters(Base):
    label: ClassVar[str] = "dwc:maximumElevationInMeters"
    aliases: ClassVar[list[str]] = Base.get_aliases(
        label,
        """
        dwc:maxElevationInMeters dwc:maxElevationInFeet dwc:maximumElevationInFeet""",
    )

    @classmethod
    def reconcile(
        cls, traiter: dict[str, Any], other: dict[str, Any], text: str
    ) -> dict[str, Any]:
        o_val = cls.search(other, cls.aliases)

        # Make sure what OpenAI returned is a string
        if o_val and not isinstance(o_val, str | float | int):
            msg = f"BAD FORMAT in OpenAI {cls.label} {o_val}"
            raise ValueError(msg)

        o_val = util.to_positive_float(o_val) if o_val is not None else o_val
        t_val = traiter.get(cls.label)

        # No match
        if not t_val and not o_val:
            return {}

        # Use the traiter version
        if t_val and not o_val:
            return {cls.label: t_val}

        # A simple match
        if (
            isinstance(o_val, float)
            and isinstance(t_val, float)
            and round(o_val) == round(t_val)
        ):
            return {cls.label: o_val}

        # Try matching on feet
        if o_val and t_val:
            factor = cls.factors_m["ft"]
            ft_to_m = round(o_val * factor, 3)
            if ft_to_m == t_val:
                return {cls.label: ft_to_m}

            msg = f"MISMATCH {cls.label}: {o_val} != {t_val}"
            raise ValueError(msg)

        if o_val and not t_val:
            msg = f"NO TRAITER MATCH: {cls.label} {o_val}"
            raise ValueError(msg)

        msg = f"UNKNOWN error in {cls.label}"
        raise ValueError(msg)
