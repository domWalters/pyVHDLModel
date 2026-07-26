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
	"""
	Represents the base-class of all expressions.
	"""


@export
class Literal(BaseExpression):
	"""
	Represents the base-class of all literals.

	A literal is an expression denoting a value written directly in the source.
	"""


@export
class NullLiteral(Literal):
	"""
	Represents a ``null`` literal.

	A null literal denotes the null value of an access type.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := null;
	      --   ^^^^    <- the literal
	"""
	def __str__(self) -> str:
		return "null"


@export
class EnumerationLiteral(Literal):
	"""
	Represents an enumeration literal.

	The literal's name is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      st <= Idle;
	      --    ^^^^    <- Value
	"""
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
	"""
	Represents the base-class of all numeric literals.

	Integer, floating-point and physical literals are numeric.
	"""


@export
class IntegerLiteral(NumericLiteral):
	"""
	Represents an integer literal.

	The literal's value is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a + 42;
	      --         ^^    <- Value
	"""
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
	"""
	Represents a floating-point literal.

	The literal's value is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      r <= 3.14;
	      --   ^^^^    <- Value
	"""
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
	"""
	Represents the base-class of all physical literals.

	A physical literal combines a numeric value with a unit name (:data:`UnitName`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 10 ns;
	      --   ^^       <- the value
	      --      ^^    <- UnitName
	"""
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
	"""
	Represents a physical literal with an integer value.

	Value (:data:`Value`) and unit name (:data:`UnitName`) are available separately.

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 10 ns;
	      --   ^^       <- Value
	      --      ^^    <- UnitName
	"""
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
	"""
	Represents a physical literal with a floating-point value.

	Value (:data:`Value`) and unit name (:data:`UnitName`) are available separately.

	.. admonition:: Example

	   .. code-block:: VHDL

	      t <= 1.5 ns;
	      --   ^^^       <- Value
	      --       ^^    <- UnitName
	"""
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
	"""
	Represents a character literal.

	The literal's character is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      ch <= 'a';
	      --    ^^^    <- Value
	"""
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
	"""
	Represents a string literal.

	The literal's text is available as :data:`Value`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      txt <= "text";
	      --     ^^^^^^    <- Value
	"""
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
	"""
	Represents the base of a bit string literal: binary, octal, decimal or hexadecimal.
	"""
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
	"""
	Represents the base-class of all bit string literals.

	Besides the literal as written (:data:`Value`), the bits are available in binary form
	(:data:`BinaryValue`, :data:`Bits`), together with the literal's length (:data:`Length`) and
	whether it is signed (:data:`Signed`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := b"10100000";
	      --      ^^^^^^^^^^^    <- Value
	"""
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
	"""
	Represents a bit string literal written in base 2.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := b"10100000";
	      --      ^^^^^^^^^^^    <- Value
	"""
	_base: ClassVar[BitStringBase] = BitStringBase.Binary


@export
class OctalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 8.

	Each digit contributes three bits.

	.. admonition:: Example

	   .. code-block:: VHDL

	      nine := o"240";
	      --      ^^^^^^    <- Value
	"""
	_base: ClassVar[BitStringBase] = BitStringBase.Octal


@export
class DecimalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 10.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := d"160";
	      --      ^^^^^^    <- Value
	"""
	_base: ClassVar[BitStringBase] = BitStringBase.Decimal


@export
class HexadecimalBitStringLiteral(BitStringLiteral):
	"""
	Represents a bit string literal written in base 16.

	Each digit contributes four bits.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := x"A0";
	      --      ^^^^^    <- Value
	"""
	_base: ClassVar[BitStringBase] = BitStringBase.Hexadecimal


