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

All declarations for literals, aggregates, operators forming an expressions.
"""
from enum                 import Flag
from typing               import Tuple, List, Iterable, Union, ClassVar, Optional as Nullable

from pyTooling.Decorators import export, readonly

from pyVHDLModel.Base     import ModelEntity, Direction, Range
from pyVHDLModel.Symbol   import Symbol, SubtypeSymbol


ExpressionUnion = Union[
	'BaseExpression',
	'QualifiedExpression',
	'FunctionCall',
	'TypeConversion',
	# ConstantOrSymbol,     TODO: ObjectSymbol
	'Literal',
]


@export
class BaseExpression(ModelEntity):
	"""A ``BaseExpression`` is a base-class for all expressions."""


@export
class Literal(BaseExpression):
	"""A ``Literal`` is a base-class for all literals."""


@export
class NullLiteral(Literal):
	def __str__(self) -> str:
		return "null"


@export
class EnumerationLiteral(Literal):
	_value: str

	def __init__(self, value: str, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def __str__(self) -> str:
		return self._value


@export
class NumericLiteral(Literal):
	"""A ``NumericLiteral`` is a base-class for all numeric literals."""


@export
class IntegerLiteral(NumericLiteral):
	_value: int

	def __init__(self, value: int) -> None:
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> int:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class FloatingPointLiteral(NumericLiteral):
	_value: float

	def __init__(self, value: float) -> None:
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> float:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class PhysicalLiteral(NumericLiteral):
	_unitName: str

	def __init__(self, unitName: str) -> None:
		super().__init__()
		self._unitName = unitName

	@readonly
	def UnitName(self) -> str:
		"""
		Read-only property to access the unit name (:attr:`_unitName`).

		:returns: The unit name.
		"""
		return self._unitName

	def __str__(self) -> str:
		return f"{self._value} {self._unitName}"


@export
class PhysicalIntegerLiteral(PhysicalLiteral):
	_value: int

	def __init__(self, value: int, unitName: str) -> None:
		super().__init__(unitName)
		self._value = value

	@readonly
	def Value(self) -> int:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value


@export
class PhysicalFloatingLiteral(PhysicalLiteral):
	_value: float

	def __init__(self, value: float, unitName: str) -> None:
		super().__init__(unitName)
		self._value = value

	@readonly
	def Value(self) -> float:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value


@export
class CharacterLiteral(Literal):
	_value: str

	def __init__(self, value: str) -> None:
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def __str__(self) -> str:
		return str(self._value)


@export
class StringLiteral(Literal):
	_value: str

	def __init__(self, value: str) -> None:
		super().__init__()
		self._value = value

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	def __str__(self) -> str:
		return "\"" + self._value + "\""


@export
class BitStringBase(Flag):
	NoBase = 0
	Binary = 2
	Octal = 8
	Decimal = 10
	Hexadecimal = 16
	Unsigned = 32
	Signed = 64


@export
class BitStringLiteral(Literal):
	# _base:  ClassVar[BitStringBase]
	_value:       str
	_binaryValue: str
	_bits:        int
	_length:      Nullable[int]
	_signed:      Nullable[bool]

	def __init__(self, value: str, length: Nullable[int] = None, signed: Nullable[bool] = None) -> None:
		super().__init__()
		self._value = value
		self._length = length
		self._signed = signed

		self._binaryValue = None
		self._bits = None

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	@readonly
	def BinaryValue(self) -> str:
		"""
		Read-only property to access the binary value (:attr:`_binaryValue`).

		:returns: The binary value.
		"""
		return self._binaryValue

	@readonly
	def Bits(self) -> Nullable[int]:
		"""
		Read-only property to access the bits (:attr:`_bits`).

		:returns: The bits, or ``None`` if not set.
		"""
		return self._bits

	@readonly
	def Length(self) -> Nullable[int]:
		"""
		Read-only property to access the length (:attr:`_length`).

		:returns: The length, or ``None`` if not set.
		"""
		return self._length

	@readonly
	def Signed(self) -> Nullable[bool]:
		"""
		Check if the bit string literal is signed (:attr:`_signed`).

		:returns: ``True``, if the literal is signed; ``None``, if unspecified.
		"""
		return self._signed

	def __str__(self) -> str:
		signed = "" if self._signed is None else "s" if self._signed is True else "u"
		if self._base is BitStringBase.NoBase:
			base = ""
		elif self._base is BitStringBase.Binary:
			base = "b"
		elif self._base is BitStringBase.Octal:
			base = "o"
		elif self._base is BitStringBase.Decimal:
			base = "d"
		elif self._base is BitStringBase.Hexadecimal:
			base = "x"
		length = "" if self._length is None else str(self._length)
		return length + signed + base + "\"" + self._value + "\""


@export
class BinaryBitStringLiteral(BitStringLiteral):
	_base: ClassVar[BitStringBase] = BitStringBase.Binary


@export
class OctalBitStringLiteral(BitStringLiteral):
	_base: ClassVar[BitStringBase] = BitStringBase.Octal


@export
class DecimalBitStringLiteral(BitStringLiteral):
	_base: ClassVar[BitStringBase] = BitStringBase.Decimal


@export
class HexadecimalBitStringLiteral(BitStringLiteral):
	_base: ClassVar[BitStringBase] = BitStringBase.Hexadecimal


@export
class ParenthesisExpression: #(Protocol):
	__slots__ = ()  # FIXME: use ExtendedType?

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to return the operand. A parenthesis expression has none of its own.

		:returns: The operand.
		"""
		return None


