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
from typing                 import Iterable, Optional as Nullable, List, Iterator, Tuple

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType

from pyVHDLModel.Symbol     import Symbol, SubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Base       import ModelEntity, DocumentedEntityMixin, NamedEntityMixin, OptionallyNamedEntityMixin
from pyVHDLModel.Base       import MultipleNamedEntityMixin, identifiersOf
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

	.. seealso::

	   * :class:`Composite mode view element <pyVHDLModel.Interface.CompositeModeViewElement>`
	   * :class:`Simple mode view element <pyVHDLModel.Interface.SimpleModeViewElement>`
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
		"""
		Read-only property to access the mode (:attr:`_mode`).

		:returns: The mode.
		"""
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
		"""
		Read-only property to access the mode view name (:attr:`_modeViewName`).

		:returns: The mode view name.
		"""
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

	.. seealso::

	   * :class:`Port declared with a mode view <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
	   * :class:`Parameter declared with a mode view <pyVHDLModel.Interface.ParameterViewSignalInterfaceItem>`
	   * :class:`Reference to a mode view <pyVHDLModel.Symbol.ModeViewSymbol>`
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
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	@readonly
	def Elements(self) -> List[ModeViewElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements


@export
class InterfaceItemMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class marking a declaration as an interface item.

	Interface items appear in generic clauses, port clauses and parameter lists.

	.. seealso::

	   * :class:`Generic interface item mixin <pyVHDLModel.Interface.GenericInterfaceItemMixin>`
	   * :class:`Parameter interface item mixin <pyVHDLModel.Interface.ParameterInterfaceItemMixin>`
	   * :class:`Port interface item mixin <pyVHDLModel.Interface.PortInterfaceItemMixin>`
	   * :class:`Port signal interface item <pyVHDLModel.Interface.PortSignalInterfaceItem>`
	"""


@export
class InterfaceItemWithModeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for interface items declared with a mode.

	The mode is available as :data:`Mode`.

	.. seealso::

	   * :class:`Generic constant interface item <pyVHDLModel.Interface.GenericConstantInterfaceItem>`
	   * :class:`Parameter constant interface item <pyVHDLModel.Interface.ParameterConstantInterfaceItem>`
	   * :class:`Parameter simple signal interface item <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
	   * :class:`Parameter variable interface item <pyVHDLModel.Interface.ParameterVariableInterfaceItem>`
	   * :class:`Port interface item mixin <pyVHDLModel.Interface.PortInterfaceItemMixin>`
	   * :class:`Port simple signal interface item <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
	"""

	_mode: Mode

	def __init__(self, mode: Mode) -> None:
		self._mode = mode

	@readonly
	def Mode(self) -> Mode:
		"""
		Read-only property to access the mode (:attr:`_mode`).

		:returns: The mode.
		"""
		return self._mode


@export
class GenericInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""
	A mixin-class for all items in a generic clause.

	.. seealso::

	   * :class:`Generic constant interface item <pyVHDLModel.Interface.GenericConstantInterfaceItem>`
	   * :class:`Generic function interface item <pyVHDLModel.Interface.GenericFunctionInterfaceItem>`
	   * :class:`Generic package interface item <pyVHDLModel.Interface.GenericPackageInterfaceItem>`
	   * :class:`Generic procedure interface item <pyVHDLModel.Interface.GenericProcedureInterfaceItem>`
	   * :class:`Generic subprogram interface item <pyVHDLModel.Interface.GenericSubprogramInterfaceItem>`
	   * :class:`Generic type interface item <pyVHDLModel.Interface.GenericTypeInterfaceItem>`
	"""


@export
class PortInterfaceItemMixin(InterfaceItemMixin, InterfaceItemWithModeMixin, mixin=True):
	"""
	A mixin-class for all items in a port clause.
	"""

	def __init__(self, mode: Mode) -> None:
		super().__init__()
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class ParameterInterfaceItemMixin(InterfaceItemMixin, mixin=True):
	"""
	A mixin-class for all items in a subprogram's parameter list.

	.. seealso::

	   * :class:`Parameter constant interface item <pyVHDLModel.Interface.ParameterConstantInterfaceItem>`
	   * :class:`Parameter file interface item <pyVHDLModel.Interface.ParameterFileInterfaceItem>`
	   * :class:`Parameter signal interface item <pyVHDLModel.Interface.ParameterSignalInterfaceItem>`
	   * :class:`Parameter variable interface item <pyVHDLModel.Interface.ParameterVariableInterfaceItem>`
	"""


@export
class GenericConstantInterfaceItem(Constant, GenericInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a constant in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (W : positive := 8);
	      --       ^                     <- Identifiers
	      --           ^^^^^^^^          <- Subtype
	      --                       ^     <- DefaultExpression
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
		GenericInterfaceItemMixin.__init__(self)
		InterfaceItemWithModeMixin.__init__(self, mode)


@export
class GenericTypeInterfaceItem(Type, GenericInterfaceItemMixin):
	"""
	Represents a type in a generic clause.

	A generic type introduces a type name without defining the type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (type T);
	      --            ^     <- Identifier
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericSubprogramInterfaceItem(GenericInterfaceItemMixin):
	"""
	Represents the base-class of subprograms in a generic clause.
	"""
	pass


@export
class GenericProcedureInterfaceItem(Procedure, GenericInterfaceItemMixin):
	"""
	Represents a procedure in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (procedure log(msg : string));
	      --                 ^^^                   <- Identifier
	      --                     ^^^^^^^^^^^^      <- ParameterItems
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation=documentation, parent=parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class GenericFunctionInterfaceItem(Function, GenericInterfaceItemMixin):
	"""
	Represents a function in a generic clause.

	.. admonition:: Example

	   .. code-block:: VHDL

	      generic (function cmp(a, b : integer) return boolean);
	      --                ^^^                                    <- Identifier
	      --                    ^^^^^^^^^^^^^^                     <- ParameterItems
	      --                                           ^^^^^^^     <- ReturnType
	"""
	def __init__(
		self,
		identifier:    str,
		returnType:    SubtypeSymbol,
		documentation: Nullable[str] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifier, returnType, documentation=documentation, parent=parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class InterfacePackage(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a package as a generic of a design unit.

	An interface package parameterises a design unit with an instantiated package.

	.. seealso::

	   * :class:`Generic package interface item <pyVHDLModel.Interface.GenericPackageInterfaceItem>`
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)


@export
class GenericPackageInterfaceItem(InterfacePackage, GenericInterfaceItemMixin):
	"""
	Represents a package in a generic clause.

	A generic package parameterises a design unit with an instantiated package.
	"""
	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)
		GenericInterfaceItemMixin.__init__(self)


@export
class PortSignalInterfaceItem(Signal, InterfaceItemMixin):
	"""
	Represents the base-class of all signals in a port clause.

	A port is declared either with a simple mode (:class:`PortSimpleSignalInterfaceItem`) or with a
	mode view (:class:`PortViewSignalInterfaceItem`).

	.. seealso::

	   * :class:`Port simple signal interface item <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
	   * :class:`Port view signal interface item <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
	"""


@export
class PortSimpleSignalInterfaceItem(PortSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""
	Represents a port declared with a simple mode.

	The port's mode is available as :data:`Mode`, its subtype as :data:`Subtype`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : in bit);
	    --^                    <- Identifiers
	    --          ^^         <- Mode
	    --             ^^^     <- Subtype

	.. seealso::

	   * :class:`Port declared with a mode view <pyVHDLModel.Interface.PortViewSignalInterfaceItem>`
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
	Represents a port declared with a mode view (VHDL-2019).

	Instead of a mode, the port names a mode view (:data:`ModeViewIndication`) that assigns a mode to
	each element of its record type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      port (p : view MyView);
	    --^                         <- Identifiers
	    --               ^^^^^^     <- ModeViewIndication

	. note::

	  VHDL's grammar treats a mode view indication as occupying the same structural position as an
	  ordinary subtype indication (``mode_indication ::= simple_mode_indication | mode_view_indication``).
	  Accordingly, the mode view reference *is* this object's :attr:`Subtype` (a :class:`Symbol` is a
	  :class:`Symbol`, whether it names a subtype or a mode view) - :attr:`ModeViewIndication` is just a
	  more specific, aliased name for the same value, not a separate field. An object's subtype can never
	  be ``None`` - there is no VHDL syntax that omits it.

	.. seealso::

	   * :class:`Mode view declaration <pyVHDLModel.Interface.ModeViewDeclaration>`
	   * :class:`Port declared with a simple mode <pyVHDLModel.Interface.PortSimpleSignalInterfaceItem>`
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
		"""
		Read-only property to access the mode view indication (:attr:`_subtype`).

		:returns: The mode view indication.
		"""
		return self._subtype


@export
class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a constant parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      function fun(constant c : in integer) return integer;
	      -- ^                                                    <- Identifiers
	      --                        ^^                            <- Mode
	      --                           ^^^^^^^                    <- Subtype
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
class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItemMixin, InterfaceItemWithModeMixin):
	"""
	Represents a variable parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(variable v : out bit);
	      --             ^                        <- Identifiers
	      --                          ^^^         <- Mode
	      --                              ^^^     <- Subtype
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
class ParameterSignalInterfaceItem(Signal, ParameterInterfaceItemMixin):
	"""
	Represents a signal parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : in bit);
	      --             ^                     <- Identifiers
	      --                        ^^         <- Mode
	      --                           ^^^     <- Subtype

	.. seealso::

	   * :class:`Parameter simple signal interface item <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
	   * :class:`Parameter view signal interface item <pyVHDLModel.Interface.ParameterViewSignalInterfaceItem>`
	"""


@export
class ParameterSimpleSignalInterfaceItem(ParameterSignalInterfaceItem, InterfaceItemWithModeMixin):
	"""
	Represents a signal parameter declared with a simple mode.

	The parameter's mode is available as :data:`Mode`, its subtype as :data:`Subtype`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : in bit);
	      --             ^                     <- Identifiers
	      --                        ^^         <- Mode
	      --                           ^^^     <- Subtype
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
	Represents a signal parameter declared with a mode view (VHDL-2019).

	Instead of a mode, the parameter names a mode view (:data:`ModeViewIndication`) that assigns a mode
	to each element of its record type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(signal s : view MyView);
	      --             ^                          <- Identifiers
	      --                             ^^^^^^     <- ModeViewIndication

	. note::

	  See :class:`PortViewSignalInterfaceItem` for why the mode view reference *is* :attr:`Subtype`
	  (aliased as :attr:`ModeViewIndication`), rather than a separate, possibly-``None`` field.

	.. seealso::

	   * :class:`Mode view declaration <pyVHDLModel.Interface.ModeViewDeclaration>`
	   * :class:`Parameter declared with a simple mode <pyVHDLModel.Interface.ParameterSimpleSignalInterfaceItem>`
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
		"""
		Read-only property to access the mode view indication (:attr:`_subtype`).

		:returns: The mode view indication.
		"""
		return self._subtype


