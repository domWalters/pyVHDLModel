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

Types.
"""
from typing                 import Union, List, Iterator, Iterable, Tuple, Optional as Nullable, Dict, Mapping

from pyTooling.Decorators   import export, readonly
from pyTooling.MetaClasses  import ExtendedType
from pyTooling.Graph        import Vertex

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, MultipleNamedEntityMixin, DocumentedEntityMixin, ExpressionUnion, Range
from pyVHDLModel.Symbol     import Symbol
from pyVHDLModel.Expression import EnumerationLiteral, PhysicalIntegerLiteral


@export
class BaseType(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	A base-class for all type entities: full types, subtypes and anonymous types.
	"""

	_objectVertex: Vertex

	def __init__(self, identifier: str, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initializes underlying ``BaseType``.

		:param identifier: Name of the type.
		:param parent:     Reference to the logical parent in the model hierarchy.
		"""
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._objectVertex = None


@export
class Type(BaseType):
	"""
	A base-class for types that are named by a type declaration.

	Besides real type declarations, this is also the base-class of a generic type interface item, which
	introduces a type name without defining the type itself.
	"""
	pass


@export
class AnonymousType(Type):
	"""
	A base-class for types that have no type definition of their own.

	An incomplete type is the typical case: it names a type whose definition appears later.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type ptr;              -- incomplete, completed further down
	      --   ^^^
	"""
	pass


@export
class FullType(BaseType):
	"""
	A base-class for all full type definitions, as opposed to a :class:`Subtype`.

	This is the distinction the declaration regions index on: a full type goes into ``Types``, a subtype
	into ``Subtypes``.
	"""
	pass


@export
class Subtype(BaseType):
	"""
	A subtype declaration: a type mark, optionally narrowed by a constraint and/or a resolution function.

	.. admonition:: Example

	   .. code-block:: VHDL

	      subtype byte is bit_vector(7 downto 0);
	      --      ^^^^                              <- Identifier
	      --              ^^^^^^^^^^                <- Type (the type mark)
	      --                        ^^^^^^^^^^^^   <- Range (the constraint)
	"""
	_type:               Symbol
	_baseType:           BaseType
	_range:              Range
	_resolutionFunction: 'Function'

	def __init__(self, identifier: str, symbol: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._type = symbol
		self._baseType = None
		self._range = None
		self._resolutionFunction = None

	@readonly
	def Type(self) -> Symbol:
		"""
		Read-only property to access the type (:attr:`_type`).

		:returns: The type.
		"""
		return self._type

	@readonly
	def BaseType(self) -> BaseType:
		"""
		Read-only property to access the base type (:attr:`_baseType`).

		:returns: The base type.
		"""
		return self._baseType

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	@readonly
	def ResolutionFunction(self) -> 'Function':
		"""
		Read-only property to access the resolution function (:attr:`_resolutionFunction`).

		:returns: The resolution function.
		"""
		return self._resolutionFunction

	def __str__(self) -> str:
		return f"subtype {self._identifier} is {self._baseType}"


@export
class ScalarType(FullType):
	"""
	A base-class for all scalar types: enumerated, integer, real and physical types.
	"""


@export
class RangedScalarType(ScalarType):
	"""
	A base-class for all scalar types constrained by a range: integer, real and physical types.

	An enumerated type is scalar but not ranged, which is why it derives from :class:`ScalarType`
	directly.
	"""

	_range: Range

	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		"""
		Initialize a scalar type with a range.

		:param identifier:    The type's identifier.
		:param rng:           The type's range.
		:param documentation: The type's documentation.
		:param parent:        The parent model entity.
		"""
		super().__init__(identifier, documentation, parent)
		self._range = rng

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the type's range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range


@export
class NumericTypeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all numeric types: integer, real and physical types.
	"""

	def __init__(self) -> None:
		pass


@export
class DiscreteTypeMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all discrete types: enumerated and integer types.
	"""

	def __init__(self) -> None:
		pass


@export
class EnumeratedType(ScalarType, DiscreteTypeMixin):
	"""
	An enumerated type definition, listing its literals in declaration order.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type state is (Idle, Running, Done);
	      --             ^^^^^^^^^^^^^^^^^^^   <- Literals
	"""
	_literals: List[EnumerationLiteral]

	def __init__(self, identifier: str, literals: Iterable[EnumerationLiteral], documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._literals = []
		if literals is not None:
			for literal in literals:
				self._literals.append(literal)
				literal.Parent = self

	@readonly
	def Literals(self) -> List[EnumerationLiteral]:
		"""
		Read-only property to access the literals (:attr:`_literals`).

		:returns: List of literals.
		"""
		return self._literals

	def __str__(self) -> str:
		return f"{self._identifier} is ({', '.join(str(l) for l in self._literals)})"


@export
class IntegerType(RangedScalarType, NumericTypeMixin, DiscreteTypeMixin):
	"""
	An integer type definition, constrained by a range.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type nibble is range 0 to 15;
	      --                   ^^^^^^^   <- Range
	"""
	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, rng, documentation, parent)

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range}"


@export
class RealType(RangedScalarType, NumericTypeMixin):
	"""
	A floating-point type definition, constrained by a range.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type fraction is range 0.0 to 1.0;
	      --                     ^^^^^^^^^^   <- Range
	"""
	def __init__(self, identifier: str, rng: Range, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, rng, documentation, parent)

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range}"


@export
class PhysicalType(RangedScalarType, NumericTypeMixin):
	"""
	A physical type definition: a range, a primary unit and any number of secondary units.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type distance is range 0 to 1e9 units
	        um;                                  -- PrimaryUnit
	        mm = 1000 um;                        -- SecondaryUnits
	        m  = 1000 mm;
	      end units;
	"""
	_primaryUnit:    str
	_secondaryUnits: List[Tuple[str, PhysicalIntegerLiteral]]

	def __init__(
		self,
		identifier: str,
		rng: Range,
		primaryUnit: str,
		units: Iterable[Tuple[str, PhysicalIntegerLiteral]],
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifier, rng, documentation, parent)

		self._primaryUnit = primaryUnit

		self._secondaryUnits = []  # TODO: convert to dict
		for unit in units:
			self._secondaryUnits.append(unit)
			unit[1].Parent = self

	@readonly
	def PrimaryUnit(self) -> str:
		"""
		Read-only property to access the primary unit (:attr:`_primaryUnit`).

		:returns: The primary unit.
		"""
		return self._primaryUnit

	@readonly
	def SecondaryUnits(self) -> List[Tuple[str, PhysicalIntegerLiteral]]:
		"""
		Read-only property to access the secondary units (:attr:`_secondaryUnits`).

		:returns: List of secondary units.
		"""
		return self._secondaryUnits

	def __str__(self) -> str:
		return f"{self._identifier} is range {self._range} units {self._primaryUnit}; {'; '.join(su + ' = ' + str(pu) for su, pu in self._secondaryUnits)};"


@export
class CompositeType(FullType):
	"""
	A base-class for all composite types: array and record types.
	"""


@export
class ArrayType(CompositeType):
	"""
	An array type definition: one or more index ranges and an element subtype.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type memory is array (0 to 255) of bit_vector(7 downto 0);
	      --                    ^^^^^^^^                              <- Dimensions
	      --                                 ^^^^^^^^^^^^^^^^^^^^^^   <- ElementType
	"""
	_dimensions:  List[Range]
	_elementType: Symbol

	def __init__(
		self,
		identifier: str,
		indices: Iterable,
		elementSubtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(identifier, documentation, parent)

		self._dimensions = []
		for index in indices:
			self._dimensions.append(index)
			# index.Parent = self  # FIXME: indices are provided as empty list

		self._elementType = elementSubtype
		# elementSubtype.Parent = self   # FIXME: subtype is provided as None

	@readonly
	def Dimensions(self) -> List[Range]:
		"""
		Read-only property to access the dimensions (:attr:`_dimensions`).

		:returns: List of dimensions.
		"""
		return self._dimensions

	@readonly
	def ElementType(self) -> Symbol:
		"""
		Read-only property to access the element type (:attr:`_elementType`).

		:returns: The element type.
		"""
		return self._elementType

	def __str__(self) -> str:
		return f"{self._identifier} is array({'; '.join(str(r) for r in self._dimensions)}) of {self._elementType}"


@export
class RecordTypeElement(ModelEntity, MultipleNamedEntityMixin):
	"""
	One element declaration inside a record type definition.

	A single declaration may name several elements at once, hence ``Identifiers`` rather than one
	identifier.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type frame is record
	        a, b : bit;
	      --^^^^         <- Identifiers
	      --       ^^^   <- Subtype
	      end record;
	"""
	_subtype: Symbol

	def __init__(self, identifiers: Iterable[str], subtype: Symbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)
		MultipleNamedEntityMixin.__init__(self, identifiers)

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Subtype(self) -> Symbol:
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def __str__(self) -> str:
		return f"{', '.join(self._identifiers)} : {self._subtype}"


@export
class RecordType(CompositeType):
	"""
	A record type definition, holding its elements in declaration order.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type frame is record
	        header : bit_vector(7 downto 0);   -- Elements
	        payload : bit_vector(31 downto 0);
	      end record;
	"""
	_elements: List[RecordTypeElement]

	def __init__(self, identifier: str, elements: Nullable[Iterable[RecordTypeElement]] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._elements = []  # TODO: convert to dict
		if elements is not None:
			for element in elements:
				self._elements.append(element)
				element.Parent = self

	@readonly
	def Elements(self) -> List[RecordTypeElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	def __str__(self) -> str:
		return f"{self._identifier} is record {'; '.join(str(re) for re in self._elements)};"


@export
class ProtectedType(FullType):
	"""
	A protected type declaration, exposing only its methods (VHDL-2002).

	The implementation lives in a separate :class:`ProtectedTypeBody`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type counter is protected
	        procedure increment;             -- Methods
	        impure function value return natural;
	      end protected;
	"""
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, methods: Union[List, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._methods = []
		if methods is not None:
			for method in methods:
				self._methods.append(method)
				method.Parent = self

	@readonly
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		"""
		Read-only property to access the methods (:attr:`_methods`).

		:returns: List of methods.
		"""
		return self._methods


@export
class ProtectedTypeBody(FullType):
	"""
	A protected type body, implementing the methods declared by its :class:`ProtectedType`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type counter is protected body
	        variable count : natural := 0;
	        procedure increment is           -- Methods
	        begin
	          count := count + 1;
	        end procedure;
	      end protected body;
	"""
	_methods: List[Union['Procedure', 'Function']]

	def __init__(self, identifier: str, declaredItems: Union[List, Iterator] = None, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._methods = []
		if declaredItems is not None:
			for method in declaredItems:
				self._methods.append(method)
				method.Parent = self

	# FIXME: needs to be declared items or so
	@readonly
	def Methods(self) -> List[Union['Procedure', 'Function']]:
		"""
		Read-only property to access the methods (:attr:`_methods`).

		:returns: List of methods.
		"""
		return self._methods


@export
class AccessType(FullType):
	"""
	An access type definition, pointing at values of its designated subtype.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type ptr is access integer;
	      --                 ^^^^^^^   <- DesignatedSubtype
	"""
	_designatedSubtype: Symbol

	def __init__(self, identifier: str, designatedSubtype: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype.Parent = self

	@readonly
	def DesignatedSubtype(self) -> Symbol:
		"""
		Read-only property to access the designated subtype (:attr:`_designatedSubtype`).

		:returns: The designated subtype.
		"""
		return self._designatedSubtype

	def __str__(self) -> str:
		return f"{self._identifier} is access {self._designatedSubtype}"


@export
class FileType(FullType):
	"""
	A file type definition, holding values of its designated subtype.

	.. admonition:: Example

	   .. code-block:: VHDL

	      type text_file is file of string;
	      --                        ^^^^^^   <- DesignatedSubtype
	"""
	_designatedSubtype: Symbol

	def __init__(self, identifier: str, designatedSubtype: Symbol, documentation: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(identifier, documentation, parent)

		self._designatedSubtype = designatedSubtype
		designatedSubtype.Parent = self

	@readonly
	def DesignatedSubtype(self) -> Symbol:
		"""
		Read-only property to access the designated subtype (:attr:`_designatedSubtype`).

		:returns: The designated subtype.
		"""
		return self._designatedSubtype

	def __str__(self) -> str:
		return f"{self._identifier} is file of {self._designatedSubtype}"
