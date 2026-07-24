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

Interface items are used in generic, port and parameter declarations.
"""
from typing                 import Iterable, Optional as Nullable, List, Iterator

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Symbol     import Symbol, SubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Base       import ModelEntity, DocumentedEntityMixin, NamedEntityMixin, OptionallyNamedEntityMixin
from pyVHDLModel.Base       import MultipleNamedEntityMixin
from pyVHDLModel.Base       import ExpressionUnion, Mode
from pyVHDLModel.Object     import Constant, Signal, Variable, File
from pyVHDLModel.Subprogram import Procedure, Function
from pyVHDLModel.Type       import Type


@export
class ModeViewElement(ModelEntity, MultipleNamedEntityMixin):
	"""
	Base-class for one element definition inside a mode view declaration (VHDL-2019). An element may name
	several fields sharing the same specification (e.g. ``a, b : out;``), hence
	:class:`~pyVHDLModel.Base.MultipleNamedEntityMixin` is inherited.
	"""

	def __init__(self, identifiers: Iterable[str], parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)


@export
class SimpleModeViewElement(ModeViewElement):
	"""
	A mode view element with a plain (simple) mode.

	.. admonition:: Example

	   .. code-block:: VHDL

	      view MyView of RecordType is
	        a, b : out;
	        --     ^^^
	      end view;
	"""

	_mode: Mode

	def __init__(self, identifiers: Iterable[str], mode: Mode, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifiers, parent)
		self._mode = mode

	@readonly
	def Mode(self) -> Mode:
		return self._mode


@export
class CompositeModeViewElement(ModeViewElement):
	"""
	A mode view element that refers to another (named) mode view for an array or record sub-element.
	.. admonition:: Example

	   .. code-block:: VHDL

	      view OuterView of OuterRecord is
	        b : view InnerView;
	        --       ^^^^^^^^^
	      end view;
	"""

	_modeViewName: ModeViewSymbol

	def __init__(self, identifiers: Iterable[str], modeViewName: ModeViewSymbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifiers, parent)

		self._modeViewName = modeViewName
		modeViewName.Parent = self

	@readonly
	def ModeViewName(self) -> ModeViewSymbol:
		return self._modeViewName


@export
class ModeViewDeclaration(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a mode view declaration (VHDL-2019).

	.. admonition:: Example

	   .. code-block:: VHDL

	      view MyView of RecordType is
	        a : out;
	        b : in;
	      end view;
	"""

	_subtype:  SubtypeSymbol
	_elements: List[ModeViewElement]

	def __init__(
		self,
		identifier:    str,
		subtype:       SubtypeSymbol,
		elements:      Nullable[Iterable[ModeViewElement]] = None,
		documentation: Nullable[str] =                        None,
		parent:        Nullable[ModelEntity] =                None
	) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

		self._elements = []
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element.Parent = self

	@readonly
	def Subtype(self) -> SubtypeSymbol:
		return self._subtype

	@readonly
	def Elements(self) -> List[ModeViewElement]:
		return self._elements


@export
class InterfaceItemMixin(DocumentedEntityMixin, mixin=True):
	"""An ``InterfaceItem`` is a base-class for all mixin-classes for all interface items."""

	def __init__(self, documentation: Nullable[str] = None) -> None:
		super().__init__(documentation)


@export
class InterfaceItemWithModeMixin(metaclass=ExtendedType, mixin=True):
	"""An ``InterfaceItemWithMode`` is a mixin-class to provide a ``Mode`` to interface items."""

	_mode: Mode

	def __init__(self, mode: Mode) -> None:
		self._mode = mode

	@readonly
	def Mode(self) -> Mode:
		return self._mode


@export
class GenericInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""A ``GenericInterfaceItem`` is a mixin class for all generic interface items."""


@export
class PortInterfaceItemMixin(InterfaceItemMixin, InterfaceItemWithModeMixin, mixin=True):
	"""A ``PortInterfaceItem`` is a mixin class for all port interface items."""

	def __init__(self, mode: Mode) -> None:
		super().__init__()
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""A ``ParameterInterfaceItem`` is a mixin class for all parameter interface items."""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericSubprogramInterfaceItem(GenericInterfaceItemMixin):
	pass


