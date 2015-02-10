.. _conceptual_overview:

Conceptual Overview
===================

GBDB consists of 4 basic entities: Observation Sessions, Behavioral and Gestural Events and Subevents, Primates, and Gestures.


Observation Session
--------------------------
This table in GBDB represents a video that may contain one are more Behavioral and/or Gestural Events and/or Subevents. It indicates the time and location of the Session.


Behavioral and Gestural Events and Subevents
--------------------------------------------
Behavioral Events are a hierachical representation of actions that happen in the Observation Session. At the highest-level is a 'Generic' Behavioral Event which can consist of any number of Generic or 'Gestural' Subevents and thus can encapsulate a sequence of Behavioral Events. A Gestural Subevent is a subtype of a Generic Event where one individual is gesturing to another with a specific goal.

Primate
-------
The Primate table in GBDB is an entry of the individual that distinguishes location, age, species, and if the individual is wild or captive.

Gesture
-------
A Gesture is represented as a table in GBDB seperate to that of an event. That is, several events can be of the same gesture. a gesture is distinguished by signaller, recipient, body parts, goal, and whether or not the gesture is audible.


