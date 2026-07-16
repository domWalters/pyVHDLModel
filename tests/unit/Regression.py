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
"""Regression tests for previously crashing / incorrect behaviour."""
from pathlib import Path
from unittest import TestCase

from pyTooling.Warning         import WarningCollector

from pyVHDLModel                import Design, Library, Document, VHDLModelException
from pyVHDLModel.DesignUnit     import Entity, Architecture, Package
from pyVHDLModel.Exception      import NotImplementedWarning
from pyVHDLModel.Object         import Variable
from pyVHDLModel.Symbol         import EntitySymbol, PackageReferenceSymbol, SimpleSubtypeSymbol
from pyVHDLModel.Name           import SimpleName
from pyVHDLModel.Instantiation  import PackageInstantiation


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class GetAncestor(TestCase):
	def test_AncestorExists(self) -> None:
		entity = Entity("e")
		architecture = Architecture("rtl", EntitySymbol(SimpleName("e")), parent=entity)

		self.assertIs(entity, architecture.GetAncestor(Entity))

	def test_AncestorDoesNotExist_RaisesVHDLModelException(self) -> None:
		"""Previously raised an unguarded ``AttributeError`` when the root of the model was reached."""
		entity = Entity("e")

		with self.assertRaises(VHDLModelException):
			entity.GetAncestor(Package)


class AllowBlackbox(TestCase):
	def test_LocalValueIsUsed(self) -> None:
		entity = Entity("e", allowBlackbox=True)

		self.assertTrue(entity.AllowBlackbox)

	def test_InheritsFromParent(self) -> None:
		library = Library("lib", allowBlackbox=False)
		entity = Entity("e", parent=library)

		self.assertFalse(entity.AllowBlackbox)

	def test_NoLocalValueAndNoParent_RaisesVHDLModelException(self) -> None:
		"""Previously raised an unguarded ``AttributeError`` when no parent was available to inherit from."""
		entity = Entity("e")

		with self.assertRaises(VHDLModelException):
			entity.AllowBlackbox


class TopLevel(TestCase):
	def test_SingleEntityWithoutArchitecture_IsNotMistakenForUncomputedHierarchy(self) -> None:
		"""
		A design consisting of a single entity without any (yet analyzed) architecture produces a hierarchy graph with
		exactly one vertex and zero edges. This must not be mistaken for "hierarchy not yet computed".
		"""
		design = Design()
		library = Library("lib")
		design.AddLibrary(library)

		document = Document(Path("top.vhdl"), parent=None)
		document._AddEntity(Entity("top"))
		design.AddDocument(document, library)

		design.CreateDependencyGraph()
		design.CreateHierarchyGraph()

		self.assertEqual(0, design.HierarchyGraph.EdgeCount)
		self.assertEqual(1, design.HierarchyGraph.VertexCount)
		self.assertIs(design.GetLibrary("lib")._entities["top"], design.TopLevel)

	def test_HierarchyNotYetComputed_RaisesVHDLModelException(self) -> None:
		design = Design()

		with self.assertRaises(VHDLModelException):
			design.TopLevel


class PackageInstantiationContextItems(TestCase):
	def test_ContextItemsAreForwarded(self) -> None:
		packageReference = PackageReferenceSymbol(SimpleName("GenericPackage"))
		instantiation = PackageInstantiation("Inst", packageReference, contextItems=[])

		self.assertEqual([], instantiation.ContextItems)


class IndexDeclaredItemsVariableWarning(TestCase):
	"""
	Regression tests for replacing a stray ``print()`` with ``WarningCollector.Raise(NotImplementedWarning(...))`` in
	``IndexDeclaredItems``, consistent with every other "not yet implemented" warning in this codebase (see
	``pyVHDLModel/__init__.py``) and with pyGHDL.dom's ``WarningCollector``-based idiom (both build on
	``pyTooling.Warning``).
	"""

	@staticmethod
	def _designWithVariableInArchitecture() -> Library:
		design = Design()
		library = Library("lib")
		design.AddLibrary(library)

		document = Document(Path("regression.vhdl"), parent=None)
		entitySymbol = EntitySymbol(SimpleName("e"))
		subtype = SimpleSubtypeSymbol(SimpleName("natural"))
		variable = Variable(["v"], subtype)
		architecture = Architecture("rtl", entitySymbol, declaredItems=[variable], parent=None)
		document._AddArchitecture(architecture)
		design.AddDocument(document, library)

		return library

	def test_WarningIsCollected_WhenCollectorIsInScope(self) -> None:
		library = self._designWithVariableInArchitecture()

		with WarningCollector() as collector:
			library.IndexArchitectures()

		self.assertEqual(1, len(collector))
		self.assertIsInstance(collector[0], NotImplementedWarning)

	def test_DoesNotCrash_WhenNoCollectorIsInScope(self) -> None:
		"""Previously raised ``TypeError: category must be a Warning subclass, not 'type'`` due to a broken
		``warnings.warn(...)`` call; must not raise at all here, since ``NotImplementedWarning`` is a *non-critical*
		``pyTooling.Warning.Warning`` and is silently dropped when unhandled - exactly like every other
		``NotImplementedWarning`` call site in this codebase."""
		library = self._designWithVariableInArchitecture()

		library.IndexArchitectures()
