"""
Brawl Stars Stats — библиотека для работы с Brawl Stars API и расчёта PSI.
"""
from .bs_api import BrawlStarsAPI, BrawlStarsAPIError, NotFoundError
from .bs_tag_converter import LongToCodeConverter
from .psi_calculator import calculate_psi

__version__ = "2.0.0"