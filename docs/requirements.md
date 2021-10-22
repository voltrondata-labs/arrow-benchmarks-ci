# Buildkite Pipelines
- make sure deploy pipeline is filtered by main branch
- make sure benchmark pipelines specify agent queues


# Automation
- Create new pipeline if it does not exist when a new machine is added

# Authentication
- Add authentication for API requests
- Is it OK for me to assume that when Arrow contributor wants to add their own benchmark machine to our current list of benchmark machines, we can share BK agent token (for  https://buildkite.com/apache-arrow with them so BK agent on their machine can authenticate with https://buildkite.com/apache-arrow ?

# Adding new machines
- ability to add slack channels
- ability to add machines