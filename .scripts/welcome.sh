[[ -z $TTY ]] || echo '
Welcome to pos-sim-core docker environment.

If you see this message you have just started a new session.

Run

$ python -m sim.executor.config-doctor

to see if this instance is correctly configured and
ready to join the distributed system.

Use

$ run-worker

to have this machine run a worker node.

Use

$ launch-flower

to start monitoring the system from this machine.

Use the "dctl" program to fetch result files

(See project readme for complete instructions)

'
