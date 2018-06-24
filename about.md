---
title: About
layout: page
---

## Why - Motivation
Most data scientists and researchers I follow live in timezones that are quite far from mine. That makes it very easy for me to miss valuable tweets. It is also hard to read past a hundred tweets in the timeline. And finally I want to keep easily accessible lists of interesting tweets. This projects aims to solve these problem.

@Smerity did a better job explaining the problem in his tweets:

<amp-twitter width="400" height="250"
             layout="responsive"
             data-tweetid="1007758301788925953">
    <blockquote placeholder><p lang="en" dir="ltr">I hate to say but <a href="https://twitter.com/Twitter?ref_src=twsrc%5Etfw">@Twitter</a> sucks for knowledge. Amidst the flame wars and trolls, there is genuinely valuable discussions had here - but how the hell do you find it. You can&#39;t order tweets by popularity. Search barely works. I have a hard enough time finding my own tweets.</p>&mdash; Smerity (@Smerity) <a href="https://twitter.com/Smerity/status/1007758301788925953?ref_src=twsrc%5Etfw">June 15, 2018</a></blockquote>
</amp-twitter>

<amp-twitter width="400" height="250"
             layout="responsive"
             data-tweetid="1007758302598402048"
             data-conversation="none">
    <blockquote placeholder><p lang="en" dir="ltr">Hilariously the reason this is likely an issue is that using <a href="https://twitter.com/Twitter?ref_src=twsrc%5Etfw">@Twitter</a> for knowledge is not the standard use case. Most tweets are intended to be transient. Most tweets are never worth more than a cursory look. Yet there are stunning evergreen threads that are lost forever.</p>&mdash; Smerity (@Smerity) <a href="https://twitter.com/Smerity/status/1007758302598402048?ref_src=twsrc%5Etfw">June 15, 2018</a></blockquote>
</amp-twitter>

## How - Methodology
The gist of the process:

1. Collect tweets on my timeline periodically and automatically.
2. Cluster collected tweets according to their topics and sort them by popularity.
3. Read relevant tweets and picked the ones I find interesting enough.
4. Convert picked tweets and combine them into a web page.

The tweets are split by day. A day starts at 08:00 UTC, which was selected based on the pattern of activities on my timeline:

<amp-img
  src= "/public/images/20180521-timeline.png"
  width="750" height="250" layout="responsive" alt="Timeilne Activity Distribution">
</amp-img>


The time used to put a tweets in a day is the time it appeared on my timeline, not the creation time of the tweet (only retweets are affected).

## Contributions Welcome!
Here are some ways to contribute:

1. Recommend people to follow.
2. Improve the posts. (Everything is open-sourced.)
3. Suggest additional tweets to a day (through Github pull requests or issues).
4. Any general suggestions to the project (through Github issues.)