@export
class ParameterFileInterfaceItem(File, ParameterInterfaceItemMixin):
	"""
	Represents a file parameter of a subprogram.

	.. admonition:: Example

	   .. code-block:: VHDL

	      procedure proc(file f : text_file);
	      --             ^                      <- Identifiers
	      --                      ^^^^^^^^^     <- Subtype
	"""
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
	"""
	A mixin-class for language constructs with a generic clause.

	.. seealso::

	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Generic group <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Package <pyVHDLModel.DesignUnit.Package>`
	"""
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

	@readonly
	def GenericItems(self) -> List[GenericInterfaceItemMixin]:
		"""
		Read-only property to access the generic items (:attr:`_genericItems`).

		:returns: List of generic items.
		"""
		return self._genericItems

	@readonly
	def GenericCount(self) -> int:
		"""
		Read-only property to return the number of generics in :attr:`_genericItems`.

		:returns: The generic count.
		"""
		return len(self._genericItems)


@export
class WithPortsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a port clause.

	.. seealso::

	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`Port group <pyVHDLModel.Interface.PortGroup>`
	"""
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

	@readonly
	def PortItems(self) -> List[PortInterfaceItemMixin]:
		"""
		Read-only property to access the port items (:attr:`_portItems`).

		:returns: List of port items.
		"""
		return self._portItems

	@readonly
	def PortCount(self) -> int:
		"""
		Read-only property to return the number of ports in :attr:`_portItems`.

		:returns: The port count.
		"""
		return len(self._portItems)


@export
class WithParametersMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for language constructs with a parameter list.

	.. seealso::

	   * :class:`Parameter group <pyVHDLModel.Interface.ParameterGroup>`
	"""
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

	@readonly
	def ParameterItems(self) -> List[ParameterInterfaceItemMixin]:
		"""
		Read-only property to access the parameter items (:attr:`_parameterItems`).

		:returns: List of parameter items.
		"""
		return self._parameterItems

	@readonly
	def ParameterCount(self) -> int:
		"""
		Read-only property to return the number of parameters in :attr:`_parameterItems`.

		:returns: The parameter count.
		"""
		return len(self._parameterItems)


