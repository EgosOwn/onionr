"""Onionr - Private P2P Communication.

Setup config from onboarding choices
"""
from pathlib import Path
from typing import Union

from filepaths import onboarding_mark_file
from onionrtypes import JSONSerializable
from onionrtypes import OnboardingConfig
import config
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


def _get_val_or_none(json: dict, key: str) -> Union[None, JSONSerializable]:
    try:
        return json['configInfo'][key]
    except KeyError:
        return None


def set_config_from_onboarding(config_settings: OnboardingConfig):
    get = _get_val_or_none

    config.reload()

    if get(config_settings, 'optimize'):
        config.set('ui.animated_background', False)
        config.set('general.insert_deniable_blocks', False)

    if get(config_settings, 'stateTarget') or not get(config_settings,
                                                      'networkContrib'):
        config.set('general.security_level', 1)

    if get(config_settings, 'localThreat'):
        config.set('general.security_level', 3)
        config.set('transports.lan', False)

    config.set('ui.theme', 'light')
    if get(config_settings, 'useDark'):
        config.set('ui.theme', 'dark')

    disabled = config.get('plugins.disabled', [])

    if not get(config_settings, 'circles') or \
            config.get('general.security_level') > 0:
        disabled.append('flow')

    if not get(config_settings, 'mail'):
        disabled.append('pms')

    config.set('plugins.disabled', disabled)

    config.set('general.store_plaintext_blocks',
               get(config_settings, 'plainContrib'))

    config.set('onboarding.done', True, savefile=True)


def set_onboarding_finished():
    """Create the onboarding completed setting file"""
    Path(onboarding_mark_file).touch()


def is_onboarding_finished() -> bool:
    return True