@export
class ParenthesisExpression: #(Protocol):
	"""
	Represents the base-class of expressions wrapped in parentheses.

	The operand is available as :data:`Operand`.
	"""
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
	"""
	Represents the base-class of all unary expressions.

	The operand is available as :data:`Operand`.
	"""

	_FORMAT:  Tuple[str, str]
	_operand: ExpressionUnion

	def __init__(self, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	def __str__(self) -> str:
		return f"{self._FORMAT[0]}{self._operand!s}{self._FORMAT[1]}"


@export
class NegationExpression(UnaryExpression):
	"""
	Represents a negation (unary minus) expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := -a;
	      --     ^^    <- the expression
	      --      ^    <- Operand
	"""
	_FORMAT = ("-", "")


@export
class IdentityExpression(UnaryExpression):
	"""
	Represents a identity (unary plus) expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := +a;
	      --     ^^    <- the expression
	      --      ^    <- Operand
	"""
	_FORMAT = ("+", "")


@export
class InverseExpression(UnaryExpression):
	"""
	Represents a logical inversion expression (``not``).

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := not f;
	      --      ^^^^^    <- the expression
	      --          ^    <- Operand
	"""
	_FORMAT = ("not ", "")


@export
class UnaryAndExpression(UnaryExpression):
	"""
	Represents a ``and`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := and v;
	      --      ^^^^^    <- the expression
	      --          ^    <- Operand
	"""
	_FORMAT = ("and ", "")


@export
class UnaryNandExpression(UnaryExpression):
	"""
	Represents a ``nand`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := nand v;
	      --      ^^^^^^    <- the expression
	      --           ^    <- Operand
	"""
	_FORMAT = ("nand ", "")


@export
class UnaryOrExpression(UnaryExpression):
	"""
	Represents a ``or`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := or v;
	      --      ^^^^    <- the expression
	      --         ^    <- Operand
	"""
	_FORMAT = ("or ", "")


@export
class UnaryNorExpression(UnaryExpression):
	"""
	Represents a ``nor`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := nor v;
	      --      ^^^^^    <- the expression
	      --          ^    <- Operand
	"""
	_FORMAT = ("nor ", "")


@export
class UnaryXorExpression(UnaryExpression):
	"""
	Represents a ``xor`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := xor v;
	      --      ^^^^^    <- the expression
	      --          ^    <- Operand
	"""
	_FORMAT = ("xor ", "")


@export
class UnaryXnorExpression(UnaryExpression):
	"""
	Represents a ``xnor`` reduction expression (VHDL-2008).

	A reduction operator folds all elements of an array into a single value. The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := xnor v;
	      --      ^^^^^^    <- the expression
	      --           ^    <- Operand
	"""
	_FORMAT = ("xnor ", "")


@export
class AbsoluteExpression(UnaryExpression):
	"""
	Represents a absolute value expression (``abs``).

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := abs a;
	      --     ^^^^^    <- the expression
	      --     ^        <- Operand
	"""
	_FORMAT = ("abs ", "")


@export
class TypeConversion(UnaryExpression):
	"""
	Represents a type conversion.

	A type conversion converts its operand (:data:`Operand`) to the target subtype
	(:data:`TargetSubtype`). Unlike every other :class:`UnaryExpression`, its "operator" is the target
	type name itself rather than a fixed string, so it carries its own subtype and renders itself.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := integer(r);
	      --     ^^^^^^^       <- TargetSubtype
	      --^                  <- Operand
	"""

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
	"""
	Represents a parenthesized sub-expression.

	The operand is available as :data:`Operand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := (a + b);
	      --     ^^^^^^^    <- the sub-expression
	      --      ^^^^^     <- Operand
	"""
	_FORMAT = ("(", ")")


@export
class BinaryExpression(BaseExpression):
	"""
	Represents the base-class of all binary expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""

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
	def LeftOperand(self) -> ExpressionUnion:
		"""
		Read-only property to access the left operand (:attr:`_leftOperand`).

		:returns: The left operand.
		"""
		return self._leftOperand

	@readonly
	def RightOperand(self) -> ExpressionUnion:
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
	"""
	Represents the base-class of range expressions.

	A range has a direction (:data:`Direction`) and two bounds. Both operands are available as :data:`LeftOperand` and
	:data:`RightOperand`.
	"""
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
	"""
	Represents an ascending range expression (``to``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v(0 to 3);
	      --        ^^^^^^     <- the range
	      --        ^          <- LeftOperand
	      --             ^     <- RightOperand
	"""
	_direction = Direction.To
	_FORMAT = ("", " to ", "")


@export
class DescendingRangeExpression(RangeExpression):
	"""
	Represents a descending range expression (``downto``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v(7 downto 4);
	      --        ^^^^^^^^^^     <- the range
	      --        ^              <- LeftOperand
	      --                 ^     <- RightOperand
	"""
	_direction = Direction.DownTo
	_FORMAT = ("", " downto ", "")


@export
class AddingExpression(BinaryExpression):
	"""
	Represents the base-class of all adding expressions: ``+``, ``-`` and ``&``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""


@export
class AdditionExpression(AddingExpression):
	"""
	Represents an addition expression (``+``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a + b;
	      --     ^^^^^    <- the expression
	      --     ^        <- LeftOperand
	      --         ^    <- RightOperand
	"""
	_FORMAT = ("", " + ", "")


@export
class SubtractionExpression(AddingExpression):
	"""
	Represents a subtraction expression (``-``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a - b;
	      --     ^^^^^    <- the expression
	      --     ^        <- LeftOperand
	      --         ^    <- RightOperand
	"""
	_FORMAT = ("", " - ", "")


@export
class ConcatenationExpression(AddingExpression):
	"""
	Represents a concatenation expression (``&``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v & w;
	      --      ^^^^^    <- the expression
	      --^              <- LeftOperand
	      --          ^    <- RightOperand
	"""
	_FORMAT = ("", " & ", "")


@export
class MultiplyingExpression(BinaryExpression):
	"""
	Represents the base-class of all multiplying expressions: ``*``, ``/``, ``rem``, ``mod`` and ``**``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""


@export
class MultiplyExpression(MultiplyingExpression):
	"""
	Represents a multiplication expression (``*``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a * b;
	      --     ^^^^^    <- the expression
	      --     ^        <- LeftOperand
	      --         ^    <- RightOperand
	"""
	_FORMAT = ("", " * ", "")


@export
class DivisionExpression(MultiplyingExpression):
	"""
	Represents a division expression (``/``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a / b;
	      --     ^^^^^    <- the expression
	      --     ^        <- LeftOperand
	      --         ^    <- RightOperand
	"""
	_FORMAT = ("", " / ", "")


@export
class RemainderExpression(MultiplyingExpression):
	"""
	Represents a remainder expression (``rem``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a rem b;
	      --     ^^^^^^^    <- the expression
	      --     ^          <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " rem ", "")


@export
class ModuloExpression(MultiplyingExpression):
	"""
	Represents a modulo expression (``mod``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a mod b;
	      --     ^^^^^^^    <- the expression
	      --     ^          <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " mod ", "")


@export
class ExponentiationExpression(MultiplyingExpression):
	"""
	Represents an exponentiation expression (``**``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a ** 2;
	      --     ^^^^^^    <- the expression
	      --     ^         <- LeftOperand
	      --          ^    <- RightOperand
	"""
	_FORMAT = ("", "**", "")


@export
class LogicalExpression(BinaryExpression):
	"""
	Represents the base-class of all binary logical expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""


@export
class AndExpression(LogicalExpression):
	"""
	Represents a logical ``and`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f and g;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " and ", "")


@export
class NandExpression(LogicalExpression):
	"""
	Represents a logical ``nand`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f nand g;
	      --      ^^^^^^^^    <- the expression
	      --      ^           <- LeftOperand
	      --             ^    <- RightOperand
	"""
	_FORMAT = ("", " nand ", "")


@export
class OrExpression(LogicalExpression):
	"""
	Represents a logical ``or`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f or g;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " or ", "")


@export
class NorExpression(LogicalExpression):
	"""
	Represents a logical ``nor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f nor g;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " nor ", "")


@export
class XorExpression(LogicalExpression):
	"""
	Represents a logical ``xor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f xor g;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " xor ", "")


@export
class XnorExpression(LogicalExpression):
	"""
	Represents a logical ``xnor`` expression.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := f xnor g;
	      --      ^^^^^^^^    <- the expression
	      --      ^           <- LeftOperand
	      --             ^    <- RightOperand
	"""
	_FORMAT = ("", " xnor ", "")


@export
class RelationalExpression(BinaryExpression):
	"""
	Represents the base-class of all relational expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""


@export
class EqualExpression(RelationalExpression):
	"""
	Represents an equality expression (``=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a = b;
	      --      ^^^^^    <- the expression
	      --      ^        <- LeftOperand
	      --^              <- RightOperand
	"""
	_FORMAT = ("", " = ", "")


@export
class UnequalExpression(RelationalExpression):
	"""
	Represents an inequality expression (``/=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a /= b;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --^               <- RightOperand
	"""
	_FORMAT = ("", " /= ", "")


@export
class GreaterThanExpression(RelationalExpression):
	"""
	Represents a greater-than expression (``>``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a > b;
	      --      ^^^^^    <- the expression
	      --      ^        <- LeftOperand
	      --^              <- RightOperand
	"""
	_FORMAT = ("", " > ", "")


@export
class GreaterEqualExpression(RelationalExpression):
	"""
	Represents a greater-or-equal expression (``>=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a >= b;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --^               <- RightOperand
	"""
	_FORMAT = ("", " >= ", "")


@export
class LessThanExpression(RelationalExpression):
	"""
	Represents a less-than expression (``<``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a < b;
	      --      ^^^^^    <- the expression
	      --      ^        <- LeftOperand
	      --^              <- RightOperand
	"""
	_FORMAT = ("", " < ", "")


@export
class LessEqualExpression(RelationalExpression):
	"""
	Represents a less-or-equal expression (``<=``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      bres := a <= b;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --^               <- RightOperand
	"""
	_FORMAT = ("", " <= ", "")


@export
class MatchingRelationalExpression(RelationalExpression):
	"""
	Represents the base-class of all matching relational expressions (VHDL-2008).

	Matching operators return a ``bit``/``std_ulogic`` rather than a ``boolean``. Both operands are available as
	:data:`LeftOperand` and :data:`RightOperand`.
	"""
	pass


@export
class MatchingEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching equality expression (``?=``, VHDL-2008).

	Unlike ``=``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as :data:`LeftOperand`
	and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?= w;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " ?= ", "")


@export
class MatchingUnequalExpression(MatchingRelationalExpression):
	"""
	Represents a matching inequality expression (``?/=``, VHDL-2008).

	Unlike ``/=``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as
	:data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?/= w;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " ?/= ", "")


@export
class MatchingGreaterThanExpression(MatchingRelationalExpression):
	"""
	Represents a matching greater-than expression (``?>``, VHDL-2008).

	Unlike ``>``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as :data:`LeftOperand`
	and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?> w;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " ?> ", "")


@export
class MatchingGreaterEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching greater-or-equal expression (``?>=``, VHDL-2008).

	Unlike ``>=``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as
	:data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?>= w;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " ?>= ", "")


@export
class MatchingLessThanExpression(MatchingRelationalExpression):
	"""
	Represents a matching less-than expression (``?<``, VHDL-2008).

	Unlike ``<``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as :data:`LeftOperand`
	and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?< w;
	      --      ^^^^^^    <- the expression
	      --      ^         <- LeftOperand
	      --           ^    <- RightOperand
	"""
	_FORMAT = ("", " ?< ", "")


@export
class MatchingLessEqualExpression(MatchingRelationalExpression):
	"""
	Represents a matching less-or-equal expression (``?<=``, VHDL-2008).

	Unlike ``<=``, a matching operator returns a ``bit``/``std_ulogic``. Both operands are available as
	:data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      sres := v ?<= w;
	      --      ^^^^^^^    <- the expression
	      --      ^          <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " ?<= ", "")


@export
class ShiftExpression(BinaryExpression):
	"""
	Represents the base-class of all shift and rotate expressions.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""


@export
class ShiftLogicExpression(ShiftExpression):
	"""
	Represents the base-class of the logical shift expressions ``srl`` and ``sll``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""
	pass


@export
class ShiftArithmeticExpression(ShiftExpression):
	"""
	Represents the base-class of the arithmetic shift expressions ``sra`` and ``sla``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""
	pass


@export
class RotateExpression(ShiftExpression):
	"""
	Represents the base-class of the rotate expressions ``ror`` and ``rol``.

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.
	"""
	pass


@export
class ShiftRightLogicExpression(ShiftLogicExpression):
	"""
	Represents a logical right shift expression (``srl``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v srl 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " srl ", "")


@export
class ShiftLeftLogicExpression(ShiftLogicExpression):
	"""
	Represents a logical left shift expression (``sll``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v sll 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " sll ", "")


@export
class ShiftRightArithmeticExpression(ShiftArithmeticExpression):
	"""
	Represents an arithmetic right shift expression (``sra``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v sra 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " sra ", "")


@export
class ShiftLeftArithmeticExpression(ShiftArithmeticExpression):
	"""
	Represents an arithmetic left shift expression (``sla``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v sla 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " sla ", "")


@export
class RotateRightExpression(RotateExpression):
	"""
	Represents a right rotate expression (``ror``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v ror 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " ror ", "")


@export
class RotateLeftExpression(RotateExpression):
	"""
	Represents a left rotate expression (``rol``).

	Both operands are available as :data:`LeftOperand` and :data:`RightOperand`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := v rol 1;
	      --      ^^^^^^^    <- the expression
	      --^                <- LeftOperand
	      --            ^    <- RightOperand
	"""
	_FORMAT = ("", " rol ", "")


@export
class QualifiedExpression(BaseExpression, ParenthesisExpression):
	"""
	Represents a qualified expression.

	A qualified expression states the subtype (:data:`Subtype`) of its operand (:data:`Operand`),
	resolving which of several overloaded meanings is intended.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := byte'(others => '0');
	      --      ^^^^                    <- Subtype
	      --           ^^^^^^^^^^^^^^^    <- Operand
	"""
	_operand:  ExpressionUnion
	_subtype:  Symbol

	def __init__(self, subtype: Symbol, operand: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._operand = operand
		operand.Parent = self

		self._subtype = subtype
		subtype.Parent = self

	@readonly
	def Operand(self) -> ExpressionUnion:
		"""
		Read-only property to access the operand (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	@readonly
	def Subtype(self) -> Symbol:
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
	Represents the base-class of all ternary expressions.
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
	Represents a conditional expression (VHDL-2008).

	A conditional expression selects between two values (:data:`ThenValue`, :data:`ElseValue`) based on
	a condition (:data:`Condition`). It is usable anywhere an expression is expected - distinct from
	:class:`~pyVHDLModel.Common.ConditionalExpression`, which models the cascading ``when``/``else``
	list of a conditional *assignment*.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := a when f else b;
	      --     ^                  <- ThenValue
	      --            ^           <- Condition
	      --                   ^    <- ElseValue
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
	"""
	Represents a call to a function.

	.. admonition:: Example

	   .. code-block:: VHDL

	      res := maximum(a, b);
	      --     ^^^^^^^^^^^^^    <- the call
	"""
	pass


@export
class Allocation(BaseExpression):
	"""
	Represents the base-class of all allocations via ``new``.
	"""
	pass


@export
class SubtypeAllocation(Allocation):
	"""
	Represents an allocation of a subtype via ``new``.

	The allocated subtype is available as :data:`Subtype`. The allocated object is default-initialized.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := new integer;
	      --       ^^^^^^^    <- Subtype
	"""
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
	"""
	Represents an allocation initialized by a qualified expression.

	The qualified expression providing the initial value is available as :data:`QualifiedExpression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      p := new integer'(5);
	      --       ^^^^^^^^^^^    <- QualifiedExpression
	"""
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
	"""
	Represents the base-class of all aggregate elements.

	Every element carries the value assigned to it (:data:`Expression`).
	"""

	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		"""
		Read-only property to access the expression (:attr:`_expression`).

		:returns: The expression.
		"""
		return self._expression


@export
class SimpleAggregateElement(AggregateElement):
	"""
	Represents an aggregate element given by position.

	A positional element has no choice of its own; only its value (:data:`Expression`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := ('1', '0', '1', '0', '1', '0', '1', '0');
	      --       ^^^                                        <- Expression
	"""
	def __str__(self) -> str:
		return str(self._expression)


@export
class IndexedAggregateElement(AggregateElement):
	"""
	Represents an aggregate element chosen by an index.

	The index is available as :data:`Index`, the assigned value as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := (0 => '1', others => '0');
	      --       ^                           <- Index
	      --            ^^^                    <- Expression
	"""
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
	"""
	Represents an aggregate element chosen by a range.

	The range is available as :data:`Range`, the assigned value as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := (1 to 3 => '0', others => '1');
	      --       ^^^^^^                           <- Range
	      --                 ^^^                    <- Expression
	"""
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
	"""
	Represents an aggregate element chosen by a name.

	Used for record aggregates, where the choice names a record element (:data:`Name`).

	.. admonition:: Example

	   .. code-block:: VHDL

	      r := (a => '1', b => '0');
	      --    ^                      <- Name
	      --         ^^^               <- Expression
	"""
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
	"""
	Represents the ``others`` element of an aggregate.

	It supplies the value (:data:`Expression`) for every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := (0 => '1', others => '0');
	      --                 ^^^^^^            <- the choice
	      --                           ^^^     <- Expression
	"""
	def __str__(self) -> str:
		return "others => {value!s}".format(
			value=self._expression,
		)


@export
class Aggregate(BaseExpression):
	"""
	Represents an aggregate.

	An aggregate composes a value from its elements (:data:`Elements`), each of which associates a
	choice with a value.

	.. admonition:: Example

	   .. code-block:: VHDL

	      vres := (0 => '1', 1 to 3 => '0', others => '1');
	      --      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    <- Elements
	"""
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
