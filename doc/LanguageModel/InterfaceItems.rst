.. _vhdlmodel-inter:

Interface Items
###################

Interface items are used in generic, port and parameter declarations.

.. contents:: Table of Content
   :local:

.. rubric:: Class Hierarchy

.. inheritance-diagram:: pyVHDLModel.SyntaxModel.GenericConstantInterfaceItem pyVHDLModel.SyntaxModel.GenericTypeInterfaceItem pyVHDLModel.SyntaxModel.GenericProcedureInterfaceItem pyVHDLModel.SyntaxModel.GenericFunctionInterfaceItem pyVHDLModel.SyntaxModel.PortSimpleSignalInterfaceItem pyVHDLModel.SyntaxModel.PortViewSignalInterfaceItem pyVHDLModel.SyntaxModel.ParameterConstantInterfaceItem pyVHDLModel.SyntaxModel.ParameterVariableInterfaceItem pyVHDLModel.SyntaxModel.ParameterSimpleSignalInterfaceItem pyVHDLModel.SyntaxModel.ParameterViewSignalInterfaceItem pyVHDLModel.SyntaxModel.ParameterFileInterfaceItem
   :parts: 1


.. _vhdlmodel-generics:

Generic Interface Items
=======================

.. _vhdlmodel-genericconstant:

GenericConstantInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.GenericConstantInterfaceItem`:

.. code-block:: Python

   @export
   class GenericConstantInterfaceItem(Constant, GenericInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-generictype:

GenericTypeInterfaceItem
------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.GenericTypeInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericTypeInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-genericprocedure:

GenericProcedureInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.GenericProcedureInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericProcedureInterfaceItem(GenericSubprogramInterfaceItem):



.. _vhdlmodel-genericfunction:

GenericFunctionInterfaceItem
----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.GenericFunctionInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericFunctionInterfaceItem(GenericSubprogramInterfaceItem):



.. _vhdlmodel-genericpackage:

GenericPackageInterfaceItem
---------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.GenericPackageInterfaceItem`:

.. code-block:: Python

   @Export
   class GenericPackageInterfaceItem(GenericInterfaceItem):


.. _vhdlmodel-ports:

Port Interface Item
===================

.. _vhdlmodel-portsignal:

PortSignalInterfaceItem
-----------------------

``PortSignalInterfaceItem`` is now an abstract base-class for :class:`PortSimpleSignalInterfaceItem`
(``port (p : in bit);``) and :class:`PortViewSignalInterfaceItem` (``port (p : view MyView);``,
VHDL-2019 mode views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-portsimplesignal:

PortSimpleSignalInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.PortSimpleSignalInterfaceItem`:

.. code-block:: Python

   @export
   class PortSimpleSignalInterfaceItem(PortSignalInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-portviewsignal:

PortViewSignalInterfaceItem
-----------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.PortViewSignalInterfaceItem`:

.. code-block:: Python

   @export
   class PortViewSignalInterfaceItem(PortSignalInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object; aliased as ModeViewIndication (a mode view reference occupies the
     # same structural position as an ordinary subtype indication)
     @property
     def Subtype(self) -> Symbol:

     @property
     def ModeViewIndication(self) -> ModeViewSymbol:



.. _vhdlmodel-parameters:

Parameter Interface Item
=========================

.. _vhdlmodel-parameterconstant:

ParameterConstantInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ParameterConstantInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterConstantInterfaceItem(Constant, ParameterInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parametervariable:

ParameterVariableInterfaceItem
------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ParameterVariableInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterVariableInterfaceItem(Variable, ParameterInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItem
     @property
     def Mode(self) -> Mode:



.. _vhdlmodel-parametersignal:

ParameterSignalInterfaceItem
----------------------------

``ParameterSignalInterfaceItem`` is now an abstract base-class for
:class:`ParameterSimpleSignalInterfaceItem` (``procedure p(signal s : in bit);``) and
:class:`ParameterViewSignalInterfaceItem` (``procedure p(signal s : view MyView);``, VHDL-2019 mode
views) - see below. It is not meant to be instantiated directly.

.. _vhdlmodel-parametersimplesignal:

ParameterSimpleSignalInterfaceItem
-----------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ParameterSimpleSignalInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterSimpleSignalInterfaceItem(ParameterSignalInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object
     @property
     def Subtype(self) -> Subtype:

     # inherited from WithDefaultExpressionMixin
     @property
     def DefaultExpression(self) -> BaseExpression:

     # inherited from InterfaceItemWithModeMixin
     @property
     def Mode(self) -> Mode:


.. _vhdlmodel-parameterviewsignal:

ParameterViewSignalInterfaceItem
-----------------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ParameterViewSignalInterfaceItem`:

.. code-block:: Python

   @export
   class ParameterViewSignalInterfaceItem(ParameterSignalInterfaceItem):
     # inherited from ModelEntity
     @property
     def Parent(self) -> ModelEntity:

     # inherited from NamedEntity
     @property
     def Name(self) -> str:

     # inherited from Object; aliased as ModeViewIndication (a mode view reference occupies the
     # same structural position as an ordinary subtype indication)
     @property
     def Subtype(self) -> Symbol:

     @property
     def ModeViewIndication(self) -> ModeViewSymbol:



.. _vhdlmodel-parameterfile:

ParameterFileInterfaceItem
--------------------------

.. todo::

   Write documentation.

**Condensed definition of class** :class:`~pyVHDLModel.SyntaxModel.ParameterFileInterfaceItem`:

.. code-block:: Python

   @Export
   class ParameterFileInterfaceItem(ParameterInterfaceItem):
