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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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

Configurations: entity aspects, binding indications, component configurations (and the structurally
identical configuration specifications), and block configurations.
"""
from typing import List, Iterable, Union, Optional as Nullable

from pyTooling.Decorators    import export, readonly
from pyTooling.MetaClasses   import ExtendedType

from pyVHDLModel.Base        import ModelEntity
from pyVHDLModel.Name        import Name
from pyVHDLModel.Symbol      import Symbol, EntitySymbol, ArchitectureSymbol, ConfigurationSymbol
from pyVHDLModel.Symbol      import ComponentInstantiationSymbol
from pyVHDLModel.Association import GenericAssociationItem, PortAssociationItem


@export
class EntityAspect(ModelEntity):
	"""
	Base-class for the three forms an entity aspect can take in a binding indication: an entity
	(optionally with an architecture), a configuration, or ``open``.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav);
	      --                ^^^^^^^^^^^^^^^^^^^^^^
	"""


@export
class EntityAspectEntity(EntityAspect):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav);
	      --                       ^^^^^^^^  ^^^^^
	      --                       Entity    Architecture (optional)
	"""

	_entity:       EntitySymbol
	_architecture: Nullable[ArchitectureSymbol]

	def __init__(
		self,
		entity: EntitySymbol,
		architecture: Nullable[ArchitectureSymbol] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		self._entity = entity
		entity.Parent = self

		self._architecture = architecture
		if architecture is not None:
			architecture.Parent = self

	@readonly
	def Entity(self) -> EntitySymbol:
		return self._entity

	@readonly
	def Architecture(self) -> Nullable[ArchitectureSymbol]:
		return self._architecture


@export
class EntityAspectConfiguration(EntityAspect):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use configuration work.cfg;
	      --                              ^^^^^^^
	"""

	_configuration: ConfigurationSymbol

	def __init__(self, configuration: ConfigurationSymbol, parent: Nullable[ModelEntity] = None) -> None:
		super().__init__(parent)

		self._configuration = configuration
		configuration.Parent = self

	@readonly
	def Configuration(self) -> ConfigurationSymbol:
		return self._configuration


@export
class EntityAspectOpen(EntityAspect):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use open;
	"""


@export
class BindingIndication(ModelEntity):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav) generic map (...) port map (...);
	      --                ^^^^^^^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^ ^^^^^^^^^^^^^^
	"""

	_entityAspect:            Nullable[EntityAspect]
	_genericAssociationItems: List[GenericAssociationItem]
	_portAssociationItems:    List[PortAssociationItem]

	def __init__(
		self,
		entityAspect: Nullable[EntityAspect] = None,
		genericAssociationItems: Nullable[Iterable[GenericAssociationItem]] = None,
		portAssociationItems: Nullable[Iterable[PortAssociationItem]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		self._entityAspect = entityAspect
		if entityAspect is not None:
			entityAspect.Parent = self

		self._genericAssociationItems = []
		if genericAssociationItems is not None:
			for association in genericAssociationItems:
				self._genericAssociationItems.append(association)
				association.Parent = self

		self._portAssociationItems = []
		if portAssociationItems is not None:
			for association in portAssociationItems:
				self._portAssociationItems.append(association)
				association.Parent = self

	@readonly
	def EntityAspect(self) -> Nullable[EntityAspect]:
		return self._entityAspect

	@readonly
	def GenericAssociationItems(self) -> List[GenericAssociationItem]:
		return self._genericAssociationItems

	@readonly
	def PortAssociationItems(self) -> List[PortAssociationItem]:
		return self._portAssociationItems


@export
class AllInstantiationList(ModelEntity):
	"""
	Represents the reserved word ``all`` used as an instantiation list.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for all : comp use entity work.sub(behav);
	      --    ^^^
	"""


@export
class OthersInstantiationList(ModelEntity):
	"""
	Represents the reserved word ``others`` used as an instantiation list.

	.. admonition:: Example

	   .. code-block:: VHDL

	      for others : comp use entity work.sub(behav);
	      --    ^^^^^^
	"""


InstantiationListUnion = Union[List[Name], AllInstantiationList, OthersInstantiationList]


@export
class ComponentConfiguration(ModelEntity):
	"""
	Represents a component configuration (inside a block configuration), or - structurally identical
	- a configuration specification (declared directly in an architecture's declarative part).

	.. admonition:: Example

	   .. code-block:: VHDL

	      for U1 : comp use entity work.sub(behav);
	      --  ^^   ^^^^
	      --  |    Component name
	      --  Instantiation list
	"""

	_instantiationList:  InstantiationListUnion
	_componentName:      ComponentInstantiationSymbol
	_bindingIndication:   Nullable[BindingIndication]

	def __init__(
		self,
		instantiationList: InstantiationListUnion,
		componentName: ComponentInstantiationSymbol,
		bindingIndication: Nullable[BindingIndication] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		if isinstance(instantiationList, (AllInstantiationList, OthersInstantiationList)):
			self._instantiationList = instantiationList
			instantiationList.Parent = self
		else:
			self._instantiationList = [label for label in instantiationList]
			for label in self._instantiationList:
				label.Parent = self

		self._componentName = componentName
		componentName.Parent = self

		self._bindingIndication = bindingIndication
		if bindingIndication is not None:
			bindingIndication.Parent = self

	@readonly
	def InstantiationList(self) -> InstantiationListUnion:
		return self._instantiationList

	@readonly
	def ComponentName(self) -> ComponentInstantiationSymbol:
		return self._componentName

	@readonly
	def BindingIndication(self) -> Nullable[BindingIndication]:
		return self._bindingIndication


@export
class BlockConfiguration(ModelEntity):
	"""
	.. admonition:: Example

	   .. code-block:: VHDL

	      for rtl
	      --  ^^^ Block specification
	        for U1 : comp
	        -- ...
	        end for;
	      end for;
	"""

	_blockSpecification: Symbol
	_items:               List[Union["BlockConfiguration", ComponentConfiguration]]

	def __init__(
		self,
		blockSpecification: Symbol,
		items: Nullable[Iterable[Union["BlockConfiguration", ComponentConfiguration]]] = None,
		parent: Nullable[ModelEntity] = None
	) -> None:
		super().__init__(parent)

		self._blockSpecification = blockSpecification
		blockSpecification.Parent = self

		self._items = []
		if items is not None:
			for item in items:
				self._items.append(item)
				item.Parent = self

	@readonly
	def BlockSpecification(self) -> Symbol:
		return self._blockSpecification

	@readonly
	def Items(self) -> List[Union["BlockConfiguration", ComponentConfiguration]]:
		return self._items
