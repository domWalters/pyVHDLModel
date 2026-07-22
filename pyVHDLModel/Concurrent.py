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

Concurrent defines all concurrent statements used in entities, architectures, generates and block statements.
"""
from typing                  import List, Dict, Union, Iterable, Generator, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin, DocumentedEntityMixin, Range, BaseChoice, BaseCase, IfBranchMixin
from pyVHDLModel.Base        import ElsifBranchMixin, ElseBranchMixin, AssertStatementMixin, BlockStatementMixin, WaveformElement
from pyVHDLModel.Regions     import ConcurrentDeclarationRegionMixin
from pyVHDLModel.Namespace   import Namespace
from pyVHDLModel.Name        import Name
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol, ConfigurationInstantiationSymbol
from pyVHDLModel.Symbol      import SignalSymbol
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Association import AssociationItem, ParameterAssociationItem
from pyVHDLModel.Interface   import PortInterfaceItemMixin
from pyVHDLModel.Common      import Statement, ProcedureCallMixin, SignalAssignmentMixin, AllowBlackboxMixin
from pyVHDLModel.Common      import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Common      import ConditionalWaveformsMixin, WaveformMixin
from pyVHDLModel.Sequential  import SequentialStatement, SequentialStatementsMixin, SequentialDeclarationsMixin


ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
class ConcurrentStatement(Statement):
	"""A base-class for all concurrent statements."""


@export
class ConcurrentStatementsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all language constructs supporting concurrent statements.

	.. seealso::

	   .. todo:: concurrent declaration region
	"""

	_statements:     List[ConcurrentStatement]

	_instantiations: Dict[str, 'Instantiation']  # TODO: add another instantiation class level for entity/configuration/component inst.
	_blocks:         Dict[str, 'ConcurrentBlockStatement']
	_generates:      Dict[str, 'GenerateStatement']
	_hierarchy:      Dict[str, Union['ConcurrentBlockStatement', 'GenerateStatement']]

	def __init__(self, statements: Nullable[Iterable[ConcurrentStatement]] = None) -> None:
		self._statements = []

		self._instantiations = {}
		self._blocks = {}
		self._generates = {}
		self._hierarchy = {}

		if statements is not None:
			for statement in statements:
				self._statements.append(statement)
				statement.Parent = self

	@readonly
	def Statements(self) -> List[ConcurrentStatement]:
		return self._statements

	def IterateInstantiations(self) -> Generator['Instantiation', None, None]:
		for instance in self._instantiations.values():
			yield instance

		for block in self._blocks.values():
			yield from block.IterateInstantiations()

		for generate in self._generates.values():
			yield from generate.IterateInstantiations()

	# TODO: move into _init__
	def IndexStatements(self) -> None:
		for statement in self._statements:
			if isinstance(statement, (EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation)):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, (ForGenerateStatement, IfGenerateStatement, CaseGenerateStatement)):
				self._generates[statement.NormalizedLabel] = statement
				statement.IndexStatement()
			elif isinstance(statement, ConcurrentBlockStatement):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.IndexStatements()


@export
class Instantiation(ConcurrentStatement):
	"""
	A base-class for all (component) instantiations.
	"""

	_genericAssociationItems: List[AssociationItem]
	_portAssociationItems:    List[AssociationItem]

	def __init__(
		self,
		label: str,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)

		# TODO: extract to mixin
		self._genericAssociationItems = []
		if genericAssociationItems is not None:
			for association in genericAssociationItems:
				self._genericAssociationItems.append(association)
				association.Parent = self

		# TODO: extract to mixin
		self._portAssociationItems = []
		if portAssociationItems is not None:
			for association in portAssociationItems:
				self._portAssociationItems.append(association)
				association.Parent = self

	@readonly
	def GenericAssociationItems(self) -> List[AssociationItem]:
		return self._genericAssociationItems

	@property
	def PortAssociationItems(self) -> List[AssociationItem]:
		return self._portAssociationItems


