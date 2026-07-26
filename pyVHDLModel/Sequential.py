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

Declarations for sequential statements.
"""
from typing                  import List, Iterable, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, ExpressionUnion, Range, BaseChoice, BaseCase, ConditionalMixin, IfBranchMixin, ElsifBranchMixin
from pyVHDLModel.Base        import ElseBranchMixin, ReportStatementMixin, AssertStatementMixin, WaveformElement, ChoicesMixin
from pyVHDLModel.Symbol      import Symbol, SignalSymbol, VariableSymbol
from pyVHDLModel.Common      import Statement, ProcedureCallMixin
from pyVHDLModel.Common      import AssignmentMixin, SignalAssignmentMixin, VariableAssignmentMixin
from pyVHDLModel.Common      import ConditionalWaveform, ConditionalExpression
from pyVHDLModel.Common      import ConditionalWaveformsMixin, WaveformMixin
from pyVHDLModel.Common      import ExpressionMixin, SelectedWaveformsMixin, SelectedExpressionsMixin
from pyVHDLModel.Common      import SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Common      import SelectedExpression, OthersSelectedExpression
from pyVHDLModel.Association import ParameterAssociationItem


@export
class SequentialStatement(Statement):
	"""A ``SequentialStatement`` is a base-class for all sequential statements."""


@export
class SequentialStatementsMixin(metaclass=ExtendedType, mixin=True):
	_statements: List[SequentialStatement]

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None) -> None:
		# TODO: extract to mixin
		self._statements = []
		if statements is not None:
			for item in statements:
				self._statements.append(item)
				item.Parent = self

	@readonly
	def Statements(self) -> List[SequentialStatement]:
		"""
		Read-only property to access the list of sequential statements (:attr:`_statements`).

		:returns: A list of sequential statements.
		"""
		return self._statements


@export
class SequentialProcedureCall(SequentialStatement, ProcedureCallMixin):
	def __init__(
		self,
		procedureName: Symbol,
		parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		ProcedureCallMixin.__init__(self, procedureName, parameterAssociationItems)


@export
class SequentialSignalAssignment(SequentialStatement, SignalAssignmentMixin):
	def __init__(self, target: SignalSymbol, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class SequentialSimpleSignalAssignment(SequentialSignalAssignment, WaveformMixin):
	def __init__(self, target: SignalSymbol, waveform: Iterable[WaveformElement], label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(target, label, parent)
		WaveformMixin.__init__(self, waveform)


@export
class SequentialVariableAssignment(SequentialStatement, VariableAssignmentMixin):
	def __init__(self, target: VariableSymbol, expression: ExpressionUnion, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		VariableAssignmentMixin.__init__(self, target, expression)


@export
class SequentialConditionalVariableAssignment(SequentialStatement, AssignmentMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      v := '1' when cond1 else '0' when cond2 else 'Z';
	"""

	_conditionalExpressions: List[ConditionalExpression]

	def __init__(
		self,
		target: VariableSymbol,
		conditionalExpressions: Iterable[ConditionalExpression],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		AssignmentMixin.__init__(self, target)

		self._conditionalExpressions = []
		for conditionalExpression in conditionalExpressions:
			self._conditionalExpressions.append(conditionalExpression)
			conditionalExpression.Parent = self

	@readonly
	def ConditionalExpressions(self) -> List[ConditionalExpression]:
		"""
		Read-only property to access the conditional expressions (:attr:`_conditionalExpressions`).

		:returns: List of conditional expressions.
		"""
		return self._conditionalExpressions


@export
class SequentialConditionalSignalAssignment(SequentialStatement, SignalAssignmentMixin, ConditionalWaveformsMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1' when cond1 else '0' when cond2 else 'Z';
	"""

	def __init__(
		self,
		target: SignalSymbol,
		conditionalWaveforms: Iterable[ConditionalWaveform],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ConditionalWaveformsMixin.__init__(self, conditionalWaveforms)


@export
class SequentialSelectedVariableAssignment(SequentialStatement, AssignmentMixin, ExpressionMixin, SelectedExpressionsMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select v := '1' when 0, '0' when others;
	"""

	def __init__(
		self,
		target: VariableSymbol,
		expression: ExpressionUnion,
		selectedExpressions: Iterable[SelectedExpression],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		AssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)
		SelectedExpressionsMixin.__init__(self, selectedExpressions)


@export
class SequentialSelectedSignalAssignment(SequentialStatement, SignalAssignmentMixin, ExpressionMixin, SelectedWaveformsMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select s <= '1' when 0, '0' when others;
	"""

	def __init__(
		self,
		target: SignalSymbol,
		expression: ExpressionUnion,
		selectedWaveforms: Iterable[SelectedWaveform],
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)
		SelectedWaveformsMixin.__init__(self, selectedWaveforms)


@export
class SignalForceAssignment(SequentialStatement, SignalAssignmentMixin, ExpressionMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= force '1';
	"""

	def __init__(
		self,
		target: SignalSymbol,
		expression: ExpressionUnion,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)
		ExpressionMixin.__init__(self, expression)


@export
class SignalReleaseAssignment(SequentialStatement, SignalAssignmentMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= release;
	"""

	def __init__(self, target: SignalSymbol, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class SequentialReportStatement(SequentialStatement, ReportStatementMixin):
	def __init__(self, message: ExpressionUnion, severity: Nullable[ExpressionUnion] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		ReportStatementMixin.__init__(self, message, severity)


@export
class SequentialAssertStatement(SequentialStatement, AssertStatementMixin):
	def __init__(
		self,
		condition: ExpressionUnion,
		message: Nullable[ExpressionUnion] = None,
		severity: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		AssertStatementMixin.__init__(self, condition, message, severity)


@export
class CompoundStatement(SequentialStatement):
	"""A ``CompoundStatement`` is a base-class for all compound statements."""


@export
class Branch(ModelEntity, SequentialStatementsMixin):
	"""A ``Branch`` is a base-class for all branches in a if statement."""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)


@export
class IfBranch(Branch, IfBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(statements, parent)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifBranch(Branch, ElsifBranchMixin):
	def __init__(self, condition: ExpressionUnion, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(statements, parent)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseBranch(Branch, ElseBranchMixin):
	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(statements, parent)
		ElseBranchMixin.__init__(self)


@export
class IfStatement(CompoundStatement):
	_ifBranch: IfBranch
	_elsifBranches: List['ElsifBranch']
	_elseBranch: Nullable[ElseBranch]

	def __init__(
		self,
		ifBranch: IfBranch,
		elsifBranches: Nullable[Iterable[ElsifBranch]] = None,
		elseBranch: Nullable[ElseBranch] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)

		self._ifBranch = ifBranch
		ifBranch.Parent = self

		self._elsifBranches = []
		if elsifBranches is not None:
			for branch in elsifBranches:
				self._elsifBranches.append(branch)
				branch.Parent = self

		if elseBranch is not None:
			self._elseBranch = elseBranch
			elseBranch.Parent = self
		else:
			self._elseBranch = None

	@readonly
	def IfBranch(self) -> IfBranch:
		"""
		Read-only property to access the if-branch of the if-statement (:attr:`_ifBranch`).

		:returns: The if-branch.
		"""
		return self._ifBranch

	@readonly
	def ElsIfBranches(self) -> List['ElsifBranch']:
		"""
		Read-only property to access the elsif-branch of the if-statement (:attr:`_elsifBranch`).

		:returns: The elsif-branch.
		"""
		return self._elsifBranches

	@readonly
	def ElseBranch(self) -> Nullable[ElseBranch]:
		"""
		Read-only property to access the else-branch of the if-statement (:attr:`_elseBranch`).

		:returns: The else-branch.
		"""
		return self._elseBranch


@export
class SequentialChoice(BaseChoice):
	"""A ``SequentialChoice`` is a base-class for all sequential choices (in case statements)."""


@export
class IndexedChoice(SequentialChoice):
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

	def __str__(self) -> str:
		return str(self._expression)


@export
class RangedChoice(SequentialChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range', parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._range = rng
		rng.Parent = self

	@readonly
	def Range(self) -> 'Range':
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range

	def __str__(self) -> str:
		return str(self._range)


@export
class SequentialCase(BaseCase, SequentialStatementsMixin, ChoicesMixin):
	def __init__(
		self,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		choices: Nullable[Iterable[BaseChoice]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)
		SequentialStatementsMixin.__init__(self, statements)
		ChoicesMixin.__init__(self, choices)


@export
class Case(SequentialCase):
	def __init__(self, choices: Iterable[SequentialChoice], statements: Nullable[Iterable[SequentialStatement]] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(statements, choices, parent)

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersCase(SequentialCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class CaseStatement(CompoundStatement):
	_expression: ExpressionUnion
	_cases:      List[SequentialCase]

	def __init__(self, expression: ExpressionUnion, cases: Iterable[SequentialCase], label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)

		self._expression = expression
		expression.Parent = self

		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case.Parent = self

	@readonly
	def SelectExpression(self) -> ExpressionUnion:
		"""
		Read-only property to access the select expression (:attr:`_expression`).

		:returns: The select expression.
		"""
		return self._expression

	@readonly
	def Cases(self) -> List[SequentialCase]:
		"""
		Read-only property to access the cases (:attr:`_cases`).

		:returns: List of cases.
		"""
		return self._cases


@export
class LoopStatement(CompoundStatement, SequentialStatementsMixin):
	"""A ``LoopStatement`` is a base-class for all loop statements."""

	def __init__(self, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		SequentialStatementsMixin.__init__(self, statements)


@export
class EndlessLoopStatement(LoopStatement):
	pass


@export
class ForLoopStatement(LoopStatement):
	_loopIndex: str
	_range:     Range

	def __init__(self, loopIndex: str, rng: Range, statements: Nullable[Iterable[SequentialStatement]] = None, label: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(statements, label, parent)

		self._loopIndex = loopIndex

		self._range = rng
		rng.Parent = self

	@readonly
	def LoopIndex(self) -> str:
		"""
		Read-only property to access the loop index (:attr:`_loopIndex`).

		:returns: The loop index.
		"""
		return self._loopIndex

	@readonly
	def Range(self) -> Range:
		"""
		Read-only property to access the range (:attr:`_range`).

		:returns: The range.
		"""
		return self._range


@export
class WhileLoopStatement(LoopStatement, ConditionalMixin):
	def __init__(
		self,
		condition: ExpressionUnion,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(statements, label, parent)
		ConditionalMixin.__init__(self, condition)


@export
class LoopControlStatement(SequentialStatement, ConditionalMixin):
	"""A ``LoopControlStatement`` is a base-class for all loop controlling statements."""

	_loopReference: LoopStatement

	def __init__(self, condition: Nullable[ExpressionUnion] = None, loopLabel: Nullable[str] = None, parent: Nullable[ModelEntity] = None) -> None:  # TODO: is this label (currently str) a Name or a Label class?
		super().__init__(parent)
		ConditionalMixin.__init__(self, condition)

		self._loopReference = None

		# TODO: loopLabel
		# TODO: loop reference -> is it a symbol?

	@readonly
	def LoopReference(self) -> LoopStatement:
		"""
		Read-only property to access the loop reference (:attr:`_loopReference`).

		:returns: The loop reference.
		"""
		return self._loopReference


@export
class NextStatement(LoopControlStatement):
	pass


@export
class ExitStatement(LoopControlStatement):
	pass


@export
class NullStatement(SequentialStatement):
	pass


@export
class ReturnStatement(SequentialStatement):
	_returnValue: Nullable[ExpressionUnion]

	def __init__(
		self,
		returnValue: Nullable[ExpressionUnion] = None,
		label:       Nullable[str] =             None,
		parent:      Nullable[ModelEntity] =     None
	) -> None:
		super().__init__(label, parent)

		self._returnValue = returnValue
		if returnValue is not None:
			returnValue.Parent = self

	@readonly
	def ReturnValue(self) -> Nullable[ExpressionUnion]:
		"""
		Read-only property to access the return value (:attr:`_returnValue`).

		:returns: The return value, or ``None`` if not set.
		"""
		return self._returnValue


@export
class WaitStatement(SequentialStatement, ConditionalMixin):
	_sensitivityList: Nullable[List[Symbol]]
	_timeout:         ExpressionUnion

	def __init__(
		self,
		sensitivityList: Nullable[Iterable[Symbol]] = None,
		condition: Nullable[ExpressionUnion] = None,
		timeout: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		ConditionalMixin.__init__(self, condition)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				signalSymbol.Parent = self

		self._timeout = timeout
		if timeout is not None:
			timeout.Parent = self

	@readonly
	def SensitivityList(self) -> List[Symbol]:
		"""
		Read-only property to access the sensitivity list (:attr:`_sensitivityList`).

		:returns: List of sensitivity list.
		"""
		return self._sensitivityList

	@readonly
	def Timeout(self) -> ExpressionUnion:
		"""
		Read-only property to access the timeout (:attr:`_timeout`).

		:returns: The timeout.
		"""
		return self._timeout


