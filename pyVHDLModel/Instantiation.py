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
This module contains parts of an abstract document language model for VHDL.

Instantiations of packages, procedures, functions and protected types.
"""
from typing import List, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel             import VHDLModelException
from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.DesignUnit  import Package
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Subprogram  import Procedure, Function, Subprogram
from pyVHDLModel.Symbol      import PackageReferenceSymbol


@export
class GenericInstantiationMixin(metaclass=ExtendedType, mixin=True):
	def __init__(self) -> None:
		pass


@export
class GenericEntityInstantiationMixin(GenericInstantiationMixin, mixin=True):
	def __init__(self) -> None:
		pass


@export
class SubprogramInstantiationMixin(GenericInstantiationMixin, mixin=True):
	_subprogramReference: Subprogram  # FIXME: is this a subprogram symbol?

	def __init__(self) -> None:
		super().__init__()
		self._subprogramReference = None


@export
class ProcedureInstantiation(Procedure, SubprogramInstantiationMixin):
	pass


@export
class FunctionInstantiation(Function, SubprogramInstantiationMixin):
	pass


@export
class PackageInstantiation(Package, GenericInstantiationMixin):  # TODO: maybe a PackageBase class is needed to share members.
	_packageReference: PackageReferenceSymbol
	_genericAssociations: List[GenericAssociationItem]

	def __init__(self, identifier: str, uninstantiatedPackage: PackageReferenceSymbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation=documentation, parent=parent)
		GenericEntityInstantiationMixin.__init__(self)

		self._packageReference = uninstantiatedPackage
		# uninstantiatedPackage._parent = self    # FIXME: uninstantiatedPackage is provided as int

		# TODO: extract to mixin
		self._genericAssociations = []

	@readonly
	def PackageReference(self) -> PackageReferenceSymbol:
		return self._packageReference

	@readonly
	def GenericAssociations(self) -> List[GenericAssociationItem]:
		return self._genericAssociations

	def Instantiate(self):
		genericPackage: Package = self._packageReference.Package
		if genericPackage is None:
			raise VHDLModelException(f"PackageInstantiation '{self.Identifier}' isn't linked to the generic package '{self._packageReference.Name}'.")

		# TODO: components might need to be copied and derived
		for componentName, component in genericPackage._components.items():
			self._components[componentName] = component

		# FIXME: handle other package members
