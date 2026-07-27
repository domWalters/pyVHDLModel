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
from pyVHDLModel.Base        import ElsifBranchMixin, ElseBranchMixin, AssertStatementMixin, BlockStatementMixin, WaveformElement, ChoicesMixin
from pyVHDLModel.Regions     import ConcurrentDeclarationRegionMixin, SequentialDeclarationRegionMixin
from pyVHDLModel.Namespace   import Namespace
from pyVHDLModel.Name        import Name
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol, EntityInstantiationSymbol, ArchitectureSymbol, ConfigurationInstantiationSymbol
from pyVHDLModel.Symbol      import SignalSymbol
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Association import AssociationItem, ParameterAssociationItem
from pyVHDLModel.Interface   import PortInterfaceItemMixin, WithPortsMixin
from pyVHDLModel.Common      import Statement, ProcedureCallMixin, SignalAssignmentMixin, AllowBlackboxMixin
from pyVHDLModel.Common      import ConditionalWaveform, SelectedWaveform, OthersSelectedWaveform
from pyVHDLModel.Common      import ConditionalWaveformsMixin, WaveformMixin
from pyVHDLModel.Common      import ExpressionMixin, SelectedWaveformsMixin
from pyVHDLModel.Sequential  import SequentialStatement, SequentialStatementsMixin


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
	"""
	A base-class for all concurrent statements.

	.. seealso::

	   * :class:`Concurrent assert statement <pyVHDLModel.Concurrent.ConcurrentAssertStatement>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Concurrent procedure call <pyVHDLModel.Concurrent.ConcurrentProcedureCall>`
	   * :class:`Concurrent signal assignment <pyVHDLModel.Concurrent.ConcurrentSignalAssignment>`
	   * :class:`Generate statement <pyVHDLModel.Concurrent.GenerateStatement>`
	   * :class:`Instantiation <pyVHDLModel.Concurrent.Instantiation>`
	   * :class:`Process statement <pyVHDLModel.Concurrent.ProcessStatement>`
	"""