@export
class UnaryExpression(BaseExpression):
	"""A ``UnaryExpression`` is a base-class for all unary expressions."""

	_FORMAT:  Tuple[str, str]
	_operand: ExpressionUnion

	def __init__(self, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

	@readonly
	def Operand(self):
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	def __str__(self) -> str:
		return f"{self._FORMAT[0]}{self._operand!s}{self._FORMAT[1]}"


@export
class NegationExpression(UnaryExpression):
	_FORMAT = ("-", "")


@export
class IdentityExpression(UnaryExpression):
	_FORMAT = ("+", "")


@export
class InverseExpression(UnaryExpression):
	_FORMAT = ("not ", "")


@export
class UnaryAndExpression(UnaryExpression):
	_FORMAT = ("and ", "")


@export
class UnaryNandExpression(UnaryExpression):
	_FORMAT = ("nand ", "")


@export
class UnaryOrExpression(UnaryExpression):
	_FORMAT = ("or ", "")


@export
class UnaryNorExpression(UnaryExpression):
	_FORMAT = ("nor ", "")


@export
class UnaryXorExpression(UnaryExpression):
	_FORMAT = ("xor ", "")


@export
class UnaryXnorExpression(UnaryExpression):
	_FORMAT = ("xnor ", "")


@export
class AbsoluteExpression(UnaryExpression):
	_FORMAT = ("abs ", "")


@export
class TypeConversion(UnaryExpression):
	"""``natural(x)`` - a type conversion. Unlike every other :class:`UnaryExpression` subclass, its
	"operator" is the target type name itself, not a fixed string, so it doesn't participate in the
	shared ``_FORMAT``-based :meth:`UnaryExpression.__str__` at all - it carries its own
	:attr:`_targetSubtype` (mirroring :class:`QualifiedExpression`'s ``_subtype``) and overrides
	``__str__`` accordingly."""

	_targetSubtype: SubtypeSymbol

	def __init__(self, targetSubtype: SubtypeSymbol, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(operand, parent)

		self._targetSubtype = targetSubtype
		targetSubtype.Parent = self

	@readonly
	def TargetSubtype(self) -> SubtypeSymbol:
		"""
		Read-only property to access the target subtype (:attr:`_targetSubtype`).

		:returns: The target subtype.
		"""
		return self._targetSubtype

	def __str__(self) -> str:
		return f"{self._targetSubtype!s}({self._operand!s})"


@export
class SubExpression(UnaryExpression, ParenthesisExpression):
	_FORMAT = ("(", ")")


@export
class BinaryExpression(BaseExpression):
	"""A ``BinaryExpression`` is a base-class for all binary expressions."""

	_FORMAT: Tuple[str, str, str]
	_leftOperand:  ExpressionUnion
	_rightOperand: ExpressionUnion

	def __init__(self, leftOperand: ExpressionUnion, rightOperand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._leftOperand = leftOperand
		leftOperand.Parent = self

		self._rightOperand = rightOperand
		rightOperand.Parent = self

	@readonly
	def LeftOperand(self):
		"""
		Read-only property to access the left operand (:attr:`_leftOperand`).

		:returns: The left operand.
		"""
		return self._leftOperand

	@readonly
	def RightOperand(self):
		"""
		Read-only property to access the right operand (:attr:`_rightOperand`).

		:returns: The right operand.
		"""
		return self._rightOperand

	def __str__(self) -> str:
		return "{leftOperator}{leftOperand!s}{middleOperator}{rightOperand!s}{rightOperator}".format(
			leftOperator=self._FORMAT[0],
			leftOperand=self._leftOperand,
			middleOperator=self._FORMAT[1],
			rightOperand=self._rightOperand,
			rightOperator=self._FORMAT[2],
		)


@export
class RangeExpression(BinaryExpression):
	_direction: Direction

	@readonly
	def Direction(self) -> Direction:
		"""
		Read-only property to access the direction (:attr:`_direction`).

		:returns: The direction.
		"""
		return self._direction


@export
class AscendingRangeExpression(RangeExpression):
	_direction = Direction.To
	_FORMAT = ("", " to ", "")


@export
class DescendingRangeExpression(RangeExpression):
	_direction = Direction.DownTo
	_FORMAT = ("", " downto ", "")


@export
class AddingExpression(BinaryExpression):
	"""A ``AddingExpression`` is a base-class for all adding expressions."""


@export
class AdditionExpression(AddingExpression):
	_FORMAT = ("", " + ", "")


@export
class SubtractionExpression(AddingExpression):
	_FORMAT = ("", " - ", "")


@export
class ConcatenationExpression(AddingExpression):
	_FORMAT = ("", " & ", "")


@export
class MultiplyingExpression(BinaryExpression):
	"""A ``MultiplyingExpression`` is a base-class for all multiplying expressions."""


@export
class MultiplyExpression(MultiplyingExpression):
	_FORMAT = ("", " * ", "")


@export
class DivisionExpression(MultiplyingExpression):
	_FORMAT = ("", " / ", "")


@export
class RemainderExpression(MultiplyingExpression):
	_FORMAT = ("", " rem ", "")


@export
class ModuloExpression(MultiplyingExpression):
	_FORMAT = ("", " mod ", "")


@export
class ExponentiationExpression(MultiplyingExpression):
	_FORMAT = ("", "**", "")


@export
class LogicalExpression(BinaryExpression):
	"""A ``LogicalExpression`` is a base-class for all logical expressions."""


@export
class AndExpression(LogicalExpression):
	_FORMAT = ("", " and ", "")


@export
class NandExpression(LogicalExpression):
	_FORMAT = ("", " nand ", "")


@export
class OrExpression(LogicalExpression):
	_FORMAT = ("", " or ", "")


@export
class NorExpression(LogicalExpression):
	_FORMAT = ("", " nor ", "")


@export
class XorExpression(LogicalExpression):
	_FORMAT = ("", " xor ", "")


@export
class XnorExpression(LogicalExpression):
	_FORMAT = ("", " xnor ", "")


@export
class RelationalExpression(BinaryExpression):
	"""A ``RelationalExpression`` is a base-class for all shifting expressions."""


@export
class EqualExpression(RelationalExpression):
	_FORMAT = ("", " = ", "")


@export
class UnequalExpression(RelationalExpression):
	_FORMAT = ("", " /= ", "")


@export
class GreaterThanExpression(RelationalExpression):
	_FORMAT = ("", " > ", "")


@export
class GreaterEqualExpression(RelationalExpression):
	_FORMAT = ("", " >= ", "")


@export
class LessThanExpression(RelationalExpression):
	_FORMAT = ("", " < ", "")


@export
class LessEqualExpression(RelationalExpression):
	_FORMAT = ("", " <= ", "")


@export
class MatchingRelationalExpression(RelationalExpression):
	pass


@export
class MatchingEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?= ", "")


@export
class MatchingUnequalExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?/= ", "")


@export
class MatchingGreaterThanExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?> ", "")


@export
class MatchingGreaterEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?>= ", "")


@export
class MatchingLessThanExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?< ", "")


@export
class MatchingLessEqualExpression(MatchingRelationalExpression):
	_FORMAT = ("", " ?<= ", "")


@export
class ShiftExpression(BinaryExpression):
	"""A ``ShiftExpression`` is a base-class for all shifting expressions."""


@export
class ShiftLogicExpression(ShiftExpression):
	pass


@export
class ShiftArithmeticExpression(ShiftExpression):
	pass


@export
class RotateExpression(ShiftExpression):
	pass


@export
class ShiftRightLogicExpression(ShiftLogicExpression):
	_FORMAT = ("", " srl ", "")


@export
class ShiftLeftLogicExpression(ShiftLogicExpression):
	_FORMAT = ("", " sll ", "")


@export
class ShiftRightArithmeticExpression(ShiftArithmeticExpression):
	_FORMAT = ("", " sra ", "")


@export
class ShiftLeftArithmeticExpression(ShiftArithmeticExpression):
	_FORMAT = ("", " sla ", "")


@export
class RotateRightExpression(RotateExpression):
	_FORMAT = ("", " ror ", "")


@export
class RotateLeftExpression(RotateExpression):
	_FORMAT = ("", " rol ", "")


@export
class QualifiedExpression(BaseExpression, ParenthesisExpression):
	_operand:  ExpressionUnion
	_subtype:  Symbol

	def __init__(self, subtype: Symbol, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Operand(self):
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	@readonly
	def Subtype(self):
		"""
		Read-only property to access the subtype (:attr:`_subtype`).

		:returns: The subtype.
		"""
		return self._subtype

	def __str__(self) -> str:
		return f"{self._subtype}'({self._operand!s})"


@export
class TernaryExpression(BaseExpression):
	"""
	A ``TernaryExpression`` is a base-class for all ternary expressions.

	The three operands are deliberately *not* exposed as public properties here: unlike
	:class:`UnaryExpression`/:class:`BinaryExpression` (where "the operand"/"left operand"/"right
	operand" are already the natural domain names for every consumer), a ternary's three operands
	play a different semantic role depending on the concrete expression - e.g.
	:class:`WhenElseExpression`'s are really "then value"/"condition"/"else value". Each concrete
	subclass is expected to expose its own, appropriately-named properties over the shared
	``_firstOperand``/``_secondOperand``/``_thirdOperand`` fields, rather than duplicating a
	generic and a specific name for the same value.
	"""

	_FORMAT: Tuple[str, str, str, str]  # FIXME: needs ClassVar[...] when pyTooling gets fixed.
	_firstOperand:  ExpressionUnion
	_secondOperand: ExpressionUnion
	_thirdOperand:  ExpressionUnion

	def __init__(
		self,
		firstOperand: ExpressionUnion,
		secondOperand: ExpressionUnion,
		thirdOperand: ExpressionUnion,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		self._firstOperand = firstOperand
		firstOperand.Parent = self

		self._secondOperand = secondOperand
		secondOperand.Parent = self

		self._thirdOperand = thirdOperand
		thirdOperand.Parent = self

	def __str__(self) -> str:
		return "{beforeFirstOperator}{firstOperand!s}{beforeSecondOperator}{secondOperand!s}{beforeThirdOperator}{thirdOperand!s}{lastOperator}".format(
			beforeFirstOperator=self._FORMAT[0],
			firstOperand=self._firstOperand,
			beforeSecondOperator=self._FORMAT[1],
			secondOperand=self._secondOperand,
			beforeThirdOperator=self._FORMAT[2],
			thirdOperand=self._thirdOperand,
			lastOperator=self._FORMAT[3],
		)


@export
class WhenElseExpression(TernaryExpression):
	"""
	``thenValue when condition else elseValue`` (VHDL-2008 conditional expression, usable anywhere an
	expression is expected - distinct from :class:`~pyVHDLModel.Common.ConditionalExpression`, which
	models the cascading when/else list used in a conditional *assignment*).
	"""

	_FORMAT = ("", " when ", " else ", "")

	def __init__(
		self,
		thenValue: ExpressionUnion,
		condition: ExpressionUnion,
		elseValue: ExpressionUnion,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(thenValue, condition, elseValue, parent)

	@readonly
	def ThenValue(self) -> ExpressionUnion:
		"""
		Read-only property to access the then value (:attr:`_firstOperand`).

		:returns: The then value.
		"""
		return self._firstOperand

	@readonly
	def Condition(self) -> ExpressionUnion:
		"""
		Read-only property to access the condition (:attr:`_secondOperand`).

		:returns: The condition.
		"""
		return self._secondOperand

	@readonly
	def ElseValue(self) -> ExpressionUnion:
		"""
		Read-only property to access the else value (:attr:`_thirdOperand`).

		:returns: The else value.
		"""
		return self._thirdOperand


@export
class FunctionCall(BaseExpression):
	pass


@export
class Allocation(BaseExpression):
	pass


@export
class SubtypeAllocation(Allocation):
	_subtype: Symbol

	def __init__(self, subtype: Symbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

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
		return f"new {self._subtype!s}"


@export
class QualifiedExpressionAllocation(Allocation):
	_qualifiedExpression: QualifiedExpression

	def __init__(self, qualifiedExpression: QualifiedExpression, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._qualifiedExpression = qualifiedExpression
		qualifiedExpression.Parent = self

	@readonly
	def QualifiedExpression(self) -> QualifiedExpression:
		"""
		Read-only property to access the qualified expression (:attr:`_qualifiedExpression`).

		:returns: The qualified expression.
		"""
		return self._qualifiedExpression

	def __str__(self) -> str:
		return f"new {self._qualifiedExpression!s}"


@export
class AggregateElement(ModelEntity):
	"""A ``AggregateElement`` is a base-class for all aggregate elements."""

	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self):
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression


@export
class SimpleAggregateElement(AggregateElement):
	def __str__(self) -> str:
		return str(self._expression)


@export
class IndexedAggregateElement(AggregateElement):
	_index: int

	def __init__(self, index: ExpressionUnion, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(expression, parent)

		self._index = index

	@readonly
	def Index(self) -> int:
		"""
		Read-only property to access the index (:attr:`_index`).

		:returns: The index.
		"""
		return self._index

	def __str__(self) -> str:
		return f"{self._index!s} => {self._expression!s}"


@export
class RangedAggregateElement(AggregateElement):
	_range: Range

	def __init__(self, rng: Range, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(expression, parent)

		self._range = rng
		rng.Parent = self

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	def __str__(self) -> str:
		return f"{self._range!s} => {self._expression!s}"


@export
class NamedAggregateElement(AggregateElement):
	_name: Symbol

	def __init__(self, name: Symbol, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(expression, parent)

		self._name = name
		name.Parent = self

	@readonly
	def Name(self) -> Symbol:
		"""
		Read-only property to access the name (:attr:`_name`).

		:returns: The name.
		"""
		return self._name

	def __str__(self) -> str:
		return "{name!s} => {value!s}".format(
			name=self._name,
			value=self._expression,
		)


@export
class OthersAggregateElement(AggregateElement):
	def __str__(self) -> str:
		return "others => {value!s}".format(
			value=self._expression,
		)


@export
class Aggregate(BaseExpression):
	_elements: List[AggregateElement]

	def __init__(self, elements: Iterable[AggregateElement], parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._elements = []
		for element in elements:
			self._elements.append(element)
			element.Parent = self

	@readonly
	def Elements(self) -> List[AggregateElement]:
		"""
		Read-only property to access the elements (:attr:`_elements`).

		:returns: List of elements.
		"""
		return self._elements

	def __str__(self) -> str:
		choices = [str(element) for element in self._elements]
		return "({choices})".format(
			choices=", ".join(choices)
		)
