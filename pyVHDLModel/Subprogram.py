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

Subprograms are procedures, functions and methods.
"""
from typing                 import List, Iterable, Optional as Nullable

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Symbol     import SubtypeSymbol
from pyVHDLModel.Type       import ProtectedType
from pyVHDLModel.Regions    import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin
from pyVHDLModel.Sequential import SequentialStatement


@export
class Subprogram(ModelEntity, NamedEntityMixin, DocumentedEntityMixin, SequentialDeclarationRegionMixin):
	_genericItems:   List['GenericInterfaceItemMixin']
	_parameterItems: List['ParameterInterfaceItemMixin']
	_statements:     List[SequentialStatement]
	_isPure:         bool

	def __init__(
		self,
		identifier:     str,
		isPure:         bool,
		genericItems:   Nullable[Iterable['GenericInterfaceItemMixin']] =   None,
		parameterItems: Nullable[Iterable['ParameterInterfaceItemMixin']] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None
	) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedIdentifier, declaredItems)

		self._genericItems = []  # TODO: convert to dict
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item.Parent = self

		self._parameterItems = []  # TODO: convert to dict
		if parameterItems is not None:
			for item in parameterItems:
				self._parameterItems.append(item)
				item.Parent = self

		self._statements = []  # TODO: use mixin class
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item.Parent = self

		self._isPure = isPure

	@ModelEntity.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ModelEntity.Parent.fset(self, parent)

		# Connect the subprogram's namespace to the enclosing declaration region's namespace, so a
		# declaration inside the subprogram hides a same-named one from the scope around it. A subprogram
		# can also be a protected type's method, and a protected type is no declaration region, hence the
		# check.
		if isinstance(parent, (ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin)):
			self._namespace.ParentNamespace = parent._namespace

	@readonly
	def GenericItems(self) -> List['GenericInterfaceItemMixin']:
		return self._genericItems

	@readonly
	def ParameterItems(self) -> List['ParameterInterfaceItemMixin']:
		return self._parameterItems

	@readonly
	def Statements(self) -> List[SequentialStatement]:
		return self._statements

	@readonly
	def IsPure(self) -> bool:
		return self._isPure


@export
class Procedure(Subprogram):
	def __init__(
		self,
		identifier:     str,
		genericItems:   Nullable[Iterable['GenericInterfaceItemMixin']] =   None,
		parameterItems: Nullable[Iterable['ParameterInterfaceItemMixin']] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None
	) -> None:
		super().__init__(identifier, False, genericItems, parameterItems, declaredItems, statements, documentation, parent)


@export
class Function(Subprogram):
	_returnType: SubtypeSymbol

	def __init__(
		self,
		identifier:     str,
		returnType:     SubtypeSymbol,
		isPure:         bool =                                              True,
		genericItems:   Nullable[Iterable['GenericInterfaceItemMixin']] =   None,
		parameterItems: Nullable[Iterable['ParameterInterfaceItemMixin']] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		parent:         Nullable[ModelEntity] =                             None
	) -> None:
		super().__init__(identifier, isPure, genericItems, parameterItems, declaredItems, statements, documentation, parent)

		self._returnType = returnType
		returnType.Parent = self

	@readonly
	def ReturnType(self) -> SubtypeSymbol:
		return self._returnType


@export
class MethodMixin(metaclass=ExtendedType, mixin=True):
	"""A ``Method`` is a mixin class for all subprograms in a protected type."""

	_protectedType: ProtectedType

	def __init__(self, protectedType: Nullable[ProtectedType] = None) -> None:
		self._protectedType = protectedType
		if protectedType is not None:
			protectedType.Parent = self

	@readonly
	def ProtectedType(self) -> ProtectedType:
		return self._protectedType


@export
class ProcedureMethod(Procedure, MethodMixin):
	def __init__(
		self,
		identifier:     str,
		genericItems:   Nullable[Iterable['GenericInterfaceItemMixin']] =   None,
		parameterItems: Nullable[Iterable['ParameterInterfaceItemMixin']] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		protectedType:  Nullable[ProtectedType] =                           None,
		parent:         Nullable[ModelEntity] =                             None
	) -> None:
		super().__init__(identifier, genericItems, parameterItems, declaredItems, statements, documentation, parent)
		MethodMixin.__init__(self, protectedType)


@export
class FunctionMethod(Function, MethodMixin):
	def __init__(
		self,
		identifier:     str,
		returnType:     SubtypeSymbol,
		isPure:         bool =                                              True,
		genericItems:   Nullable[Iterable['GenericInterfaceItemMixin']] =   None,
		parameterItems: Nullable[Iterable['ParameterInterfaceItemMixin']] = None,
		declaredItems:  Nullable[Iterable] =                                None,
		statements:     Nullable[Iterable[SequentialStatement]] =           None,
		documentation:  Nullable[str] =                                     None,
		protectedType:  Nullable[ProtectedType] =                           None,
		parent:         Nullable[ModelEntity] =                             None
	) -> None:
		super().__init__(identifier, returnType, isPure, genericItems, parameterItems, declaredItems, statements, documentation, parent)
		MethodMixin.__init__(self, protectedType)
