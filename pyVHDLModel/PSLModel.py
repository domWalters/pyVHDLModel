# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |   |  \/  | ___   __| | ___| |                                                    #
#  | '_ \| | | \ \ / /| |_| | | | | |   | |\/| |/ _ \ / _` |/ _ \ |                                                    #
#  | |_) | |_| |\ V / |  _  | |_| | |___| |  | | (_) | (_| |  __/ |                                                    #
#  | .__/ \__, | \_/  |_| |_|____/|_____|_|  |_|\___/ \__,_|\___|_|                                                    #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
# Copyright 2016-2017 Patrick Lehmann - Dresden, Germany                                                               #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
This module contains an abstract document language model for PSL in VHDL.
"""
from pyTooling.Decorators import export

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin
from pyVHDLModel.DesignUnit import PrimaryUnit


@export
class PSLEntity(ModelEntity):
	"""
	Represents the base-class of all PSL entities.

	PSL (Property Specification Language) support is rudimentary: verification units are recognised
	and named, but their contents are not modelled.
	"""
	pass


@export
class PSLPrimaryUnit(PrimaryUnit):
	"""
	Represents the base-class of all PSL primary units.
	"""
	pass


@export
class VerificationUnit(PSLPrimaryUnit):
	"""
	Represents a PSL verification unit (``vunit``).
	"""
	def __init__(self, identifier: str) -> None:
		super().__init__(identifier, parent=None)


@export
class VerificationProperty(PSLPrimaryUnit):
	"""
	Represents a PSL verification property (``vprop``).
	"""
	def __init__(self, identifier: str) -> None:
		super().__init__(identifier, parent=None)


@export
class VerificationMode(PSLPrimaryUnit):
	"""
	Represents a PSL verification mode (``vmode``).
	"""
	def __init__(self, identifier: str) -> None:
		super().__init__(identifier, parent=None)


@export
class DefaultClock(PSLEntity, NamedEntityMixin):
	"""
	Represents a PSL default clock declaration.

	It names the clock expression used by PSL directives that do not state one themselves.
	"""
	def __init__(self, identifier: str) -> None:
		super().__init__()
		NamedEntityMixin.__init__(self, identifier)