@export
class ConcurrentStatementsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class for all language constructs supporting concurrent statements.

	.. seealso::

	   * :class:`Architecture <pyVHDLModel.DesignUnit.Architecture>`
	   * :class:`Concurrent block statement <pyVHDLModel.Concurrent.ConcurrentBlockStatement>`
	   * :class:`Concurrent case <pyVHDLModel.Concurrent.ConcurrentCase>`
	   * :class:`Entity <pyVHDLModel.DesignUnit.Entity>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	   * :class:`Generate branch <pyVHDLModel.Concurrent.GenerateBranch>`

	   .. todo:: concurrent declaration region
	"""

	_statements:     List[ConcurrentStatement]

	_instantiations: Dict[str, 'Instantiation']  # TODO: add another instantiation class level for entity/configuration/component inst.
	_hierarchy:      Dict[str, Union['ConcurrentBlockStatement', 'GenerateStatement']]  #: All elements creating a hierarchy level (blocks and generates), in declaration order.

	def __init__(self, statements: Nullable[Iterable[ConcurrentStatement]] = None) -> None:
		self._statements = []

		self._instantiations = {}
		self._hierarchy = {}

		if statements is not None:
			for statement in statements:
				self._statements.append(statement)
				statement.Parent = self

	@readonly
	def Statements(self) -> List[ConcurrentStatement]:
		"""
		Read-only property to access the statements (:attr:`_statements`).

		:returns: List of statements.
		"""
		return self._statements

	def IterateInstantiations(self) -> Generator['Instantiation', None, None]:
		for instance in self._instantiations.values():
			yield instance

		for element in self._hierarchy.values():
			yield from element.IterateInstantiations()

	# TODO: move into _init__
	def IndexStatements(self) -> None:
		for statement in self._statements:
			if isinstance(statement, (EntityInstantiation, ComponentInstantiation, ConfigurationInstantiation)):
				self._instantiations[statement.NormalizedLabel] = statement
			elif isinstance(statement, (ForGenerateStatement, IfGenerateStatement, CaseGenerateStatement)):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.IndexStatement()
			elif isinstance(statement, ConcurrentBlockStatement):
				self._hierarchy[statement.NormalizedLabel] = statement
				statement.IndexStatements()


@export
class Instantiation(ConcurrentStatement):
	"""
	A base-class for all (component) instantiations.

	.. seealso::

	   * :class:`Component instantiation <pyVHDLModel.Concurrent.ComponentInstantiation>`
	   * :class:`Configuration instantiation <pyVHDLModel.Concurrent.ConfigurationInstantiation>`
	   * :class:`Entity instantiation <pyVHDLModel.Concurrent.EntityInstantiation>`
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
		"""
		Read-only property to access the generic association items (:attr:`_genericAssociationItems`).

		:returns: List of generic association items.
		"""
		return self._genericAssociationItems

	@readonly
	def PortAssociationItems(self) -> List[AssociationItem]:
		"""
		Read-only property to access the port association items (:attr:`_portAssociationItems`).

		:returns: List of port association items.
		"""
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

	@readonly
	def Component(self) -> ComponentInstantiationSymbol:
		"""
		Read-only property to access the component (:attr:`_component`).

		:returns: The component.
		"""
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

	@readonly
	def Entity(self) -> EntityInstantiationSymbol:
		"""
		Read-only property to access the entity (:attr:`_entity`).

		:returns: The entity.
		"""
		return self._entity

	@readonly
	def Architecture(self) -> ArchitectureSymbol:
		"""
		Read-only property to access the architecture (:attr:`_architecture`).

		:returns: The architecture.
		"""
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

	@readonly
	def Configuration(self) -> ConfigurationInstantiationSymbol:
		"""
		Read-only property to access the configuration (:attr:`_configuration`).

		:returns: The configuration.
		"""
		return self._configuration


@export
class ProcessStatement(ConcurrentStatement, SequentialDeclarationRegionMixin, SequentialStatementsMixin, DocumentedEntityMixin):
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
		SequentialDeclarationRegionMixin.__init__(self, self._normalizedLabel, declaredItems)
		SequentialStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)

		if sensitivityList is None:
			self._sensitivityList = None
		else:
			self._sensitivityList = []  # TODO: convert to dict
			for signalSymbol in sensitivityList:
				self._sensitivityList.append(signalSymbol)
				# signalSymbol._parent = self  # FIXME: currently str are provided

	@ConcurrentStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ConcurrentStatement.Parent.fset(self, parent)

		# Connect the process' namespace to the enclosing declaration region's namespace, so a declaration
		# inside the process hides a same-named one from the architecture, block or generate around it.
		self._namespace.ParentNamespace = parent._namespace

	@readonly
	def SensitivityList(self) -> List[Name]:
		"""
		Read-only property to access the sensitivity list (:attr:`_sensitivityList`).

		:returns: List of sensitivity list.
		"""
		return self._sensitivityList


@export
class ConcurrentProcedureCall(ConcurrentStatement, ProcedureCallMixin):
	"""
	Represents a concurrent procedure call.

	.. admonition:: Example

	   .. code-block:: VHDL

	      proc_lbl : proc(clk, open);
	    --^^^^^^^^                      <- Label
	    --           ^^^^^^^^^^^^^^^    <- the call

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialProcedureCall>`
	"""
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
class ConcurrentBlockStatement(ConcurrentStatement, BlockStatementMixin, LabeledEntityMixin, WithPortsMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, DocumentedEntityMixin, AllowBlackboxMixin):
	"""
	Represents a block statement.

	A block groups concurrent statements and may declare its own items. It can also have a port
	clause (:data:`PortItems`), which makes it a hierarchy level of its own.

	.. admonition:: Example

	   .. code-block:: VHDL

	      blk : block
	    --^^^                            <- Label
	        port (bp : in bit);
	      --      ^^^^^^^^^^^            <- PortItems
	        signal inner : bit := '0';
	      --^^^^^^^^^^^^^^^^^^^^^^^^^^   <- DeclaredItems
	      begin
	      end block;

	.. seealso::

	   * :class:`Generate statement <pyVHDLModel.Concurrent.GenerateStatement>`
	"""
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
		WithPortsMixin.__init__(self, portItems)
		ConcurrentDeclarationRegionMixin.__init__(self, declaredItems)
		ConcurrentStatementsMixin.__init__(self, statements)
		DocumentedEntityMixin.__init__(self, documentation)
		AllowBlackboxMixin.__init__(self, allowBlackbox)

	@ConcurrentStatement.Parent.setter
	def Parent(self, parent: ModelEntity) -> None:
		ConcurrentStatement.Parent.fset(self, parent)

		self._namespace.ParentNamespace = parent._namespace


	def IndexDeclaredItems(self) -> None:
		"""A block's ports share the declarative region of its declarative part."""
		self._IndexPortItems()

		super().IndexDeclaredItems()


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

	@readonly
	def AlternativeLabel(self) -> Nullable[str]:
		"""
		Read-only property to access the alternative label (:attr:`_alternativeLabel`).

		:returns: The alternative label, or ``None`` if not set.
		"""
		return self._alternativeLabel

	@readonly
	def NormalizedAlternativeLabel(self) -> Nullable[str]:
		"""
		Read-only property to access the normalized alternative label (:attr:`_normalizedAlternativeLabel`).

		:returns: The normalized alternative label, or ``None`` if not set.
		"""
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
	Represents the base-class of all generate statements.

	A generate statement replicates or conditionally elaborates concurrent statements.

	.. seealso::

	   * :class:`Case generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	   * :class:`For generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
	   * :class:`If generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
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
	   * :class:`Case-generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
	   * :class:`For-generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
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
		if namespace._name is None:
			namespace._name = self._normalizedLabel

		for elseBranch in self._elsifBranches:
			elseBranch._namespace.ParentNamespace = parent._namespace

		if self._elseBranch is not None:
			self._elseBranch._namespace.ParentNamespace = parent._namespace

	@readonly
	def IfBranch(self) -> IfGenerateBranch:
		"""
		Read-only property to access the if branch (:attr:`_ifBranch`).

		:returns: The if branch.
		"""
		return self._ifBranch

	@readonly
	def ElsifBranches(self) -> List[ElsifGenerateBranch]:
		"""
		Read-only property to access the elsif branches (:attr:`_elsifBranches`).

		:returns: List of elsif branches.
		"""
		return self._elsifBranches

	@readonly
	def ElseBranch(self) -> Nullable[ElseGenerateBranch]:
		"""
		Read-only property to access the else branch (:attr:`_elseBranch`).

		:returns: The else branch, or ``None`` if not set.
		"""
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
	"""
	A base-class for all concurrent choices (in case...generate statements).

	.. seealso::

	   * :class:`Indexed generate choice <pyVHDLModel.Concurrent.IndexedGenerateChoice>`
	   * :class:`Ranged generate choice <pyVHDLModel.Concurrent.RangedGenerateChoice>`
	"""


@export
class IndexedGenerateChoice(ConcurrentChoice):
	"""
	Represents a case-generate choice given by a single value.

	The value is available as :data:`Expression`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 8 =>
	      --   ^      <- Expression
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

	def __str__(self) -> str:
		return str(self._expression)


@export
class RangedGenerateChoice(ConcurrentChoice):
	"""
	Represents a case-generate choice given by a range.

	The range is available as :data:`Range`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 0 to 3 =>
	      --   ^^^^^^      <- Range
	"""
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
class ConcurrentCase(BaseCase, LabeledEntityMixin, ConcurrentDeclarationRegionMixin, ConcurrentStatementsMixin, AllowBlackboxMixin, ChoicesMixin):
	"""
	Represents the base-class of all alternatives of a case-generate statement.

	.. seealso::

	   * :class:`Generate case <pyVHDLModel.Concurrent.GenerateCase>`
	   * :class:`Others generate case <pyVHDLModel.Concurrent.OthersGenerateCase>`
	"""
	_namespace: Namespace

	def __init__(
		self,
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		choices:          Nullable[Iterable[BaseChoice]] = None,
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
		ChoicesMixin.__init__(self, choices)


@export
class GenerateCase(ConcurrentCase):
	"""
	Represents one alternative of a case-generate statement, selected by its choices.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when 8 =>
	      --   ^      <- Choices
	"""
	def __init__(
		self,
		choices:          Iterable[ConcurrentChoice],
		declaredItems:    Nullable[Iterable] = None,
		statements:       Nullable[Iterable[ConcurrentStatement]] = None,
		alternativeLabel: Nullable[str] = None,
		allowBlackbox:    Nullable[bool] = None,
		parent:           Nullable[ModelEntity] = None
	) -> None:
		super().__init__(declaredItems, statements, alternativeLabel, choices, allowBlackbox, parent)

	def __str__(self) -> str:
		return "when {choices} =>".format(choices=" | ".join(str(c) for c in self._choices))


@export
class OthersGenerateCase(ConcurrentCase):
	"""
	Represents the ``others`` alternative of a case-generate statement.

	It covers every choice not named explicitly.

	.. admonition:: Example

	   .. code-block:: VHDL

	      when others =>
	      --   ^^^^^^      <- the choice
	"""
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

	.. seealso::

	   * :class:`If-generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`For-generate statement <pyVHDLModel.Concurrent.ForGenerateStatement>`
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

	@readonly
	def SelectExpression(self) -> ExpressionUnion:
		"""
		Read-only property to access the select expression (:attr:`_expression`).

		:returns: The select expression.
		"""
		return self._expression

	@readonly
	def Cases(self) -> List[GenerateCase]:
		"""
		Read-only property to access the cases (:attr:`_cases`).

		:returns: List of cases.
		"""
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

	.. seealso::

	   * :class:`If-generate statement <pyVHDLModel.Concurrent.IfGenerateStatement>`
	   * :class:`Case-generate statement <pyVHDLModel.Concurrent.CaseGenerateStatement>`
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
	Represents the base-class of all concurrent signal assignments.

	.. seealso::

	   * :class:`Concurrent conditional signal assignment <pyVHDLModel.Concurrent.ConcurrentConditionalSignalAssignment>`
	   * :class:`Concurrent selected signal assignment <pyVHDLModel.Concurrent.ConcurrentSelectedSignalAssignment>`
	   * :class:`Concurrent simple signal assignment <pyVHDLModel.Concurrent.ConcurrentSimpleSignalAssignment>`
	"""
	def __init__(self, label: str, target: SignalSymbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, parent)
		SignalAssignmentMixin.__init__(self, target)


@export
class ConcurrentSimpleSignalAssignment(ConcurrentSignalAssignment, WaveformMixin):
	"""
	Represents a simple concurrent signal assignment.

	.. admonition:: Example

	   .. code-block:: VHDL

	      q <= '1';
	    --^           <- Target
	    --     ^^^    <- the waveform

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialSimpleSignalAssignment>`
	"""
	def __init__(self, label: str, target: SignalSymbol, waveform: Iterable[WaveformElement], parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(label, target, parent)
		WaveformMixin.__init__(self, waveform)


@export
class ConcurrentSelectedSignalAssignment(ConcurrentSignalAssignment, ExpressionMixin, SelectedWaveformsMixin):
	"""
	Represents a selected concurrent signal assignment.

	The selector and alternatives are available as :data:`SelectExpression` and
	:data:`SelectedWaveforms`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      with sel select s <= '1' when 0, '0' when others;
	      --   ^^^                                            <- SelectExpression
	      --                   ^^^^^^^^^^                     <- first alternative

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialSelectedSignalAssignment>`
	   * :class:`Selected waveform <pyVHDLModel.Common.SelectedWaveform>`
	"""

	def __init__(
		self,
		label: str,
		target: SignalSymbol,
		expression: ExpressionUnion,
		selectedWaveforms: Iterable[SelectedWaveform],
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(label, target, parent)
		ExpressionMixin.__init__(self, expression)
		SelectedWaveformsMixin.__init__(self, selectedWaveforms)


@export
class ConcurrentConditionalSignalAssignment(ConcurrentSignalAssignment, ConditionalWaveformsMixin):
	"""
	Represents a conditional concurrent signal assignment.

	The branches are available as :data:`ConditionalWaveforms`.

	.. admonition:: Example

	   .. code-block:: VHDL

	      s <= '1' when cond1 else '0' when cond2 else 'Z';
	      --   ^^^^^^^^^^^^^^                                 <- first branch
	      --                                           ^^^    <- final branch

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialConditionalSignalAssignment>`
	   * :class:`Conditional waveform <pyVHDLModel.Common.ConditionalWaveform>`
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
	"""
	Represents a concurrent assertion statement.

	.. admonition:: Example

	   .. code-block:: VHDL

	      assert W > 0 report "w" severity note;
	      --     ^^^^^                             <- Condition
	      --                  ^^^                  <- Message
	      --                               ^^^^    <- Severity

	.. seealso::

	   * :class:`Sequential counterpart <pyVHDLModel.Sequential.SequentialAssertStatement>`
	"""
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
