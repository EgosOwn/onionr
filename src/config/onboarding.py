"""
    Onionr - Private P2P Communication

    Setup config from onboarding choices
"""
from pathlib import Path

from filepaths import onboarding_mark_file
import onionrtypes
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


def set_config_from_onboarding(config_settings: onionrtypes.OnboardingConfig):
    return

def set_onboarding_finished():
    """Create the onboarding completed setting file"""
    Path(onboarding_mark_file).touch()

def is_onboarding_finished() -> bool:
    return True
