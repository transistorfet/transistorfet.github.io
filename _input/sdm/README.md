
Super Duper MOO
===============

###### *Started March 13, 2008*

The Super Duper MOO is a generic text-based game/world engine that
can be used to make a diverse range of games and interactive
environments.  I started it as a fun project to relax and don't have
much experience playing MUDs or MOOs myself.  It has multiple
connection protocols such as telnet and IRC to make it more
accessable to a wider audience through the reuse of existing client
software.  Data is stored in xml files for easy expansion and manual
editing if needed.  Originally written in C, it was rewritten in C++
in 2010.  A custom scripting language based on Scheme has been
integrated in order to provide logic coding for the game data itself.
The engine/language use a prototype-based object oriented system, like
the original LambdaMOO engine which provided much of the inspiration.
Despite many hours of work, no official releases were ever made.
It has largely been superseded by the IRCMOO project, written
in python.

Running
-------

There shouldn't be a need to change anything before compiling, but there are some basic settings in config.mk.
After compiling, a single binary named 'moo' will be created in bin/.

```
tar -xvzf sdm.tar.gz
cd sdm
make
bin/moo -l code/core.moo
```

Note: All paths are relative to the data directory, which defaults to data/, so the correct way to run the program
is with 'code/core.moo' and not 'data/code/core.moo'

Scripting
---------

### Basic Example of an Object

```
(define *global*.thing (root:clone))

(define thing.name "generic-thing")
(define thing.title "something")
(define thing.description "You're not sure what it is.")

(define thing:move (lambda (this where)
    (define was this.location)
    (if (and (not (null? was)) (not (was.contents:remove this)))
        (return))
    (define this.location where)
    (where.contents:push this)
))

(define thing:look_self (lambda (this)
    (user:tell (expand "<lightgreen>$this.description"))
))
```

This is just a quick example to give a feel for the scripting language.  First, the root object
is cloned and the newly created object is assigned to the global name 'thing'.  Some properties of the
new object are set, and then 2 methods are defined.  The 'move' method is called when the object is
moved from one location to another and the 'look_self' method is called when the user looks at this object.

