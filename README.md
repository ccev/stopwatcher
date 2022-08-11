## Stop Watcher 3 is under construction.


What's different about it?

Mainly I'm just doing a little refresh and implement some things I've learned since 
working on v2.

The main change will be the way it will get its input. Instead of reading from a 
scanner database, it can accept raw protos and custom webhooks directly, allowing 
for more reliable detection. I will also try to design the code a lot more variable, 
making it a lot easier to add more fort types, input methods and processors.