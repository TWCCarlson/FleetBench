# FleetBench

Fall 2023 MSc thesis project. Documentation in `main` branch under `Thesis/Chapter Drafts/Main Body`. Mostly in the appendices. If this application receives further development proper documentation will be hosted elsewhere.

Application which simulates the progress of algorithms from the [WHCA*](https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIIDE.pdf) and [Token Passing](https://arxiv.org/abs/1705.10868) families. These are decoupled algorithms which solve for optimal agent fleet behavior in a decoupled fashion (one agent plans a full path at a time).

For now, use the auxiliary program [GraphRendering](https://github.com/TWCCarlson/GraphRendering) to create system maps. After loading the map file into FleetBench (File>New Session), make changes to the initial system state and then save the session (File>Save Session). You are able to add and remove new agents and tasks.

When ready, click the simulation configuration button in the top right, and configure the options for the simulation rules. Provide or generate a task schedule if desired.

Documentation is found in the `main` branch under `Thesis/Chapter Drafts/Main Body`. Look at the Appendix chapters.

An executable that comes with the files used to generate all the test cases in thesis is provided in the `installer` branch.

This is effectively a prototype, and would benefit greatly from more work.
