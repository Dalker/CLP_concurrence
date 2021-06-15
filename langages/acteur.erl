-module(acteur).
-export([start/0, machin/0]).

machin() ->
    receive
        hello ->
            io:format("Machin dit bonjour.~n", [])
    end.

start() ->
    Machin_PID = spawn(acteur, machin, []),
    Machin_PID ! hello.
