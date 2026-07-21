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

Common definitions and Mixins are used by many classes in the model as base-classes.
"""
from typing                  import List, Iterable, Union, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity, LabeledEntityMixin
from pyVHDLModel.Expression  import BaseExpression, QualifiedExpression, FunctionCall, TypeConversion, Literal
from pyVHDLModel.Symbol      import Symbol
from pyVHDLModel.Association import ParameterAssociationItem


ExpressionUnion = Union[
	BaseExpression,
	QualifiedExpression,
	FunctionCall,
	TypeConversion,
	# ConstantOrSymbol,     TODO: ObjectSymbol
	Literal,
]


@export
class AllowBlackboxMixin(metaclass=ExtendedType, mixin=True):
	_allowBlackbox: Nullable[bool]  #: Allow blackboxes for components in language entity.

	def __init__(self, allowBlackbox: Nullable[bool] = None) -> None:
		self._allowBlackbox = allowBlackbox

	@property
	def AllowBlackbox(self) -> bool:
		"""
		Read-only property to check if a design supports blackboxes (:attr:`_allowBlackbox`).

		.. rubric:: Algorithm

		1. If allow blackbox property is locally set, return the local value,
		2. Otherwise, return allow blackbox value from parent object.

		:returns:                   If blackboxes are allowed.
		:raises VHDLModelException: If neither a local value is set nor a parent object is available to inherit the
		                            value from.
		"""
		if self._allowBlackbox is not None:
			return self._allowBlackbox
		elif self._parent is None:
			from pyVHDLModel.Exception import VHDLModelException

			raise VHDLModelException(f"AllowBlackbox is not set on {self!r} and no parent is available to inherit it from.")
		else:
			return self._parent.AllowBlackbox

	@AllowBlackbox.setter
	def AllowBlackbox(self, value: Nullable[bool]) -> None:
		self._allowBlackbox = value


@export
class Statement(ModelEntity, LabeledEntityMixin):
	"""
	A ``Statement`` is a base-class for all statements.
	"""
	def __init__(self, label: Nullable[str] = None, parent=None) -> None:
		super().__init__(parent)
		LabeledEntityMixin.__init__(self, label)


@export
class ProcedureCallMixin(metaclass=ExtendedType, mixin=True):
	_procedure:                 Symbol  # TODO: implement a ProcedureSymbol
	_parameterAssociationItems: List[ParameterAssociationItem]

	def __init__(self, procedureName: Symbol, parameterAssociationItems: Nullable[Iterable[ParameterAssociationItem]] = None) -> None:
		self._procedure = procedureName
		procedureName.Parent = self

		# TODO: extract to mixin
		self._parameterAssociationItems = []
		if parameterAssociationItems is not None:
			for parameterMapping in parameterAssociationItems:
				self._parameterAssociationItems.append(parameterMapping)
				parameterMapping.Parent = self

	@readonly
	def Procedure(self) -> Symbol:
		return self._procedure

	@property
	def ParameterAssociationItems(self) -> List[ParameterAssociationItem]:
		return self._parameterAssociationItems


@export
class AssignmentMixin(metaclass=ExtendedType, mixin=True):
	"""A mixin-class for all assignment statements."""

	_target: Symbol

	def __init__(self, target: Symbol) -> None:
		self._target = target
		target.Parent = self

	@property
	def Target(self) -> Symbol:
		return self._target


@export
class SignalAssignmentMixin(AssignmentMixin, mixin=True):
	"""A mixin-class for all signal assignment statements."""


@export
class VariableAssignmentMixin(AssignmentMixin, mixin=True):
	"""A mixin-class for all variable assignment statements."""

	# FIXME: move to sequential?
	_expression: ExpressionUnion

	def __init__(self, target: Symbol, expression: ExpressionUnion) -> None:
		super().__init__(target)

		self._expression = expression
		expression.Parent = self

	@property
	def Expression(self) -> ExpressionUnion:
		return self._expression
