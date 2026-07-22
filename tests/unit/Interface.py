# ==================================================================================================================== #
#             __     ___   _ ____  _     __  __           _      _                                                     #
#   _ __  _   \ \   / / | | |  _ \| |      __| | ___  _ __ ___                                                        #
#  | '_ \| | | \ \ / /| |_| | | | | |     / _` |/ _ \| '_ ` _ \                                                       #
#  | |_) | |_| |\ V / |  _  | |_| | |___ | (_| | (_) | | | | | |                                                       #
#  | .__/ \__, | \_/  |_| |_|____/|_____(_)__,_|\___/|_| |_| |_|                                                       #
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
"""Tests for mode views (VHDL-2019) and the Port/Parameter signal interface item split."""
from unittest import TestCase

from pyVHDLModel.Base       import Mode
from pyVHDLModel.Name       import SimpleName
from pyVHDLModel.Symbol     import SimpleSubtypeSymbol, ModeViewSymbol
from pyVHDLModel.Interface  import ModeViewDeclaration, SimpleModeViewElement, CompositeModeViewElement
from pyVHDLModel.Interface  import PortSignalInterfaceItem, PortSimpleSignalInterfaceItem, PortViewSignalInterfaceItem
from pyVHDLModel.Interface  import ParameterSignalInterfaceItem, ParameterSimpleSignalInterfaceItem, ParameterViewSignalInterfaceItem


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ModeViewSymbols(TestCase):
	def test_Unresolved(self) -> None:
		name = SimpleName("MyView")
		symbol = ModeViewSymbol(name)

		self.assertIs(name, symbol.Name)
		self.assertFalse(symbol.IsResolved)
		self.assertIsNone(symbol.Reference)
		self.assertIsNone(symbol.ModeView)

	def test_Resolved(self) -> None:
		symbol = ModeViewSymbol(SimpleName("MyView"))
		subtype = SimpleSubtypeSymbol(SimpleName("RecordType"))
		modeView = ModeViewDeclaration("MyView", subtype)

		symbol.ModeView = modeView

		self.assertTrue(symbol.IsResolved)
		self.assertIs(modeView, symbol.ModeView)
		self.assertIs(modeView, symbol.Reference)


class ModeViewDeclarations(TestCase):
	def test_SimpleElements(self) -> None:
		subtype = SimpleSubtypeSymbol(SimpleName("RecordType"))
		elements = [
			SimpleModeViewElement(["a"], Mode.Out),
			SimpleModeViewElement(["b"], Mode.In),
		]
		modeView = ModeViewDeclaration("MyView", subtype, elements)

		self.assertEqual("MyView", modeView.Identifier)
		self.assertIs(subtype, modeView.Subtype)
		self.assertEqual(2, len(modeView.Elements))

		a, b = modeView.Elements
		self.assertIsInstance(a, SimpleModeViewElement)
		self.assertEqual(("a",), a.Identifiers)
		self.assertEqual(Mode.Out, a.Mode)
		self.assertIsInstance(b, SimpleModeViewElement)
		self.assertEqual(("b",), b.Identifiers)
		self.assertEqual(Mode.In, b.Mode)

	def test_MultipleIdentifiersSharingOneMode(self) -> None:
		"""``a, b : out;`` - one element definition, multiple target field names."""
		element = SimpleModeViewElement(["a", "b"], Mode.Out)

		self.assertEqual(("a", "b"), element.Identifiers)
		self.assertEqual(Mode.Out, element.Mode)

	def test_CompositeElement(self) -> None:
		"""``b : view InnerView;`` - a nested/hierarchical mode view reference."""
		subtype = SimpleSubtypeSymbol(SimpleName("OuterRecord"))
		innerViewSymbol = ModeViewSymbol(SimpleName("InnerView"))
		elements = [
			SimpleModeViewElement(["a"], Mode.Out),
			CompositeModeViewElement(["b"], innerViewSymbol),
		]
		modeView = ModeViewDeclaration("OuterView", subtype, elements)

		b = modeView.Elements[1]
		self.assertIsInstance(b, CompositeModeViewElement)
		self.assertEqual(("b",), b.Identifiers)
		self.assertIs(innerViewSymbol, b.ModeViewName)


class PortSignalInterfaceItems(TestCase):
	def test_SimpleMode(self) -> None:
		port = PortSimpleSignalInterfaceItem(["p"], Mode.In, SimpleSubtypeSymbol(SimpleName("bit")))

		self.assertIsInstance(port, PortSignalInterfaceItem)
		self.assertEqual(Mode.In, port.Mode)
		self.assertIsNotNone(port.Subtype)

	def test_ModeView(self) -> None:
		modeViewIndication = ModeViewSymbol(SimpleName("MyView"))
		port = PortViewSignalInterfaceItem(["p"], modeViewIndication)

		self.assertIsInstance(port, PortSignalInterfaceItem)
		self.assertIs(modeViewIndication, port.ModeViewIndication)
		self.assertIs(modeViewIndication, port.Subtype)


class ParameterSignalInterfaceItems(TestCase):
	def test_SimpleMode(self) -> None:
		parameter = ParameterSimpleSignalInterfaceItem(["s"], Mode.In, SimpleSubtypeSymbol(SimpleName("bit")))

		self.assertIsInstance(parameter, ParameterSignalInterfaceItem)
		self.assertEqual(Mode.In, parameter.Mode)

	def test_ModeView(self) -> None:
		modeViewIndication = ModeViewSymbol(SimpleName("MyView"))
		parameter = ParameterViewSignalInterfaceItem(["s"], modeViewIndication)

		self.assertIsInstance(parameter, ParameterSignalInterfaceItem)
		self.assertIs(modeViewIndication, parameter.ModeViewIndication)
		self.assertIs(modeViewIndication, parameter.Subtype)