@export
class ComponentInstantiation(Instantiation):
	"""
	Represents a component instantiation by referring to a component name.

	.. admonition:: Example

	   .. code-block:: VHDL

	      inst : component Counter;
	"""

	_component: ComponentInstantiationSymbol

	def __init__(
		self,
		label: str,
		componentSymbol: ComponentInstantiationSymbol,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._component = componentSymbol
		componentSymbol.Parent = self

	@property
	def Component(self) -> ComponentInstantiationSymbol:
		return self._component


@export
class EntityInstantiation(Instantiation):
	"""
	Represents an entity instantiation by referring to an entity name with optional architecture name.

	.. admonition:: Example

	   .. code-block:: VHDL

	      inst : entity work. Counter;
	"""

	_entity: EntityInstantiationSymbol
	_architecture: ArchitectureSymbol

	def __init__(
		self,
		label: str,
		entitySymbol: EntityInstantiationSymbol,
		architectureSymbol: Nullable[ArchitectureSymbol] = None,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._entity = entitySymbol
		entitySymbol.Parent = self

		self._architecture = architectureSymbol
		if architectureSymbol is not None:
			architectureSymbol.Parent = self

	@property
	def Entity(self) -> EntityInstantiationSymbol:
		return self._entity

	@property
	def Architecture(self) -> ArchitectureSymbol:
		return self._architecture


@export
class ConfigurationInstantiation(Instantiation):
	"""
	Represents a configuration instantiation by referring to a configuration name.

	.. admonition:: Example

	   .. code-block:: VHDL

	      inst : configuration Counter;
	"""

	_configuration: ConfigurationInstantiationSymbol

	def __init__(
		self,
		label: str,
		configurationSymbol: ConfigurationInstantiationSymbol,
		genericAssociationItems: Nullable[Iterable[AssociationItem]] = None,
		portAssociationItems:    Nullable[Iterable[AssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, genericAssociationItems, portAssociationItems, parent)

		self._configuration = configurationSymbol
		configurationSymbol.Parent = self

	@property
	def Configuration(self) -> ConfigurationInstantiationSymbol:
		return self._configuration


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarationsMixin, SequentialStatementsMixin, DocumentedEntityMixin):
	"""
	Represents a process statement with sensitivity list, sequential declaration region and sequential statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      proc: process(Clock)
	        -- sequential declarations
	      begin
	        -- sequential statements
	      end process;
	"""

	_sensitivityList: List[Name]  # TODO: implement a SignalSymbol

	def __init__(
		self,
		label: Nullable[str] = None,
		declaredItems: Nullable[Iterable] = None,
		statements: Nullable[Iterable[SequentialStatement]] = None,
		sensitivityList: Nullable[Iterable[Name]] = None,
		documentation: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		SequentialDeclarationsMixin.__init__(self, declaredItems)
		SequentialStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				# signalSymbol._parent = self  # FIXME: currently str are provided

	@property
	def SensitivityList(self) -> List[Name]:
		return self._sensitivityList


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCallMixin):
	def __init__(
		self,
		label: str,
		procedureName: Name,
		parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		ProcedureCallMixin.__init__(self, procedureName, parameterAssociationItems)


@export
class ConcurrentBlockStatement(ConcurrentStatement, BlockStatementMixin, LabeledEntityMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, DocumentedEntityMixin, AllowBlackboxMixin):
	_portItems: List[PortInterfaceItemMixin]

	_namespace: Namespace

	def __init__(
		self,
		label:         str,
		portItems:     Nullable[Iterable[PortInterfaceItemMixin]] = None,
		declaredItems: Nullable[Iterable] = None,
		statements:    Iterable['ConcurrentStatement'] = None,
		documentation: Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)

		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		BlockStatementMixin.__init__(self)
		LabeledEntityMixin.__init__(self, label)
		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

		# TODO: extract to mixin
		self._portItems = []
		if portItems is not None:
			for item in portItems:
				self._portItems.append(item)
				item.Parent = self

	@ConcurrentStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ConcurrentStatement.Parent.fset(self, parent)

		self._namespace.ParentNamespace = parent._namespace

	@property
	def PortItems(self) -> List[PortInterfaceItemMixin]:
		return self._portItems


@export
class GenerateBranch(ModelEntity, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin):
	"""
	A base-class for all branches in a generate statements.

	.. seealso::

	   * :class:`If-generate branch <pyVHDLModel.Concurrent.IfGenerateBranch>`
	   * :class:`Elsif-generate branch <pyVHDLModel.Concurrent.ElsifGenerateBranch>`
	   * :class:`Else-generate branch <pyVHDLModel.Concurrent.ElseGenerateBranch>`
	"""

	_alternativeLabel:           Nullable[str]
	_normalizedAlternativeLabel: Nullable[str]

	_namespace:                  Namespace

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		self._alternativeLabel = alternativeLabel
		self._normalizedAlternativeLabel = alternativeLabel.lower() if alternativeLabel is not None else None

		self._namespace = Namespace(self._normalizedAlternativeLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	@property
	def AlternativeLabel(self) -> Nullable[str]:
		return self._alternativeLabel

	@property
	def NormalizedAlternativeLabel(self) -> Nullable[str]:
		return self._normalizedAlternativeLabel


@export
class IfGenerateBranch(GenerateBranch, IfBranchMixin):
	"""
	Represents if-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      elsif condition generate
	        -- ...
	      else generate
	        -- ...
	      end generate;
	"""

	def __init__(
		self,
		condition:        ExpressionUnion,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		IfBranchMixin.__init__(self, condition)


@export
class ElsifGenerateBranch(GenerateBranch, ElsifBranchMixin):
	"""
	Represents elsif-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- ...
	      elsif condition generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      else generate
	        -- ...
	      end generate;
	"""

	def __init__(
		self,
		condition:        ExpressionUnion,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		ElsifBranchMixin.__init__(self, condition)


@export
class ElseGenerateBranch(GenerateBranch, ElseBranchMixin):
	"""
	Represents else-generate branch in a generate statement with a concurrent declaration region and concurrent statements.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- ...
	      elsif condition generate
	        -- ...
	      else generate
	        -- concurrent declarations
	      begin
	        -- concurrent statements
	      end generate;
	"""

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)
		ElseBranchMixin.__init__(self)


@export
class GenerateStatement(ConcurrentStatement, AllowBlackboxMixin):
	"""
	A base-class for all generate statements.

	.. seealso::

	   * :class:`If...generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`Case...generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	   * :class:`For...generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	"""

	def __init__(
		self,
		label:         Nullable[str] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	# @mustoverride
	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		raise NotImplementedError()

	# @mustoverride
	def IndexStatement(self) -> None:
		raise NotImplementedError()


@export
class IfGenerateStatement(GenerateStatement):
	"""
	Represents an if...generate statement.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: if condition generate
	        -- ...
	      elsif condition generate
	        -- ...
	      else generate
	        -- ...
	      end generate;

	.. seealso::

	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>` base-class
	   * :class:`If-generate branch <pyVHDLModel.Concurrent.IfGenerateBranch>`
	   * :class:`Elsif-generate branch <pyVHDLModel.Concurrent.ElsifGenerateBranch>`
	   * :class:`Else-generate branch <pyVHDLModel.Concurrent.ElseGenerateBranch>`
	"""

	_ifBranch:      IfGenerateBranch
	_elsifBranches: List[ElsifGenerateBranch]
	_elseBranch:    Nullable[ElseGenerateBranch]

	def __init__(
		self,
		label:         str,
		ifBranch:      IfGenerateBranch,
		elsifBranches: Nullable[Iterable[ElsifGenerateBranch]] = None,
		elseBranch:    Nullable[ElseGenerateBranch] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, allowBlackbox, parent)

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

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		from pyVHDLModel.DesignUnit import Architecture

		GenerateStatement.Parent.fset(self, parent)

		# Connect namespaces
		namespace = self._ifBranch._namespace
		namespace.ParentNamespace = parent._namespace
		if namespace._name == "":
			namespace._name = self._normalizedLabel

		for elseBranch in self._elsifBranches:
			elseBranch._namespace.ParentNamespace = parent._namespace

		if self._elseBranch is not None:
			self._elseBranch._namespace.ParentNamespace = parent._namespace

	@property
	def IfBranch(self) -> IfGenerateBranch:
		return self._ifBranch

	@property
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		return self._elsifBranches

	@property
	def ElseBranch(self) -> Nullable[ElseGenerateBranch]:
		return self._elseBranch

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		yield from self._ifBranch.IterateInstantiations()
		for branch in self._elsifBranches:
			yield from branch.IterateInstantiations()
		if self._elseBranch is not None:
			yield from self._ifBranch.IterateInstantiations()

	def IndexStatement(self) -> None:
		self._ifBranch.IndexStatements()
		for branch in self._elsifBranches:
			branch.IndexStatements()
		if self._elseBranch is not None:
			self._elseBranch.IndexStatements()


@export
class ConcurrentChoice(BaseChoice):
	"""A base-class for all concurrent choices (in case...generate statements)."""


@export
class IndexedGenerateChoice(ConcurrentChoice):
	_expression: ExpressionUnion

	def __init__(self, expression: ExpressionUnion, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._expression = expression
		expression.Parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression

	def __str__(self) -> str:
		return str(self._expression)


@export
class RangedGenerateChoice(ConcurrentChoice):
	_range: 'Range'

	def __init__(self, rng: 'Range', parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._range = rng
		rng.Parent = self

	@property
	def Range(self) -> 'Range':
		return self._range

	def __str__(self) -> str:
		return str(self._range)


@export
class ConcurrentCase(BaseCase, LabeledEntityMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin):
	_namespace: Namespace

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)
		LabeledEntityMixin.__init__(self, alternativeLabel)

		# TODO: Why not handover self?
		#       This allows access to Label and NormalizedLabel, also to create a full instance path in case a lookup goes wrong.
		# TODO: How about a WithNamespaceMixin class?
		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		AllowBlackboxMixin.__init__(self, allowBlackbox)


@export
class GenerateCase(ConcurrentCase):
	_choices: List[ConcurrentChoice]

	def __init__(
		self,
		choices:          Iterable[ConcurrentChoice],
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(declaredItems, statements, alternativeLabel, allowBlackbox, parent)

		# TODO: move to parent or grandparent
		self._choices = []
		if choices is not None:
			for choice in choices:
				self._choices.append(choice)
				choice.Parent = self

	# TODO: move to parent or grandparent
	@property
	def Choices(self) -> List[ConcurrentChoice]:
		return self._choices

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersGenerateCase(ConcurrentCase):
	def __str__(self) -> str:
		return "when others =>"


@export
class CaseGenerateStatement(GenerateStatement):
	"""
	Represents a case...generate statement.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: case selector generate
	        case choice1 =>
	          -- ...
	        case choice2 =>
	          -- ...
	        case others =>
	          -- ...
	      end generate;
	"""

	_expression: ExpressionUnion
	_cases:      List[GenerateCase]

	def __init__(
		self,
		label:         str,
		expression:    ExpressionUnion,
		cases:         Iterable[ConcurrentCase],
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, allowBlackbox, parent)

		self._expression = expression
		expression.Parent = self

		# TODO: create a mixin for things with cases
		self._cases = []
		if cases is not None:
			for case in cases:
				self._cases.append(case)
				case.Parent = self

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		GenerateStatement.Parent.fset(self, parent)

		# Connect namespaces
		for case in self._cases:
			case._namespace.ParentNamespace = parent._namespace

	@property
	def SelectExpression(self) -> ExpressionUnion:
		return self._expression

	@property
	def Cases(self) -> List[GenerateCase]:
		return self._cases

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		for case in self._cases:
			yield from case.IterateInstantiations()

	def IndexStatement(self) -> None:
		for case in self._cases:
			case.IndexStatements()


@export
class ForGenerateStatement(GenerateStatement, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin):
	"""
	Represents a for...generate statement.

	.. admonition:: Example

	   .. code-block:: VHDL

	      gen: for i in 0 to 3 generate
	        -- ...
	      end generate;
	"""

	_loopIndex: str
	_range:     Range

	_namespace: Namespace

	def __init__(
		self,
		label:         str,
		loopIndex:     str,
		rng:           Range,
		declaredItems: Nullable[Iterable] = None,
		statements:    Nullable[Iterable[ConcurrentStatement]] = None,
		allowBlackbox: Nullable[bool] = None,
		parent:        Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, allowBlackbox, parent)

		self._namespace = Namespace(self._normalizedLabel)
		if parent is not None:
			self._namespace.ParentNamespace = parent._namespace

		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)

		self._loopIndex = loopIndex

		self._range = rng
		rng.Parent = self

	@GenerateStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		GenerateStatement.Parent.fset(self, parent)

		self._namespace.ParentNamespace = parent._namespace

	@property
	def LoopIndex(self) -> str:
		return self._loopIndex

	@property
	def Range(self) -> Range:
		return self._range

	# IndexDeclaredItems = ConcurrentStatements.IndexDeclaredItems

	def IndexStatement(self) -> None:
		self.IndexStatements()

	def IndexStatements(self) -> None:
		super().IndexStatements()

	def IterateInstantiations(self) -> Generator[Instantiation, None, None]:
		return ConcurrentStatementsMixin.IterateInstantiations(self)


@export
class ConcurrentSignalAssignment(ConcurrentStatement, SignalAssignmentMixin):
	"""
	A base-class for concurrent signal assignments.

	.. seealso::

	   * :class:`~pyVHDLModel.Concurrent.ConcurrentSimpleSignalAssignment`
	   * :class:`~pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment`
	   * :class:`~pyVHDLModel.Concurrent.ConcurrentConditionalSignalAssignment`
	"""
	def __init__(self, label: str, target: SignalSymbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class ConcurrentSimpleSignalAssignment(ConcurrentSignalAssignment, WaveformMixin):
	def __init__(self, label: str, target: SignalSymbol, waveform: Iterable[WaveformElement], parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, target, parent)
		WaveformMixin.__init__(self, waveform)


@export
class ConcurrentSelectedSignalAssignment(ConcurrentSignalAssignment):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select s <= '1' when 0, '0' when others;
	"""

	_expression:        ExpressionUnion
	_selectedWaveforms: List[SelectedWaveform]

	def __init__(
		self,
		label: str,
		target: SignalSymbol,
		expression: ExpressionUnion,
		selectedWaveforms: Iterable[SelectedWaveform],
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, target, parent)

		self._expression = expression
		expression.Parent = self

		self._selectedWaveforms = []
		for selectedWaveform in selectedWaveforms:
			self._selectedWaveforms.append(selectedWaveform)
			selectedWaveform.Parent = self

	@readonly
	def Expression(self) -> ExpressionUnion:
		return self._expression

	@readonly
	def SelectedWaveforms(self) -> List[SelectedWaveform]:
		return self._selectedWaveforms


@export
class ConcurrentConditionalSignalAssignment(ConcurrentSignalAssignment, ConditionalWaveformsMixin):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1' when cond1 else '0' when cond2 else 'Z';
	"""

	def __init__(
		self,
		label: str,
		target: SignalSymbol,
		conditionalWaveforms: Iterable[ConditionalWaveform],
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, target, parent)
		ConditionalWaveformsMixin.__init__(self, conditionalWaveforms)


@export
class ConcurrentAssertStatement(ConcurrentStatement, AssertStatementMixin):
	def __init__(
		self,
		condition: ExpressionUnion,
		message: ExpressionUnion,
		severity: Nullable[ExpressionUnion] = None,
		label: Nullable[str] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, parent)
		AssertStatementMixin.__init__(self, condition, message, severity)
