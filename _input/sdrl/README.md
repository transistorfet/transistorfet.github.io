
SDRL
====

###### *Started January 23, 2004*

SDRL is a very strange language I made near the end of university.  It was the evolution of efforts to make a language
with an overly simplified syntax.  The previous languages were purposefuly obtuse and all language constructs were a single
character.  With SDRL, the actual parser was selectable, with the default eventually being a scheme/lisp-like syntax, but
it was designed such that almost everything was a function.  The only 'form' (in the scheme sense) is the (code ...) expression,
which returns an expression-type object (the parsed AST) for the code that appears within the brackets.  Everything else is a
function, including the (if ...) statements, which are passed the conditional blocks as expression-type values.  It then
evaluates the appropriate expression based on the result of the conditional expression.

Running
-------

There shouldn't be a need to run ./configure before compiling.  After compiling, a single binary named 'sdrl'
will be created in bin/, as well as some static libraries lib/.  There is no install option.

```
tar -xvzf sdrl.tar.gz
cd sdrl
make
bin/sdrl test.sdrl
```

Towers of Hanoi Example in SDRL
-------------------------------

```
(set move-tower (lexblock
    (setlist (@ func from to discs) ($ _))
    (if (= ($ discs) 1)
        (code
            (move-disc ($ from) ($ to)))
        (code
            (move-tower ($ from)
                        (- 6 ($ from) ($ to))
                        (- ($ discs) 1))
            (move-disc ($ from) ($ to))
            (move-tower (- 6 ($ from) ($ to))
                        ($ to)
                        (- ($ discs) 1))))))

(set move-disc (lexblock
    (setlist (@ func from to) ($ _))
    (print "Moved disc from " ($ from) " to " ($ to) "\n")))

(move-tower 1 3 3)
```

News
----

##### Version 0.3 Released!
*December 23, 2007*
It's been a long long time since the last release and most of the changes in this release were implemented shortly
after that last release but as things go, I drifted into other projects and never got around to releasing those
changes.  I picked up the project again this fall and mostly reorganized and tidied up the code a bit but again
drifted into other things.  This release is somewhat hasty since I know full well that the planned changes will not be
implemented within a reasonable time-frame and the changes from version 0.2 are actually quite extensive.  I plan on
moving to git (hopefully tomorrow) before I take up coding again.  Major features in this release include an
events/continuation stack which allows for tail recursion, slightly improved error handling, and properly organized
libraries.  The parser has been completely removed from the core and put into the base library instead, allowing for
easy selection of the parser.  The primary parser has been changed to the "lispy" parser.  I also added the beginnings
of a proper automated test suite.  Plans for the next release are primarily to polish and optimize the code where
possible.
{: .entry }

##### Version 0.2 Released!
*March 30, 2005*
Version 0.2 has been released.  Its been over a year and after some time away I have completely re-written the
interpreter.  It is completely incompatible with version 0.1 (but I assure you, much better).  I already have plans for
a next release but I am not sure how much I will implement by then.  Possible features include a dynamic parser, full
garbage collection (and therefore references), and better error handling/reporting mechanisms.
{: .entry }

##### Version 0.1 Released!
*February 09, 2004*
Version 0.1 has been released.  It is very primative but it works.  I already have some ideas for major improvements but
I am unsure when I will get around to implementing them.
{: .entry }


