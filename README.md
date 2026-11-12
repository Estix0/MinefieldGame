# Minefield Cog

A simple game cog for RedBot.

## What it does

This cog creates a "minefield" in a designated channel. Every time a user (who is not a bot) sends a message in that channel, they have a set chance (default 1-in-100) to "explode."

* **If they don't explode:** Their "current score" increases by 1.
* **If they explode:** They receive a 10-minute timeout, their "current score" resets to 0, and their "times exploded" count increases. Their "current score" is compared to their "high score" and saved if it's a new record.

The cog tracks scores, high scores, and explosion counts for all members.

## Commands

* `[p]minefield setchannel <channel>`
    Sets the channel where the minefield game will be active. (Admin only)

* `[p]minefield setchance <number>`
    Sets the chance of exploding. For example, `100` means a 1-in-100 chance. (Admin only)

* `[p]minefield stats [member]`
    Displays the minefield stats (Current Score, High Score, Explosions) for you or the specified member.

* `[p]minefield leaderboard` (or `[p]mf lb`)
    Shows the server leaderboards for the Top 5 High Scores and the Top 5 Most Explosions.
