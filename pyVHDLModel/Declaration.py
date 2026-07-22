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


"""
from enum                   import unique, Enum
from typing                 import List, Iterable, Union, Optional as Nullable

from pyTooling.Decorators   import export, readonly

from pyVHDLModel.Base       import ModelEntity, NamedEntityMixin, DocumentedEntityMixin
from pyVHDLModel.Expression import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Name       import Name
from pyVHDLModel.Symbol     import Symbol, SubtypeSymbol



ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
@unique
class EntityClass(Enum):
	"""An ``EntityClass`` is an enumeration. It represents a VHDL language entity class (``entity``, ``label``, ...)."""

	Entity =        0   #: Entity
	Architecture =  1   #: Architecture
	Configuration = 2   #: Configuration
	Procedure =     3   #: Procedure
	Function =      4   #: Function
	Package =       5   #: Package
	Type =          6   #: Type
	Subtype =       7   #: Subtype
	Constant =      8   #: Constant
	Signal =        9   #: Signal
	Variable =      10  #: Variable
	Component =     11  #: Component
	Label =         12  #: Label
	Literal =       13  #: Literal
	Units =         14  #: Units
	Group =         15  #: Group
	File =          16  #: File
	Property =      17  #: Property
	Sequence =      18  #: Sequence
	View =          19  #: View
	Others =        20  #: Others


@export
class Attribute(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents an attribute declaration.

	.. admonition:: Example

	   .. code-block:: VHDL

	      attribute TotalBits : natural;
	"""

	_subtype: Symbol

	def __init__(
		self,
		identifier: str,
		subtype: Symbol,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Subtype(self) -> None:
		return self._subtype


@export
class AttributeSpecification(ModelEntity, DocumentedEntityMixin):
	"""
	Represents an attribute specification.

	.. admonition:: Example

	   .. code-block:: VHDL

	      attribute TotalBits of BusType : subtype is 32;
	"""

	_identifiers: List[Name]
	_attribute: Name
	_entityClass: EntityClass
	_expression: ExpressionUnion

	def __init__(
		self,
		identifiers: Iterable[Name],
		attribute: Name,
		entityClass: EntityClass,
		expression: ExpressionUnion,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)
		DocumentedEntityMixin.__init__(self, documentation)

		self._identifiers = []  # TODO: convert to dict
		for identifier in identifiers:
			self._identifiers.append(identifier)
			identifier.Parent = self

		self._attribute = attribute
		attribute.Parent = self

		self._entityClass = entityClass

		self._expression = expression
		expression.Parent = self

	@readonly
	def Identifiers(self) -> List[Name]:
		return self._identifiers

	@readonly
	def Attribute(self) -> Name:
		return self._attribute

	@readonly
	def EntityClass(self) -> EntityClass:
		return self._entityClass

	@readonly
	def Expression(self) -> ExpressionUnion:
		return self._expression


# TODO: move somewhere else
@export
class Alias(ModelEntity, NamedEntityMixin, DocumentedEntityMixin):
	"""
	Represents an alias declaration.

	An alias can refer to almost anything nameable (an object, a type, a subprogram, a literal, ...), so
	:attr:`Name` is a plain :class:`~pyVHDLModel.Name.Name` rather than one of the narrower
	``*ReferenceSymbol`` classes (those are for cases where the kind of thing being referenced is known
	up front, e.g. a package or a mode view).

	.. admonition:: Example

	   .. code-block:: VHDL

	      alias a : bit_vector(3 downto 0) is s(3 downto 0);
	      --        ^^^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^^^
	      --        Subtype (optional)         Name

	      alias b is s;
	      --          ^
	      --          Name
	"""

	_name:    Name
	_subtype: Nullable[SubtypeSymbol]

	def __init__(
		self,
		identifier:    str,
		name:          Name,
		subtype:       Nullable[SubtypeSymbol] = None,
		documentation: Nullable[str] =            None,
		parent:        Nullable[ModelEntity] =    None
	) -> None:
		super().__init__(parent)
		NamedEntityMixin.__init__(self, identifier)
		DocumentedEntityMixin.__init__(self, documentation)

		self._name = name
		name.Parent = self

		self._subtype = subtype
		if subtype is not None:
			subtype.Parent = self

	@readonly
	def Name(self) -> Name:
		return self._name

	@readonly
	def Subtype(self) -> Nullable[SubtypeSymbol]:
		return self._subtype
