<h1 align="center">Onionr FAQ</h1>

(Most of the FAQ answers apply to planned features and do not reflect in the demo network)

* How does Onionr route messages?

Onionr creates a message with an anti-spam proof (usually). It is then forwarded between nodes using binomial tree broadcast.

The network is structured based on the particular transport being used, for Tor, .onion addresses are used to determine closeness between nodes.

Churn due to connectivity changes or issues, membership changes or malicious activity means nodes need to sometimes look far away for missed messages.

To help with scale, messages can be intelligently deleted or forwarded, for example a mail message can be marked by its recipient at a given point for deletion, or forum posts can be set to expire after a short period or after lack of activity.


* Why do you use Python instead of [language]?

I'm very comfortable in Python, and I believe it is a maintainable language if you use it correctly with modern features, also it has many quality libraries useful to the project, like pyncal and stem. Most places in the project are IO bound.


* What do you think of bad actors who might use Onionr?

Users should be able to exclude viewing, processing, and hosting content they do not want to. To this end, I want to enable user-configurable filtering based on lists provided by friends, fuzzy hashing, and voting.