@export
class InterfaceGroup(ModelEntity, OptionallyNamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents a group of interface items sharing one clause.

	The group may be named (:data:`Identifier`), which is optional.

	.. seealso::

	   * :class:`Generic group <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Parameter group <pyVHDLModel.Interface.ParameterGroup>`
	   * :class:`Port group <pyVHDLModel.Interface.PortGroup>`
	"""
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
	"""
	Represents the generic clause of a design unit.

	The generics are available as :data:`GenericItems`.

	.. seealso::

	   * :class:`Port clause <pyVHDLModel.Interface.PortGroup>`
	   * :class:`Parameter list <pyVHDLModel.Interface.ParameterGroup>`
	"""
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
		names = ", ".join(name for item in self._genericItems for name in identifiersOf(item))
		return f"GenericGroup {self._identifier} ({len(self._genericItems)}) - generics: {names})"


@export
class PortGroup(InterfaceGroup, WithPortsMixin):
	"""
	Represents the port clause of a design unit.

	The ports are available as :data:`PortItems`.

	.. seealso::

	   * :class:`Generic clause <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Parameter list <pyVHDLModel.Interface.ParameterGroup>`
	"""
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
		names = ", ".join(name for item in self._portItems for name in identifiersOf(item))
		return f"PortGroup: {self._identifier} ({len(self._portItems)}) - ports: {names})"


@export
class ParameterGroup(InterfaceGroup, WithParametersMixin):
	"""
	Represents the parameter list of a subprogram.

	The parameters are available as :data:`ParameterItems`.

	.. seealso::

	   * :class:`Generic clause <pyVHDLModel.Interface.GenericGroup>`
	   * :class:`Port clause <pyVHDLModel.Interface.PortGroup>`
	"""
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
		names = ", ".join(name for item in self._parameterItems for name in identifiersOf(item))
		return f"ParameterGroup {self._identifier} ({len(self._parameterItems)}) - parameters: {names})"
