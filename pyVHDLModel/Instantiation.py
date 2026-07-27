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
from typing import List, Iterable, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel             import VHDLModelException
from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.DesignUnit  import Package, ContextUnion
from pyVHDLModel.Association import GenericAssociationItem
from pyVHDLModel.Subprogram  import Procedure, Function, Subprogram
from pyVHDLModel.Symbol      import PackageReferenceSymbol, SubprogramReferenceSymbol, SubtypeSymbol


@export
class GenericInstantiationMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for instantiations passing generic actuals.
	"""
	def __init__(self) -> None:
		pass


@export
class GenericEntityInstantiationMixin(GenericInstantiationMixin, mixin=True):
	"""
	A mixin-class for instantiations of a design entity.
	"""
	def __init__(self) -> None:
		pass


@export
class SubprogramInstantiationMixin(GenericInstantiationMixin, mixin=True):
	"""
	A mixin-class for instantiations of a generic subprogram.
	"""
	_subprogramReference:     SubprogramReferenceSymbol
	_genericAssociationItems: List[GenericAssociationItem]

	def __init__(
		self,
		subprogramReference: SubprogramReferenceSymbol,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None
	) -> None:
		super().__init__()

		self._subprogramReference = subprogramReference
		subprogramReference.Parent = self

		self._genericAssociationItems = []
		if genericAssociationItems is not None:
			for association in genericAssociationItems:
				self._genericAssociationItems.append(association)
				association.Parent = self

	@readonly
	def SubprogramReference(self) -> SubprogramReferenceSymbol:
		"""
		Read-only property to access the subprogram reference (:attr:`_subprogramReference`).

		:returns: The subprogram reference.
		"""
		return self._subprogramReference

	@readonly
	def GenericAssociationItems(self) -> List[GenericAssociationItem]:
		"""
		Read-only property to access the generic association items (:attr:`_genericAssociationItems`).

		:returns: List of generic association items.
		"""
		return self._genericAssociationItems


@export
class ProcedureInstantiation(Procedure, SubprogramInstantiationMixin):
	"""
	Represents the instantiation of a generic procedure.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure p is new gp generic map (N => 1);
	    --^                                             <- Identifier
	    --                   ^^                         <- GenericProcedure
	"""

	def __init__(
		self,
		identifier: str,
		subprogramReference: SubprogramReferenceSymbol,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		genericItems: Nullable[Iterable] = None,
		parameterItems: Nullable[Iterable] = None,
		declaredItems: Nullable[Iterable] = None,
		statements: Nullable[Iterable] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifier, genericItems, parameterItems, declaredItems, statements, documentation, parent)
		SubprogramInstantiationMixin.__init__(self, subprogramReference, genericAssociationItems)


@export
class FunctionInstantiation(Function, SubprogramInstantiationMixin):
	"""
	Represents the instantiation of a generic function.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function f is new gf generic map (N => 1);
	    --^                                            <- Identifier
	    --                  ^^                         <- GenericFunction
	"""

	def __init__(
		self,
		identifier: str,
		subprogramReference: SubprogramReferenceSymbol,
		isPure: bool = True,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		genericItems: Nullable[Iterable] = None,
		parameterItems: Nullable[Iterable] = None,
		declaredItems: Nullable[Iterable] = None,
		statements: Nullable[Iterable] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		# NOTE: deliberately calls Subprogram.__init__ directly, not super().__init__() (which would
		# resolve to Function.__init__ and require a returnType that can never be known here - see
		# the class docstring above).
		Subprogram.__init__(self, identifier, isPure, genericItems, parameterItems, declaredItems, statements, documentation, parent)
		SubprogramInstantiationMixin.__init__(self, subprogramReference, genericAssociationItems)

		self._returnType = None

	@readonly
	def ReturnType(self) -> Nullable[SubtypeSymbol]:
		"""
		Read-only property to access the return type (:attr:`_returnType`).

		:returns: The return type, or ``None`` if not set.
		"""
		return self._returnType


@export
class PackageInstantiation(Package, GenericInstantiationMixin):  # TODO: maybe a PackageBase class is needed to share members.
	"""
	Represents the instantiation of a generic package.

	.. admonition:: Example

	   .. code-block:: VHDL

	      package p is new gp generic map (N => 1);
	    --^                                           <- Identifier
	    --                 ^^                         <- PackageReference
	"""
	_packageReference:        PackageReferenceSymbol
	_genericAssociationItems: List[GenericAssociationItem]

	def __init__(
		self,
		identifier:              str,
		genericPackage:          PackageReferenceSymbol,
		contextItems:            Nullable[Iterable[ContextUnion]] =           None,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		documentation:           Nullable[str] =                              None,
		parent:                  Nullable[ModelEntity] =                      None
	) -> None:
		super().__init__(identifier, contextItems, documentation=documentation, parent=parent)
		GenericEntityInstantiationMixin.__init__(self)

		self._packageReference = genericPackage
		self._packageReference.Parent = self

		# TODO: extract to mixin
		self._genericAssociationItems = []
		if genericAssociationItems is not None:
			for association in genericAssociationItems:
				self._genericAssociationItems.append(association)
				association.Parent = self

	@readonly
	def PackageReference(self) -> PackageReferenceSymbol:
		"""
		Read-only property to access the package reference (:attr:`_packageReference`).

		:returns: The package reference.
		"""
		return self._packageReference

	@readonly
	def GenericAssociationItems(self) -> List[GenericAssociationItem]:
		"""
		Read-only property to access the generic association items (:attr:`_genericAssociationItems`).

		:returns: List of generic association items.
		"""
		return self._genericAssociationItems

	def Instantiate(self) -> None:
		genericPackage: Package = self._packageReference.Package
		if genericPackage is None:
			raise VHDLModelException(f"PackageInstantiation '{self.Identifier}' isn't linked to the generic package '{self._packageReference.Name}'.")

		# TODO: components might need to be copied and derived
		for componentName, component in genericPackage._components.items():
			self._components[componentName] = component

		# FIXME: handle other package members
