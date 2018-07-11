=======================
Developer Documentation
=======================

ZigZag is a hybrid of two different design patterns

- `Facade Pattern`_
    This pattern lets us present a common language of interface to unrelated parts of ZigZag.  We generally wrap different API calls and the logic around handling their success or failure inside a given Facade.
- `Mediator Pattern`_
    This pattern provides us with a location to store data in a given run that is used across API calls.  The intention is to only lookup data as it is needed and to store it for future use.  If a class wants to know something that isn't its responsibility it asks the mediator. The `ZigZag`_ class is the mediator.


Categorization of classes used in ZigZag
----------------------------------------

- Facades
    Most of these are obvious since they all have 'facade' in their name. They should all take a mediator as an argument.  Most of the time there should only be one instance of the object created by this class, they are intended to be reusable.
- Mediator
    There is only one mediator and that's an instance of `ZigZag`_. When `ZigZag`_ sets up the facades it needs it passes in itself as the mediator.
- Other (special cases)
    Not everything is a Facade or a Mediator. Some classes are used to store data during the run.  The `ZigZagTestLog`_ class is a good example of this.  As we parse incoming data from an xml source we create an instance of `ZigZagTestLog`_ to store the data.
    The other notable exception is cli.py which contains our main function.  This provides a CLI interface using click.

APIs used by ZigZag
-------------------

Generally Zigzag uses APIs provided by the `swagger_client`_ but there have been scenarios where bugs have prevented us from doing this.  In these cases we are using the `qTest Manager API`_ endpoints without going through the swagger client.  The library we use to do this is requests.

--------------------------
Gotchas and Best Practices
--------------------------

Useful information!

Initialization of a new Facade
------------------------------
The signature of an __init__ method should always have the mediator in the last position.
init function example::

    def __init__(self, xml, mediator):

Use of class methods
-------------------
There are a few places where we make use of class methods to lazily load and store contextual data for future use.  The best example of this is the method _get_fields inside `ZigZagTestLog`_.  The data is stored on the class but accessed through a property by the name of fields.

Returning vs Writing data to the Mediator
-----------------------------------------
Many of the Facades get data from an API that can be reused later, rather than returning this data we expect methods on a Facade to write reusable data to its mediator.
when a `ZigZagTestLog`_ finishes with its init it attaches itself to the mediator::

    self._mediator.test_logs.append(self)


If you are writing a private method that is used to decompose you logic returning is fine.  However many methods may write multiple bits of data to the mediator rather than return.

.. _qTest Manager API: https://support.qasymphony.com/hc/en-us/articles/115002958146-qTest-API-Specification
.. _ZigZagTestLog: ../zigzag/zigzag_test_log.py
.. _ZigZag: ../zigzag/zigzag.py
.. _swagger_client: https://github.com/rcbops/qtest-swagger-client
.. _Facade Pattern: https://sourcemaking.com/design_patterns/facade
.. _Mediator Pattern: https://sourcemaking.com/design_patterns/mediator