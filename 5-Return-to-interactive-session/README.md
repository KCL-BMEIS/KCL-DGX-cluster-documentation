# Return to Interactive Session
This tutorial explains a neat trick for returning to interactive sessions. This is useful for:

- Performance optimization
- Debugging
- Keeping logs

Let's assume you run an [interactive session](https://docs.run.ai/v2.19/Researcher/cli-reference/runai-submit/):

```shell
runai submit --name return-to-interactive -i ubuntu -g 0 --interactive -- sleep infinity
```

You now connect a bash to the interactive session:

```shell
runai bash return-to-interactive
```

This offers a convenient way to test your code / optimize for performance / trace bugs without losing acces to the logs. However, what if you now wish to leave your computer and keep tasks running? [tmux](https://github.com/tmux/tmux/wiki) to the rescue!

Inside the shell, install `tmux`:

```shell
sudo apt install tmux
```

Instead of running your script directly, do:

```shell
tmux
```

Now, run your script that you wish to leave unattended:

```shell
python my_training_script_that_takes_forever_to_run_but_i_want_to_go_home_and_check_stuff_out_later.py
```

Next, disconnect from `tmux` through `Ctrl+b; d`. Disconnect the `runai bash` via `Ctrl+d`. Go home, cook yourself some nice food. Now, to return to the session, simply do:

```shell
runai bash return-to-interactive
```

Then, connect to the `tmux` terminal:

```shell
tmux attach -t 0
```

Everything still there! Hope you find this helpful. Note, you can also run multiple terminals inside the same interactive session.
