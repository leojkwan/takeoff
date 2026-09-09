<img src="docs/cover.png" width="1280" alt="Takeoff — Find the weak spots before you ship.">

# Takeoff

**Make your coding agent try to break the release.**

Takeoff gives an agent a repeatable way to review a repository: run its checks,
look for tests that pass without testing anything, and report the failures and
gaps before you ship.

It is a review prompt with small local helper scripts. You bring the coding
agent and the repository. No service, subscription, or background process.

![Takeoff's command help in a local terminal](docs/takeoff-help.png)

[Watch the terminal walkthrough](docs/takeoff-demo.mp4) · [Reproduce it](docs/capture.md)

## Try it

Requires Python 3.10 or later, Git, and a coding agent that can run local commands.

```sh
git clone https://github.com/leojkwan/takeoff.git
cd takeoff
./bin/takeoff install
export PATH="$HOME/.local/bin:$PATH"
```

Open a clean checkout of the project you want to review. For example, with Codex:

```sh
cd /path/to/your-project
codex exec --cd "$PWD" "$(takeoff prompt)"
```

Or run `takeoff prompt` and give its output to an agent already working in
that project. [Other invocation examples](AUTOMATION.md).

## What happens

The agent reads your repository's instructions and finds its actual test and
release commands. It states which checks it will run, then runs them in an
isolated checkout.

It also challenges the checks. For example, if a test still passes after a
deliberate bug is introduced, the report identifies that gap. Temporary changes
stay on a local branch and are restored after the experiment.

You get a Markdown report under `evidence/takeoff-pass/` with the commit checked,
commands run, results, defects found, and anything left untested. Release steps
follow your repository's rules and require your existing authorization.

Read the report before approving a release. An agent can miss bugs or misread
output. Takeoff's optional archive helper checks the report format and saves it;
it does not independently verify every conclusion.

The report stays with your project. Saving a second copy in Takeoff's ledger is
[optional](docs/archiving.md).

## Read or change the review

- [Review prompt](PASS.md): the instructions your agent receives.
- [Review principles](METHOD.md): what the review should establish.
- [Stack examples](profiles/): starting points for web, iOS, and Shopify projects.

Your project's current commands take precedence over these examples.

Run `takeoff --help` for helper commands or `takeoff root` to find the installed
checkout. Installation creates a symlink to this clone; keep it in place or
reinstall after moving it.

[MIT license](LICENSE)