@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class InterfacePackage(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class GenericPackageInterfaceItem(InterfacePackage, GenericInterfaceItemMixin):
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class PortSignalInterfaceItem(Signal, InterfaceItemMixin):
	"""
	Abstract base-class for port signal interface items - either declared with a simple mode
	(:class:`PortSimpleSignalInterfaceItem`) or with a mode view (:class:`PortViewSignalInterfaceItem`,
	VHDL-2019).
	"""


@export
class PortSimpleSignalInterfaceItem(PortSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : in bit);
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class PortViewSignalInterfaceItem(PortSignalInterfaceItem):
	"""

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : view MyView);

	.. note::

	   VHDL's grammar treats a mode view indication as occupying the same structural position as an
	   ordinary subtype indication (``mode_indication ::= simple_mode_indication | mode_view_indication``).
	   Accordingly, the mode view reference *is* this object's :attr:`Subtype` (a :class:`Symbol` is a
	   :class:`Symbol`, whether it names a subtype or a mode view) - :attr:`ModeViewIndication` is just a
	   more specific, aliased name for the same value, not a separate field. An object's subtype can never
	   be ``None`` - there is no VHDL syntax that omits it.
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		modeViewIndication: ModeViewSymbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, modeViewIndication, None, documentation, parent)

	@readonly
	def ModeViewIndication(self) -> ModeViewSymbol:
		return self._subtype


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItemMixin):
	"""
	Abstract base-class for subprogram signal parameters - either declared with a simple mode
	(:class:`ParameterSimpleSignalInterfaceItem`) or with a mode view
	(:class:`ParameterViewSignalInterfaceItem`, VHDL-2019).
	"""


@export
class ParameterSimpleSignalInterfaceItem(ParameterSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : in bit);
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		mode: Mode,
		subtype: Symbol,
		defaultExpression: Nullable[ExpressionUnion] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, defaultExpression, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterViewSignalInterfaceItem(ParameterSignalInterfaceItem):
	"""

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : view MyView);

	.. note::

	   See :class:`PortViewSignalInterfaceItem` for why the mode view reference *is* :attr:`Subtype`
	   (aliased as :attr:`ModeViewIndication`), rather than a separate, possibly-``None`` field.
	"""

	def __init__(
		self,
		identifiers: Iterable[str],
		modeViewIndication: ModeViewSymbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, modeViewIndication, None, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)

	@readonly
	def ModeViewIndication(self) -> ModeViewSymbol:
		return self._subtype


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItemMixin):
	def __init__(
		self,
		identifiers: Iterable[str],
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifiers, subtype, documentation, parent)
		ParameterInterfaceItemMixin.__init__(self)


@export
class WithGenericsMixin(metaclass=ExtendedType, mixin=True):
	_genericItems: List[GenericInterfaceItemMixin]

	def __init__(
		self,
		genericItems: Nullable[Iterable[GenericInterfaceItemMixin]] = None,
 	) -> None:
		self._genericItems = []
		if genericItems is not None:
			for item in genericItems:
				self._genericItems.append(item)
				item.Parent = self

	@property
	def GenericItems(self) -> List[GenericInterfaceItemMixin]:
		return self._genericItems

	@property
	def GenericCount(self) -> int:
		return len(self._genericItems)


@export
class WithPortsMixin(metaclass=ExtendedType, mixin=True):
	_portItems: List[PortInterfaceItemMixin]

	def __init__(
		self,
		portItems: Nullable[Iterable[PortInterfaceItemMixin]] = None,
	) -> None:
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item.Parent = self

	@property
	def PortItems(self) -> List[PortInterfaceItemMixin]:
		return self._portItems

	@property
	def PortCount(self) -> int:
		return len(self._portItems)


@export
class WithParametersMixin(metaclass=ExtendedType, mixin=True):
	_parameterItems: List[ParameterInterfaceItemMixin]

	def __init__(
		self,
		parameterItems: Nullable[Iterable[ParameterInterfaceItemMixin]] = None,
	) -> None:
		self._parameterItems = []
		if parameterItems is not None:
			for item in parameterItems:
				self._parameterItems.append(item)
				item.Parent = self

	@property
	def ParameterItems(self) -> List[ParameterInterfaceItemMixin]:
		return self._parameterItems

	@property
	def ParameterCount(self) -> int:
		return len(self._parameterItems)


@export
class InterfaceGroup(ModelEntity, OptionallyNamedEntityMixin, DocumentedEntityMixin):
	def __init__(
		self,
		name:   Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		"""Initialize a PortGroup with a list of ports and optional name."""
		super().__init__(parent)
		OptionallyNamedEntityMixin.__init__(self, name)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class GenericGroup(InterfaceGroup, WithGenericsMixin):
	def __init__(
		self,
		genericItems:  Iterable[GenericInterfaceItemMixin],
		name:          Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(name, documentation, parent)
		WithGenericsMixin.__init__(self, genericItems)

	def __len__(self) -> int:
		return len(self._genericItems)

	def __iter__(self) -> Iterator[GenericInterfaceItemMixin]:
		return iter(self._genericItems)

	def __str__(self) -> str:
		return f"GenericGroup {self._identifier} ({len(self._genericItems)}) - generics: {', '.join(p._identifier for p in self._genericItems)})"


@export
class PortGroup(InterfaceGroup, WithPortsMixin):
	def __init__(
		self,
		portItems:     Iterable[PortInterfaceItemMixin],
		name:          Nullable[str] = None,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(name, documentation, parent)
		WithPortsMixin.__init__(self, portItems)

	def __len__(self) -> int:
		return len(self._portItems)

	def __iter__(self) -> Iterator[PortInterfaceItemMixin]:
		return iter(self._portItems)

	def __str__(self) -> str:
		return f"PortGroup: {self._identifier} ({len(self._portItems)}) - ports: {', '.join(p._identifier for p in self._portItems)})"


@export
class ParameterGroup(InterfaceGroup, WithParametersMixin):
	def __init__(
		self,
		parameterItems: Iterable[ParameterInterfaceItemMixin],
		name:           Nullable[str] = None,
		documentation:  Nullable[str] = None,
		parent:         Nullable[ModelEntity] = None
	) -> None:
		super().__init__(name, documentation, parent)
		WithParametersMixin.__init__(self, parameterItems)

	def __len__(self) -> int:
		return len(self._parameterItems)

	def __iter__(self) -> Iterator[ParameterInterfaceItemMixin]:
		return iter(self._parameterItems)

	def __str__(self) -> str:
		return f"ParameterGroup {self._identifier} ({len(self._parameterItems)}) - parameters: {', '.join(p._identifier for p in self._parameterItems)})"
